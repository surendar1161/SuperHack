"""
Extended SuperOps client for SLA management operations

This client extends the base SuperOps client with comprehensive SLA functionality
including metadata sync, event monitoring, and automated actions.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
import aiohttp

from .superops_client import SuperOpsClient
from .exceptions import SuperOpsAPIError, AuthenticationError, RateLimitError
from .graphql.queries import (
    # SLA Queries
    GET_SLA_POLICIES_QUERY,
    GET_SLA_POLICY_QUERY,
    GET_TICKET_SLA_STATUS_QUERY,
    GET_SLA_BREACHES_QUERY,
    GET_TECHNICIAN_SLA_METRICS_QUERY,
    GET_ALL_TECHNICIANS_SLA_METRICS_QUERY,
    
    # Enhanced User/Ticket Queries
    GET_ALL_USERS_QUERY,
    GET_USER_LIST_QUERY,
    GET_TICKETS_WITH_SLA_QUERY,
    GET_URGENT_TICKETS_QUERY,
    GET_TICKETS_AT_RISK_QUERY,
    
    # Task Queries
    GET_TASKS_QUERY,
    GET_OPEN_TASKS_QUERY,
    GET_SCHEDULED_TASKS_QUERY,
    GET_COMPLETED_TASKS_QUERY,
    
    # Event Monitoring
    GET_RECENT_TICKET_EVENTS_QUERY,
    GET_SLA_EVENTS_QUERY,
    
    # Reporting
    GET_SLA_REPORT_DATA_QUERY,
    
    # Mutations
    ADD_TICKET_COMMENT_MUTATION,
    UPDATE_TICKET_PRIORITY_MUTATION,
    ESCALATE_TICKET_MUTATION,
    ASSIGN_TICKET_MUTATION,
    UPDATE_TICKET_STATUS_MUTATION,
    CREATE_SLA_BREACH_RECORD_MUTATION,
    SEND_NOTIFICATION_MUTATION,
    UPDATE_SLA_POLICY_MUTATION
)
from ..tools.sla.models import (
    SLAPolicy,
    TicketSLAStatus,
    TechnicianSLAMetrics,
    SLABreach,
    DateRange
)
from ..tools.sla.exceptions import SLADataAccessError
from ..utils.logger import get_logger


class SLASuperOpsClient(SuperOpsClient):
    """
    Extended SuperOps client with comprehensive SLA management capabilities
    
    Features:
    - Metadata endpoints integration (users, SLAs, tasks, tickets)
    - Centralized event monitoring
    - Event-driven decision logic
    - Automated action execution
    - Periodic metadata sync
    """
    
    def __init__(self, config):
        super().__init__(config)
        self.logger = get_logger(self.__class__.__name__)
        
        # Event monitoring
        self.event_queue = asyncio.Queue()
        self.monitoring_active = False
        self.last_sync_time = None
        
        # Caching for performance
        self.cache = {
            'users': {},
            'sla_policies': {},
            'tickets': {},
            'tasks': {},
            'last_updated': {}
        }
        
        # Sync intervals (in seconds)
        self.sync_intervals = {
            'users': 300,      # 5 minutes
            'sla_policies': 600,  # 10 minutes
            'tickets': 60,     # 1 minute
            'tasks': 180       # 3 minutes
        }
    
    # ==================== METADATA ENDPOINTS INTEGRATION ====================
    
    async def get_user_list(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Get user list (/users): Regularly sync all active users and roles
        """
        try:
            cache_key = 'users'
            
            # Check cache first
            if not force_refresh and self._is_cache_valid(cache_key):
                self.logger.debug("Returning cached user list")
                return list(self.cache[cache_key].values())
            
            self.logger.info("Fetching user list from SuperOps API")
            
            query_data = {
                "query": GET_USER_LIST_QUERY
            }
            
            result = await self._execute_query(query_data)
            
            if result and "data" in result and "users" in result["data"]:
                users = result["data"]["users"]
                
                # Update cache
                self.cache[cache_key] = {user["id"]: user for user in users}
                self.cache['last_updated'][cache_key] = datetime.now()
                
                self.logger.info(f"Successfully fetched {len(users)} users")
                return users
            else:
                raise SLADataAccessError("get_user_list", "Invalid response format", "SuperOps API")
                
        except Exception as e:
            self.logger.error(f"Failed to fetch user list: {e}")
            raise SLADataAccessError("get_user_list", str(e), "SuperOps API")
    
    async def get_sla_list(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Get SLA list/details (/slas): Ingest SLA policies and breach thresholds
        """
        try:
            cache_key = 'sla_policies'
            
            # Check cache first
            if not force_refresh and self._is_cache_valid(cache_key):
                self.logger.debug("Returning cached SLA policies")
                return list(self.cache[cache_key].values())
            
            self.logger.info("Fetching SLA policies from SuperOps API")
            
            query_data = {
                "query": GET_SLA_POLICIES_QUERY
            }
            
            result = await self._execute_query(query_data)
            
            if result and "data" in result and "slaPolicies" in result["data"]:
                sla_policies = result["data"]["slaPolicies"]
                
                # Update cache
                self.cache[cache_key] = {policy["id"]: policy for policy in sla_policies}
                self.cache['last_updated'][cache_key] = datetime.now()
                
                self.logger.info(f"Successfully fetched {len(sla_policies)} SLA policies")
                return sla_policies
            else:
                raise SLADataAccessError("get_sla_list", "Invalid response format", "SuperOps API")
                
        except Exception as e:
            self.logger.error(f"Failed to fetch SLA policies: {e}")
            raise SLADataAccessError("get_sla_list", str(e), "SuperOps API")
    
    async def get_task_list(self, filters: Dict[str, Any] = None, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Get task list (/tasks): Fetch all open, scheduled, and completed tasks
        """
        try:
            cache_key = 'tasks'
            
            # Check cache first (only if no specific filters)
            if not filters and not force_refresh and self._is_cache_valid(cache_key):
                self.logger.debug("Returning cached task list")
                return list(self.cache[cache_key].values())
            
            self.logger.info("Fetching task list from SuperOps API")
            
            # Get different types of tasks
            tasks = []
            
            # Open tasks
            open_tasks_result = await self._execute_query({"query": GET_OPEN_TASKS_QUERY})
            if open_tasks_result and "data" in open_tasks_result and "openTasks" in open_tasks_result["data"]:
                tasks.extend(open_tasks_result["data"]["openTasks"])
            
            # Scheduled tasks (next 7 days)
            date_range = f"{datetime.now().isoformat()},{(datetime.now() + timedelta(days=7)).isoformat()}"
            scheduled_query = {
                "query": GET_SCHEDULED_TASKS_QUERY,
                "variables": {"dateRange": date_range}
            }
            scheduled_result = await self._execute_query(scheduled_query)
            if scheduled_result and "data" in scheduled_result and "scheduledTasks" in scheduled_result["data"]:
                tasks.extend(scheduled_result["data"]["scheduledTasks"])
            
            # Completed tasks (last 24 hours)
            completed_date_range = f"{(datetime.now() - timedelta(days=1)).isoformat()},{datetime.now().isoformat()}"
            completed_query = {
                "query": GET_COMPLETED_TASKS_QUERY,
                "variables": {"dateRange": completed_date_range, "filters": filters or {}}
            }
            completed_result = await self._execute_query(completed_query)
            if completed_result and "data" in completed_result and "completedTasks" in completed_result["data"]:
                tasks.extend(completed_result["data"]["completedTasks"])
            
            # Update cache (only if no specific filters)
            if not filters:
                self.cache[cache_key] = {task["id"]: task for task in tasks}
                self.cache['last_updated'][cache_key] = datetime.now()
            
            self.logger.info(f"Successfully fetched {len(tasks)} tasks")
            return tasks
            
        except Exception as e:
            self.logger.error(f"Failed to fetch task list: {e}")
            raise SLADataAccessError("get_task_list", str(e), "SuperOps API")
    
    async def get_ticket_list(self, filters: Dict[str, Any] = None, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Get ticket list (/tickets): Continuously update open/assigned/urgent ticket data
        """
        try:
            cache_key = 'tickets'
            
            # Check cache first (only if no specific filters)
            if not filters and not force_refresh and self._is_cache_valid(cache_key):
                self.logger.debug("Returning cached ticket list")
                return list(self.cache[cache_key].values())
            
            self.logger.info("Fetching ticket list from SuperOps API")
            
            query_data = {
                "query": GET_TICKETS_WITH_SLA_QUERY,
                "variables": {
                    "filters": filters or {},
                    "limit": 1000,
                    "offset": 0
                }
            }
            
            result = await self._execute_query(query_data)
            
            if result and "data" in result and "tickets" in result["data"]:
                tickets = result["data"]["tickets"]
                
                # Update cache (only if no specific filters)
                if not filters:
                    self.cache[cache_key] = {ticket["id"]: ticket for ticket in tickets}
                    self.cache['last_updated'][cache_key] = datetime.now()
                
                self.logger.info(f"Successfully fetched {len(tickets)} tickets")
                return tickets
            else:
                raise SLADataAccessError("get_ticket_list", "Invalid response format", "SuperOps API")
                
        except Exception as e:
            self.logger.error(f"Failed to fetch ticket list: {e}")
            raise SLADataAccessError("get_ticket_list", str(e), "SuperOps API")
    
    async def get_urgent_tickets(self) -> List[Dict[str, Any]]:
        """Get urgent tickets with SLA status"""
        try:
            self.logger.info("Fetching urgent tickets from SuperOps API")
            
            query_data = {"query": GET_URGENT_TICKETS_QUERY}
            result = await self._execute_query(query_data)
            
            if result and "data" in result and "urgentTickets" in result["data"]:
                tickets = result["data"]["urgentTickets"]
                self.logger.info(f"Successfully fetched {len(tickets)} urgent tickets")
                return tickets
            else:
                raise SLADataAccessError("get_urgent_tickets", "Invalid response format", "SuperOps API")
                
        except Exception as e:
            self.logger.error(f"Failed to fetch urgent tickets: {e}")
            raise SLADataAccessError("get_urgent_tickets", str(e), "SuperOps API")
    
    async def get_tickets_at_risk(self, risk_level: str = "HIGH") -> List[Dict[str, Any]]:
        """Get tickets at risk of SLA breach"""
        try:
            self.logger.info(f"Fetching tickets at {risk_level} risk from SuperOps API")
            
            query_data = {
                "query": GET_TICKETS_AT_RISK_QUERY,
                "variables": {"riskLevel": risk_level}
            }
            
            result = await self._execute_query(query_data)
            
            if result and "data" in result and "ticketsAtRisk" in result["data"]:
                tickets = result["data"]["ticketsAtRisk"]
                self.logger.info(f"Successfully fetched {len(tickets)} tickets at risk")
                return tickets
            else:
                raise SLADataAccessError("get_tickets_at_risk", "Invalid response format", "SuperOps API")
                
        except Exception as e:
            self.logger.error(f"Failed to fetch tickets at risk: {e}")
            raise SLADataAccessError("get_tickets_at_risk", str(e), "SuperOps API")
    
    # ==================== SLA-SPECIFIC OPERATIONS ====================
    
    async def get_ticket_sla_status(self, ticket_id: str) -> Dict[str, Any]:
        """Get SLA status for a specific ticket"""
        try:
            self.logger.info(f"Fetching SLA status for ticket {ticket_id}")
            
            query_data = {
                "query": GET_TICKET_SLA_STATUS_QUERY,
                "variables": {"ticketId": ticket_id}
            }
            
            result = await self._execute_query(query_data)
            
            if result and "data" in result and "ticketSLAStatus" in result["data"]:
                sla_status = result["data"]["ticketSLAStatus"]
                self.logger.info(f"Successfully fetched SLA status for ticket {ticket_id}")
                return sla_status
            else:
                raise SLADataAccessError("get_ticket_sla_status", "Invalid response format", "SuperOps API")
                
        except Exception as e:
            self.logger.error(f"Failed to fetch SLA status for ticket {ticket_id}: {e}")
            raise SLADataAccessError("get_ticket_sla_status", str(e), "SuperOps API")
    
    async def get_technician_sla_metrics(self, technician_id: str, date_range: DateRange) -> Dict[str, Any]:
        """Get SLA metrics for a specific technician"""
        try:
            self.logger.info(f"Fetching SLA metrics for technician {technician_id}")
            
            date_range_str = f"{date_range.start_date.isoformat()},{date_range.end_date.isoformat()}"
            
            query_data = {
                "query": GET_TECHNICIAN_SLA_METRICS_QUERY,
                "variables": {
                    "technicianId": technician_id,
                    "dateRange": date_range_str
                }
            }
            
            result = await self._execute_query(query_data)
            
            if result and "data" in result and "technicianSLAMetrics" in result["data"]:
                metrics = result["data"]["technicianSLAMetrics"]
                self.logger.info(f"Successfully fetched SLA metrics for technician {technician_id}")
                return metrics
            else:
                raise SLADataAccessError("get_technician_sla_metrics", "Invalid response format", "SuperOps API")
                
        except Exception as e:
            self.logger.error(f"Failed to fetch SLA metrics for technician {technician_id}: {e}")
            raise SLADataAccessError("get_technician_sla_metrics", str(e), "SuperOps API")
    
    async def get_sla_breaches(self, date_range: DateRange, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get SLA breaches for a date range"""
        try:
            self.logger.info(f"Fetching SLA breaches for date range {date_range.start_date} to {date_range.end_date}")
            
            date_range_str = f"{date_range.start_date.isoformat()},{date_range.end_date.isoformat()}"
            
            query_data = {
                "query": GET_SLA_BREACHES_QUERY,
                "variables": {
                    "dateRange": date_range_str,
                    "filters": filters or {}
                }
            }
            
            result = await self._execute_query(query_data)
            
            if result and "data" in result and "slaBreaches" in result["data"]:
                breaches = result["data"]["slaBreaches"]
                self.logger.info(f"Successfully fetched {len(breaches)} SLA breaches")
                return breaches
            else:
                raise SLADataAccessError("get_sla_breaches", "Invalid response format", "SuperOps API")
                
        except Exception as e:
            self.logger.error(f"Failed to fetch SLA breaches: {e}")
            raise SLADataAccessError("get_sla_breaches", str(e), "SuperOps API")
    
    # ==================== EVENT MONITORING ====================
    
    async def start_event_monitoring(self):
        """Start centralized event monitoring"""
        try:
            self.monitoring_active = True
            self.logger.info("Starting SLA event monitoring")
            
            # Start monitoring tasks
            asyncio.create_task(self._monitor_ticket_events())
            asyncio.create_task(self._monitor_sla_events())
            asyncio.create_task(self._periodic_metadata_sync())
            
        except Exception as e:
            self.logger.error(f"Failed to start event monitoring: {e}")
            raise
    
    async def stop_event_monitoring(self):
        """Stop centralized event monitoring"""
        self.monitoring_active = False
        self.logger.info("Stopped SLA event monitoring")
    
    async def _monitor_ticket_events(self):
        """Monitor ticket events for SLA-relevant changes"""
        while self.monitoring_active:
            try:
                # Get recent ticket events (last 5 minutes)
                since = (datetime.now() - timedelta(minutes=5)).isoformat()
                
                query_data = {
                    "query": GET_RECENT_TICKET_EVENTS_QUERY,
                    "variables": {"since": since}
                }
                
                result = await self._execute_query(query_data)
                
                if result and "data" in result and "recentTicketEvents" in result["data"]:
                    events = result["data"]["recentTicketEvents"]
                    
                    for event in events:
                        await self.event_queue.put({
                            "type": "ticket_event",
                            "data": event,
                            "timestamp": datetime.now()
                        })
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error monitoring ticket events: {e}")
                await asyncio.sleep(60)
    
    async def _monitor_sla_events(self):
        """Monitor SLA-specific events"""
        while self.monitoring_active:
            try:
                # Get recent SLA events (last 5 minutes)
                since = (datetime.now() - timedelta(minutes=5)).isoformat()
                
                query_data = {
                    "query": GET_SLA_EVENTS_QUERY,
                    "variables": {"since": since}
                }
                
                result = await self._execute_query(query_data)
                
                if result and "data" in result and "slaEvents" in result["data"]:
                    events = result["data"]["slaEvents"]
                    
                    for event in events:
                        await self.event_queue.put({
                            "type": "sla_event",
                            "data": event,
                            "timestamp": datetime.now()
                        })
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error monitoring SLA events: {e}")
                await asyncio.sleep(60)
    
    async def _periodic_metadata_sync(self):
        """Periodic metadata synchronization"""
        while self.monitoring_active:
            try:
                current_time = datetime.now()
                
                # Check each metadata type for sync needs
                for metadata_type, interval in self.sync_intervals.items():
                    last_sync = self.cache['last_updated'].get(metadata_type)
                    
                    if not last_sync or (current_time - last_sync).total_seconds() > interval:
                        self.logger.info(f"Syncing {metadata_type} metadata")
                        
                        if metadata_type == 'users':
                            await self.get_user_list(force_refresh=True)
                        elif metadata_type == 'sla_policies':
                            await self.get_sla_list(force_refresh=True)
                        elif metadata_type == 'tickets':
                            await self.get_ticket_list(force_refresh=True)
                        elif metadata_type == 'tasks':
                            await self.get_task_list(force_refresh=True)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in periodic metadata sync: {e}")
                await asyncio.sleep(60)
    
    # ==================== AUTOMATED ACTIONS ====================
    
    async def add_ticket_comment_with_mentions(self, ticket_id: str, comment: str, mention_user_ids: List[str], is_internal: bool = False) -> Dict[str, Any]:
        """
        Add comment to ticket with user mentions
        API: /tickets/{ticketId}/comments
        """
        try:
            self.logger.info(f"Adding comment to ticket {ticket_id} with mentions: {mention_user_ids}")
            
            # Format comment with mentions
            formatted_comment = comment
            for user_id in mention_user_ids:
                # SuperOps uses @[user_id] format for mentions
                formatted_comment += f" @[{user_id}]"
            
            mutation_data = {
                "query": ADD_TICKET_COMMENT_MUTATION,
                "variables": {
                    "ticketId": ticket_id,
                    "comment": formatted_comment,
                    "isInternal": is_internal,
                    "mentionUsers": mention_user_ids
                }
            }
            
            result = await self._execute_mutation(mutation_data)
            
            if result and "data" in result and "addTicketComment" in result["data"]:
                comment_result = result["data"]["addTicketComment"]
                self.logger.info(f"Successfully added comment to ticket {ticket_id}")
                return comment_result
            else:
                raise SuperOpsAPIError(f"Failed to add comment to ticket {ticket_id}")
                
        except Exception as e:
            self.logger.error(f"Failed to add comment to ticket {ticket_id}: {e}")
            raise SuperOpsAPIError(f"Comment addition failed: {e}")
    
    async def update_ticket_priority(self, ticket_id: str, priority: str) -> Dict[str, Any]:
        """Update ticket priority"""
        try:
            self.logger.info(f"Updating ticket {ticket_id} priority to {priority}")
            
            mutation_data = {
                "query": UPDATE_TICKET_PRIORITY_MUTATION,
                "variables": {
                    "ticketId": ticket_id,
                    "priority": priority
                }
            }
            
            result = await self._execute_mutation(mutation_data)
            
            if result and "data" in result and "updateTicketPriority" in result["data"]:
                update_result = result["data"]["updateTicketPriority"]
                self.logger.info(f"Successfully updated ticket {ticket_id} priority")
                return update_result
            else:
                raise SuperOpsAPIError(f"Failed to update ticket {ticket_id} priority")
                
        except Exception as e:
            self.logger.error(f"Failed to update ticket {ticket_id} priority: {e}")
            raise SuperOpsAPIError(f"Priority update failed: {e}")
    
    async def escalate_ticket(self, ticket_id: str, escalation_level: int, reason: str) -> Dict[str, Any]:
        """Escalate ticket to higher level"""
        try:
            self.logger.info(f"Escalating ticket {ticket_id} to level {escalation_level}")
            
            mutation_data = {
                "query": ESCALATE_TICKET_MUTATION,
                "variables": {
                    "ticketId": ticket_id,
                    "escalationLevel": escalation_level,
                    "reason": reason
                }
            }
            
            result = await self._execute_mutation(mutation_data)
            
            if result and "data" in result and "escalateTicket" in result["data"]:
                escalation_result = result["data"]["escalateTicket"]
                self.logger.info(f"Successfully escalated ticket {ticket_id}")
                return escalation_result
            else:
                raise SuperOpsAPIError(f"Failed to escalate ticket {ticket_id}")
                
        except Exception as e:
            self.logger.error(f"Failed to escalate ticket {ticket_id}: {e}")
            raise SuperOpsAPIError(f"Ticket escalation failed: {e}")
    
    async def create_sla_breach_record(self, breach_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create SLA breach record for audit and reporting"""
        try:
            self.logger.info(f"Creating SLA breach record for ticket {breach_data.get('ticketId')}")
            
            mutation_data = {
                "query": CREATE_SLA_BREACH_RECORD_MUTATION,
                "variables": {"input": breach_data}
            }
            
            result = await self._execute_mutation(mutation_data)
            
            if result and "data" in result and "createSLABreachRecord" in result["data"]:
                breach_result = result["data"]["createSLABreachRecord"]
                self.logger.info(f"Successfully created SLA breach record")
                return breach_result
            else:
                raise SuperOpsAPIError("Failed to create SLA breach record")
                
        except Exception as e:
            self.logger.error(f"Failed to create SLA breach record: {e}")
            raise SuperOpsAPIError(f"SLA breach record creation failed: {e}")
    
    # ==================== UTILITY METHODS ====================
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache is valid for the given key"""
        if cache_key not in self.cache['last_updated']:
            return False
        
        last_updated = self.cache['last_updated'][cache_key]
        interval = self.sync_intervals.get(cache_key, 300)  # Default 5 minutes
        
        return (datetime.now() - last_updated).total_seconds() < interval
    
    async def _execute_query(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute GraphQL query with error handling"""
        try:
            async with self.session.post(
                self.api_url,
                json=query_data,
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                response_text = await response.text()
                
                if response.status == 200:
                    result = json.loads(response_text)
                    
                    if "errors" in result:
                        error_messages = [err.get("message", str(err)) for err in result["errors"]]
                        raise SuperOpsAPIError(f"GraphQL errors: {'; '.join(error_messages)}")
                    
                    return result
                elif response.status == 401:
                    raise AuthenticationError("Invalid API key or expired token")
                elif response.status == 429:
                    raise RateLimitError("API rate limit exceeded")
                else:
                    raise SuperOpsAPIError(f"HTTP error {response.status}: {response_text}")
                    
        except json.JSONDecodeError as e:
            raise SuperOpsAPIError(f"Invalid JSON response: {e}")
        except Exception as e:
            if isinstance(e, (SuperOpsAPIError, AuthenticationError, RateLimitError)):
                raise
            raise SuperOpsAPIError(f"Query execution failed: {e}")
    
    async def _execute_mutation(self, mutation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute GraphQL mutation with error handling"""
        return await self._execute_query(mutation_data)
    
    async def get_event_queue(self) -> asyncio.Queue:
        """Get the event queue for external processing"""
        return self.event_queue
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring"""
        stats = {}
        for key, data in self.cache.items():
            if key != 'last_updated' and isinstance(data, dict):
                stats[key] = {
                    'count': len(data),
                    'last_updated': self.cache['last_updated'].get(key)
                }
        return stats