"""
SLA Data Access Layer

Handles all data operations for SLA management including API integration,
caching, and data transformation.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import redis.asyncio as redis

from .interfaces import ISLADataAccess
from .models import SLAPolicy, TicketSLAStatus, TechnicianSLAMetrics, DateRange, SLAPriority
from .exceptions import SLADataAccessError, SLAPolicyNotFoundError
from ...clients.sla_superops_client import SLASuperOpsClient
from ...utils.logger import get_logger


class SLADataAccess(ISLADataAccess):
    """
    SLA Data Access implementation with caching and API integration
    
    Features:
    - SuperOps API integration
    - Redis caching for performance
    - Data transformation and validation
    - Error handling and retry logic
    """
    
    def __init__(self, config, superops_client: SLASuperOpsClient = None):
        self.config = config
        self.logger = get_logger(self.__class__.__name__)
        
        # SuperOps client
        self.superops_client = superops_client or SLASuperOpsClient(config)
        
        # Redis cache
        self.redis_client = None
        self.cache_enabled = getattr(config, 'sla_cache_enabled', True)
        self.cache_ttl = getattr(config, 'sla_cache_ttl', 300)  # 5 minutes default
        
        # Cache keys
        self.cache_keys = {
            'sla_policies': 'sla:policies',
            'ticket_sla_status': 'sla:ticket:{}',
            'technician_metrics': 'sla:technician:{}:{}',
            'user_list': 'sla:users',
            'ticket_list': 'sla:tickets'
        }
    
    async def initialize(self):
        """Initialize data access layer"""
        try:
            # Initialize SuperOps client
            if not self.superops_client.session:
                await self.superops_client.connect()
            
            # Initialize Redis cache
            if self.cache_enabled:
                await self._initialize_cache()
            
            self.logger.info("SLA Data Access layer initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize SLA Data Access: {e}")
            raise SLADataAccessError("initialize", str(e))
    
    async def cleanup(self):
        """Cleanup data access layer"""
        try:
            # Close SuperOps client
            if self.superops_client:
                await self.superops_client.disconnect()
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
            
            self.logger.info("SLA Data Access layer cleaned up successfully")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    async def _initialize_cache(self):
        """Initialize Redis cache connection"""
        try:
            redis_url = getattr(self.config, 'redis_url', 'redis://localhost:6379')
            self.redis_client = redis.from_url(redis_url)
            
            # Test connection
            await self.redis_client.ping()
            self.logger.info("Redis cache initialized successfully")
            
        except Exception as e:
            self.logger.warning(f"Failed to initialize Redis cache: {e}")
            self.cache_enabled = False
    
    # ==================== SLA POLICY OPERATIONS ====================
    
    async def fetch_sla_policies_from_api(self) -> List[SLAPolicy]:
        """Fetch SLA policies from SuperOps API"""
        try:
            self.logger.info("Fetching SLA policies from SuperOps API")
            
            # Get raw data from API
            raw_policies = await self.superops_client.get_sla_list(force_refresh=True)
            
            # Transform to SLAPolicy objects
            policies = []
            for raw_policy in raw_policies:
                try:
                    policy = self._transform_sla_policy(raw_policy)
                    policies.append(policy)
                except Exception as e:
                    self.logger.warning(f"Failed to transform SLA policy {raw_policy.get('id', 'unknown')}: {e}")
                    continue
            
            self.logger.info(f"Successfully fetched {len(policies)} SLA policies")
            return policies
            
        except Exception as e:
            self.logger.error(f"Failed to fetch SLA policies from API: {e}")
            raise SLADataAccessError("fetch_sla_policies_from_api", str(e), "SuperOps API")
    
    async def get_cached_sla_policies(self) -> List[SLAPolicy]:
        """Get SLA policies from cache"""
        try:
            if not self.cache_enabled or not self.redis_client:
                return await self.fetch_sla_policies_from_api()
            
            cache_key = self.cache_keys['sla_policies']
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                self.logger.debug("Retrieved SLA policies from cache")
                policies_data = json.loads(cached_data)
                return [SLAPolicy(**policy_data) for policy_data in policies_data]
            else:
                # Cache miss - fetch from API and cache
                policies = await self.fetch_sla_policies_from_api()
                await self.update_sla_cache(policies)
                return policies
                
        except Exception as e:
            self.logger.error(f"Failed to get cached SLA policies: {e}")
            # Fallback to API
            return await self.fetch_sla_policies_from_api()
    
    async def update_sla_cache(self, policies: List[SLAPolicy]) -> None:
        """Update SLA policies in cache"""
        try:
            if not self.cache_enabled or not self.redis_client:
                return
            
            cache_key = self.cache_keys['sla_policies']
            policies_data = [policy.__dict__ for policy in policies]
            
            await self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(policies_data, default=str)
            )
            
            self.logger.debug(f"Updated SLA policies cache with {len(policies)} policies")
            
        except Exception as e:
            self.logger.warning(f"Failed to update SLA policies cache: {e}")
    
    async def get_sla_policy_by_priority(self, priority: str) -> Optional[SLAPolicy]:
        """Get SLA policy by ticket priority"""
        try:
            policies = await self.get_cached_sla_policies()
            
            # Find policy matching priority
            for policy in policies:
                if policy.priority_level.value.lower() == priority.lower():
                    return policy
            
            # If no exact match, try to find a default policy
            for policy in policies:
                if policy.name.lower() in ['default', 'standard']:
                    self.logger.warning(f"No SLA policy found for priority {priority}, using default policy")
                    return policy
            
            raise SLAPolicyNotFoundError(priority=priority)
            
        except SLAPolicyNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to get SLA policy by priority {priority}: {e}")
            raise SLADataAccessError("get_sla_policy_by_priority", str(e))
    
    # ==================== TICKET SLA OPERATIONS ====================
    
    async def fetch_ticket_sla_data(self, ticket_id: str) -> Dict[str, Any]:
        """Fetch ticket SLA data from SuperOps API"""
        try:
            self.logger.info(f"Fetching SLA data for ticket {ticket_id}")
            
            # Get SLA status from API
            sla_status = await self.superops_client.get_ticket_sla_status(ticket_id)
            
            if not sla_status:
                raise SLADataAccessError("fetch_ticket_sla_data", f"No SLA data found for ticket {ticket_id}", "SuperOps API")
            
            self.logger.info(f"Successfully fetched SLA data for ticket {ticket_id}")
            return sla_status
            
        except Exception as e:
            self.logger.error(f"Failed to fetch SLA data for ticket {ticket_id}: {e}")
            raise SLADataAccessError("fetch_ticket_sla_data", str(e), "SuperOps API")
    
    async def get_cached_ticket_sla_data(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """Get ticket SLA data from cache"""
        try:
            if not self.cache_enabled or not self.redis_client:
                return await self.fetch_ticket_sla_data(ticket_id)
            
            cache_key = self.cache_keys['ticket_sla_status'].format(ticket_id)
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                self.logger.debug(f"Retrieved SLA data for ticket {ticket_id} from cache")
                return json.loads(cached_data)
            else:
                # Cache miss - fetch from API and cache
                sla_data = await self.fetch_ticket_sla_data(ticket_id)
                await self._cache_ticket_sla_data(ticket_id, sla_data)
                return sla_data
                
        except Exception as e:
            self.logger.error(f"Failed to get cached SLA data for ticket {ticket_id}: {e}")
            # Fallback to API
            return await self.fetch_ticket_sla_data(ticket_id)
    
    async def _cache_ticket_sla_data(self, ticket_id: str, sla_data: Dict[str, Any]) -> None:
        """Cache ticket SLA data"""
        try:
            if not self.cache_enabled or not self.redis_client:
                return
            
            cache_key = self.cache_keys['ticket_sla_status'].format(ticket_id)
            
            # Use shorter TTL for ticket data (1 minute) as it changes frequently
            ticket_ttl = min(self.cache_ttl, 60)
            
            await self.redis_client.setex(
                cache_key,
                ticket_ttl,
                json.dumps(sla_data, default=str)
            )
            
            self.logger.debug(f"Cached SLA data for ticket {ticket_id}")
            
        except Exception as e:
            self.logger.warning(f"Failed to cache SLA data for ticket {ticket_id}: {e}")
    
    # ==================== TECHNICIAN METRICS OPERATIONS ====================
    
    async def fetch_technician_metrics(self, technician_id: str, date_range: DateRange) -> Dict[str, Any]:
        """Fetch technician SLA metrics from SuperOps API"""
        try:
            self.logger.info(f"Fetching SLA metrics for technician {technician_id}")
            
            # Get metrics from API
            metrics = await self.superops_client.get_technician_sla_metrics(technician_id, date_range)
            
            if not metrics:
                # Return empty metrics if none found
                return {
                    'technicianId': technician_id,
                    'technicianName': 'Unknown',
                    'technicianEmail': '',
                    'periodStart': date_range.start_date.isoformat(),
                    'periodEnd': date_range.end_date.isoformat(),
                    'totalTickets': 0,
                    'slaCompliantTickets': 0,
                    'responseBreaches': 0,
                    'resolutionBreaches': 0,
                    'averageResponseTime': None,
                    'averageResolutionTime': None,
                    'performanceTrend': 'STABLE',
                    'lastUpdated': datetime.now().isoformat()
                }
            
            self.logger.info(f"Successfully fetched SLA metrics for technician {technician_id}")
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to fetch SLA metrics for technician {technician_id}: {e}")
            raise SLADataAccessError("fetch_technician_metrics", str(e), "SuperOps API")
    
    async def get_cached_technician_metrics(self, technician_id: str, date_range: DateRange) -> Dict[str, Any]:
        """Get technician SLA metrics from cache"""
        try:
            if not self.cache_enabled or not self.redis_client:
                return await self.fetch_technician_metrics(technician_id, date_range)
            
            # Create cache key with date range
            date_key = f"{date_range.start_date.date()}_{date_range.end_date.date()}"
            cache_key = self.cache_keys['technician_metrics'].format(technician_id, date_key)
            
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                self.logger.debug(f"Retrieved SLA metrics for technician {technician_id} from cache")
                return json.loads(cached_data)
            else:
                # Cache miss - fetch from API and cache
                metrics = await self.fetch_technician_metrics(technician_id, date_range)
                await self._cache_technician_metrics(technician_id, date_range, metrics)
                return metrics
                
        except Exception as e:
            self.logger.error(f"Failed to get cached SLA metrics for technician {technician_id}: {e}")
            # Fallback to API
            return await self.fetch_technician_metrics(technician_id, date_range)
    
    async def _cache_technician_metrics(self, technician_id: str, date_range: DateRange, metrics: Dict[str, Any]) -> None:
        """Cache technician SLA metrics"""
        try:
            if not self.cache_enabled or not self.redis_client:
                return
            
            date_key = f"{date_range.start_date.date()}_{date_range.end_date.date()}"
            cache_key = self.cache_keys['technician_metrics'].format(technician_id, date_key)
            
            # Use longer TTL for historical metrics (10 minutes)
            metrics_ttl = max(self.cache_ttl, 600)
            
            await self.redis_client.setex(
                cache_key,
                metrics_ttl,
                json.dumps(metrics, default=str)
            )
            
            self.logger.debug(f"Cached SLA metrics for technician {technician_id}")
            
        except Exception as e:
            self.logger.warning(f"Failed to cache SLA metrics for technician {technician_id}: {e}")
    
    # ==================== USER AND TICKET OPERATIONS ====================
    
    async def get_user_list(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """Get user list with caching"""
        try:
            if not force_refresh and self.cache_enabled and self.redis_client:
                cache_key = self.cache_keys['user_list']
                cached_data = await self.redis_client.get(cache_key)
                
                if cached_data:
                    self.logger.debug("Retrieved user list from cache")
                    return json.loads(cached_data)
            
            # Fetch from API
            users = await self.superops_client.get_user_list(force_refresh=True)
            
            # Cache the result
            if self.cache_enabled and self.redis_client:
                cache_key = self.cache_keys['user_list']
                await self.redis_client.setex(
                    cache_key,
                    self.cache_ttl,
                    json.dumps(users, default=str)
                )
            
            return users
            
        except Exception as e:
            self.logger.error(f"Failed to get user list: {e}")
            raise SLADataAccessError("get_user_list", str(e), "SuperOps API")
    
    async def get_ticket_list(self, filters: Dict[str, Any] = None, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """Get ticket list with caching"""
        try:
            # Don't cache filtered results
            if filters or not self.cache_enabled or not self.redis_client or force_refresh:
                return await self.superops_client.get_ticket_list(filters, force_refresh=True)
            
            cache_key = self.cache_keys['ticket_list']
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                self.logger.debug("Retrieved ticket list from cache")
                return json.loads(cached_data)
            
            # Fetch from API
            tickets = await self.superops_client.get_ticket_list(force_refresh=True)
            
            # Cache the result with shorter TTL (1 minute)
            await self.redis_client.setex(
                cache_key,
                60,  # 1 minute TTL for tickets
                json.dumps(tickets, default=str)
            )
            
            return tickets
            
        except Exception as e:
            self.logger.error(f"Failed to get ticket list: {e}")
            raise SLADataAccessError("get_ticket_list", str(e), "SuperOps API")
    
    async def get_urgent_tickets(self) -> List[Dict[str, Any]]:
        """Get urgent tickets"""
        try:
            return await self.superops_client.get_urgent_tickets()
        except Exception as e:
            self.logger.error(f"Failed to get urgent tickets: {e}")
            raise SLADataAccessError("get_urgent_tickets", str(e), "SuperOps API")
    
    async def get_tickets_at_risk(self, risk_level: str = "HIGH") -> List[Dict[str, Any]]:
        """Get tickets at risk of SLA breach"""
        try:
            return await self.superops_client.get_tickets_at_risk(risk_level)
        except Exception as e:
            self.logger.error(f"Failed to get tickets at risk: {e}")
            raise SLADataAccessError("get_tickets_at_risk", str(e), "SuperOps API")
    
    # ==================== DATA TRANSFORMATION ====================
    
    def _transform_sla_policy(self, raw_policy: Dict[str, Any]) -> SLAPolicy:
        """Transform raw API data to SLAPolicy object"""
        try:
            # Map priority string to enum
            priority_str = raw_policy.get('priority', 'medium').lower()
            priority_mapping = {
                'low': SLAPriority.LOW,
                'medium': SLAPriority.MEDIUM,
                'high': SLAPriority.HIGH,
                'critical': SLAPriority.CRITICAL
            }
            priority = priority_mapping.get(priority_str, SLAPriority.MEDIUM)
            
            # Parse dates
            created_at = self._parse_datetime(raw_policy.get('createdAt'))
            updated_at = self._parse_datetime(raw_policy.get('updatedAt'))
            
            return SLAPolicy(
                id=raw_policy['id'],
                name=raw_policy.get('name', ''),
                description=raw_policy.get('description', ''),
                priority_level=priority,
                response_time_minutes=raw_policy.get('responseTimeMinutes', 60),
                resolution_time_hours=raw_policy.get('resolutionTimeHours', 24),
                business_hours_only=raw_policy.get('businessHoursOnly', True),
                escalation_rules=[],  # TODO: Transform escalation rules
                alert_rules=[],       # TODO: Transform alert rules
                is_active=raw_policy.get('isActive', True),
                created_at=created_at,
                updated_at=updated_at
            )
            
        except Exception as e:
            self.logger.error(f"Failed to transform SLA policy: {e}")
            raise SLADataAccessError("transform_sla_policy", str(e))
    
    def _parse_datetime(self, date_str: Optional[str]) -> datetime:
        """Parse datetime string from API"""
        if not date_str:
            return datetime.now()
        
        try:
            # Try ISO format first
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            try:
                # Try other common formats
                return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            except:
                return datetime.now()
    
    # ==================== CACHE MANAGEMENT ====================
    
    async def clear_cache(self, pattern: str = None) -> None:
        """Clear cache entries"""
        try:
            if not self.cache_enabled or not self.redis_client:
                return
            
            if pattern:
                # Clear specific pattern
                keys = await self.redis_client.keys(pattern)
                if keys:
                    await self.redis_client.delete(*keys)
                    self.logger.info(f"Cleared {len(keys)} cache entries matching pattern: {pattern}")
            else:
                # Clear all SLA cache entries
                for cache_key in self.cache_keys.values():
                    if '{}' not in cache_key:  # Skip template keys
                        await self.redis_client.delete(cache_key)
                
                self.logger.info("Cleared all SLA cache entries")
                
        except Exception as e:
            self.logger.warning(f"Failed to clear cache: {e}")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            if not self.cache_enabled or not self.redis_client:
                return {"cache_enabled": False}
            
            stats = {"cache_enabled": True}
            
            for name, cache_key in self.cache_keys.items():
                if '{}' not in cache_key:  # Skip template keys
                    exists = await self.redis_client.exists(cache_key)
                    if exists:
                        ttl = await self.redis_client.ttl(cache_key)
                        stats[name] = {"exists": True, "ttl": ttl}
                    else:
                        stats[name] = {"exists": False}
            
            return stats
            
        except Exception as e:
            self.logger.warning(f"Failed to get cache stats: {e}")
            return {"cache_enabled": False, "error": str(e)}    

    # ==================== MISSING METHODS FOR SLA MONITOR ====================
    
    async def get_all_sla_policies(self) -> List[SLAPolicy]:
        """Get all SLA policies (wrapper for existing method)"""
        try:
            return await self.get_cached_sla_policies()
        except Exception as e:
            self.logger.error(f"Error getting all SLA policies: {e}")
            return []
    
    async def get_active_tickets(self) -> List[Dict[str, Any]]:
        """Get all active tickets for SLA monitoring"""
        try:
            # Get tickets that are not closed/resolved
            filters = {
                "status": ["Open", "In Progress", "Pending", "Assigned"]
            }
            tickets = await self.get_ticket_list(filters=filters)
            
            # Filter for active tickets only
            active_tickets = []
            for ticket in tickets:
                status = ticket.get('status', '').lower()
                if status not in ['closed', 'resolved', 'cancelled']:
                    active_tickets.append(ticket)
            
            self.logger.info(f"Found {len(active_tickets)} active tickets for SLA monitoring")
            return active_tickets
            
        except Exception as e:
            self.logger.error(f"Error getting active tickets: {e}")
            return []