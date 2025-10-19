"""
EventMonitorAgent - Monitors SuperOps events and webhooks
Handles real-time event detection and SLA monitoring
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
import aiohttp
from collections import deque
from .base_subagent import BaseSubagent, AgentMessage
from ..config import AgentConfig

@dataclass
class Event:
    """Event structure for monitoring"""
    id: str
    timestamp: datetime
    event_type: str
    source: str
    data: Dict[str, Any]
    processed: bool = False
    priority: int = 5

@dataclass
class SLABreach:
    """SLA breach detection result"""
    ticket_id: str
    sla_type: str  # response, resolution
    breach_time: datetime
    time_remaining: float  # negative if breached
    severity: str  # warning, critical, breached

class EventMonitorAgent(BaseSubagent):
    """
    Agent responsible for monitoring SuperOps events and webhooks
    
    Responsibilities:
    - Subscribe to SuperOps webhooks
    - Implement long-polling for real-time updates
    - Detect SLA breach conditions
    - Monitor ticket status changes
    
    Scalability Features:
    - Partitioned event processing
    - Stateless design for horizontal scaling
    - Event deduplication
    - Backpressure handling
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config, "EventMonitorAgent")
        
        # Configuration
        self.polling_interval = getattr(config, 'event_polling_interval', 30)  # 30 seconds
        self.event_buffer_size = getattr(config, 'event_buffer_size', 10000)
        self.partition_count = getattr(config, 'event_partition_count', 4)
        self.webhook_port = getattr(config, 'webhook_port', 8080)
        
        # Event processing
        self.event_buffer = deque(maxlen=self.event_buffer_size)
        self.processed_events = set()  # For deduplication
        self.event_partitions = [deque() for _ in range(self.partition_count)]
        
        # SLA monitoring
        self.sla_configs = {}
        self.monitored_tickets = {}
        
        # Webhook server
        self.webhook_app = None
        self.webhook_server = None
        
        # Long polling
        self.polling_tasks = []
        self.last_poll_timestamp = datetime.now()
    
    def _get_worker_count(self) -> int:
        """Get optimal worker count for event processing"""
        return max(2, self.partition_count)
    
    async def _initialize_agent(self):
        """Initialize event monitor agent"""
        # Load SLA configurations
        await self._load_sla_configurations()
        
        # Start webhook server
        await self._start_webhook_server()
        
        # Subscribe to topics
        await self.subscribe_to_topic("webhook-events", self._handle_webhook_event)
        await self.subscribe_to_topic("polling-requests", self._handle_polling_request)
        
        # Register as publisher
        await self.publish_to_topic("event-stream")
        
        # Start monitoring tasks
        asyncio.create_task(self._long_polling_loop())
        asyncio.create_task(self._sla_monitoring_loop())
        asyncio.create_task(self._event_processing_loop())
        
        self.logger.info("EventMonitorAgent initialized successfully")
    
    async def _cleanup_agent(self):
        """Cleanup event monitor agent"""
        # Stop webhook server
        if self.webhook_server:
            self.webhook_server.close()
            await self.webhook_server.wait_closed()
        
        # Cancel polling tasks
        for task in self.polling_tasks:
            task.cancel()
    
    async def _load_sla_configurations(self):
        """Load SLA configurations from metadata"""
        # Mock SLA configurations - in real implementation, load from MetadataSyncAgent
        self.sla_configs = {
            "critical": {"response_time": 1, "resolution_time": 4},  # hours
            "high": {"response_time": 4, "resolution_time": 24},
            "medium": {"response_time": 8, "resolution_time": 72},
            "low": {"response_time": 24, "resolution_time": 168}
        }
        
        self.logger.info(f"Loaded {len(self.sla_configs)} SLA configurations")
    
    async def _start_webhook_server(self):
        """Start webhook server for receiving SuperOps events"""
        from aiohttp import web
        
        self.webhook_app = web.Application()
        self.webhook_app.router.add_post('/webhook/superops', self._handle_webhook)
        self.webhook_app.router.add_get('/health', self._health_check)
        
        try:
            self.webhook_server = await asyncio.start_server(
                lambda r, w: None,  # Placeholder - aiohttp handles this
                '0.0.0.0',
                self.webhook_port
            )
            
            self.logger.info(f"Webhook server started on port {self.webhook_port}")
            
        except Exception as e:
            self.logger.error(f"Failed to start webhook server: {e}")
    
    async def _handle_webhook(self, request):
        """Handle incoming webhook from SuperOps"""
        try:
            data = await request.json()
            
            # Create event from webhook data
            event = Event(
                id=data.get('id', f"webhook_{datetime.now().isoformat()}"),
                timestamp=datetime.now(),
                event_type=data.get('event_type', 'unknown'),
                source='webhook',
                data=data,
                priority=self._calculate_event_priority(data)
            )
            
            # Add to event buffer
            await self._add_event_to_buffer(event)
            
            return web.json_response({"status": "received"})
            
        except Exception as e:
            self.logger.error(f"Error handling webhook: {e}")
            return web.json_response({"error": str(e)}, status=400)
    
    async def _health_check(self, request):
        """Health check endpoint"""
        return web.json_response({
            "status": "healthy",
            "agent": self.agent_name,
            "events_buffered": len(self.event_buffer),
            "uptime": (datetime.now() - self.metrics.last_activity).total_seconds() if self.metrics.last_activity else 0
        })
    
    async def _process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process incoming messages"""
        if message.message_type == "webhook_event":
            return await self._handle_webhook_event(message)
        elif message.message_type == "polling_request":
            return await self._handle_polling_request(message)
        elif message.message_type == "sla_check":
            return await self._handle_sla_check(message)
        else:
            self.logger.warning(f"Unknown message type: {message.message_type}")
            return None
    
    async def _handle_webhook_event(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle webhook event message"""
        event_data = message.payload.get("event_data", {})
        
        event = Event(
            id=event_data.get('id', f"msg_{message.id}"),
            timestamp=datetime.now(),
            event_type=event_data.get('event_type', 'unknown'),
            source='message',
            data=event_data,
            priority=message.priority
        )
        
        await self._add_event_to_buffer(event)
        return None
    
    async def _handle_polling_request(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle polling request message"""
        endpoint = message.payload.get("endpoint", "tickets")
        since_timestamp = message.payload.get("since_timestamp")
        
        # Trigger polling for specific endpoint
        events = await self._poll_endpoint(endpoint, since_timestamp)
        
        response = AgentMessage(
            id=f"polling_result_{datetime.now().isoformat()}",
            timestamp=datetime.now(),
            source_agent=self.agent_name,
            target_topic="event-stream",
            message_type="polling_completed",
            payload={
                "endpoint": endpoint,
                "events_found": len(events),
                "events": [event.__dict__ for event in events]
            }
        )
        
        return response
    
    async def _handle_sla_check(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle SLA check request"""
        ticket_id = message.payload.get("ticket_id")
        
        if not ticket_id:
            return None
        
        sla_breach = await self._check_ticket_sla(ticket_id)
        
        if sla_breach:
            response = AgentMessage(
                id=f"sla_breach_{datetime.now().isoformat()}",
                timestamp=datetime.now(),
                source_agent=self.agent_name,
                target_topic="event-stream",
                message_type="sla_breach_detected",
                payload={"sla_breach": sla_breach.__dict__},
                priority=1  # High priority for SLA breaches
            )
            
            return response
        
        return None
    
    async def _long_polling_loop(self):
        """Long polling loop for real-time updates"""
        while self.is_running:
            try:
                # Poll for ticket updates
                ticket_events = await self._poll_endpoint("tickets", self.last_poll_timestamp.isoformat())
                
                # Poll for task updates
                task_events = await self._poll_endpoint("tasks", self.last_poll_timestamp.isoformat())
                
                # Process events
                all_events = ticket_events + task_events
                for event in all_events:
                    await self._add_event_to_buffer(event)
                
                if all_events:
                    self.logger.info(f"Polled {len(all_events)} events")
                
                self.last_poll_timestamp = datetime.now()
                
            except Exception as e:
                self.logger.error(f"Error in long polling: {e}")
            
            await asyncio.sleep(self.polling_interval)
    
    async def _sla_monitoring_loop(self):
        """SLA monitoring loop"""
        while self.is_running:
            try:
                # Check SLAs for all monitored tickets
                sla_breaches = await self._check_all_slas()
                
                # Publish SLA breach events
                for breach in sla_breaches:
                    await self._publish_message(AgentMessage(
                        id=f"sla_breach_{breach.ticket_id}_{datetime.now().isoformat()}",
                        timestamp=datetime.now(),
                        source_agent=self.agent_name,
                        target_topic="event-stream",
                        message_type="sla_breach_detected",
                        payload={"sla_breach": breach.__dict__},
                        priority=1
                    ))
                
                if sla_breaches:
                    self.logger.warning(f"Detected {len(sla_breaches)} SLA breaches")
                
            except Exception as e:
                self.logger.error(f"Error in SLA monitoring: {e}")
            
            # Check SLAs every minute
            await asyncio.sleep(60)
    
    async def _event_processing_loop(self):
        """Event processing loop with partitioning"""
        while self.is_running:
            try:
                # Process events from buffer
                events_to_process = []
                
                # Get events from buffer (up to batch size)
                batch_size = 100
                for _ in range(min(batch_size, len(self.event_buffer))):
                    if self.event_buffer:
                        events_to_process.append(self.event_buffer.popleft())
                
                if events_to_process:
                    # Distribute events to partitions
                    await self._distribute_events_to_partitions(events_to_process)
                    
                    # Process partitions in parallel
                    await self._process_partitions()
                
            except Exception as e:
                self.logger.error(f"Error in event processing: {e}")
            
            await asyncio.sleep(1)
    
    async def _poll_endpoint(self, endpoint: str, since_timestamp: str) -> List[Event]:
        """Poll SuperOps endpoint for updates"""
        try:
            # Mock polling implementation - replace with actual SuperOps API calls
            events = await self._get_mock_events(endpoint, since_timestamp)
            return events
            
        except Exception as e:
            self.logger.error(f"Error polling {endpoint}: {e}")
            return []
    
    async def _get_mock_events(self, endpoint: str, since_timestamp: str) -> List[Event]:
        """Generate mock events for testing"""
        events = []
        
        if endpoint == "tickets":
            # Mock ticket events
            events.append(Event(
                id=f"ticket_event_{datetime.now().isoformat()}",
                timestamp=datetime.now(),
                event_type="ticket_status_changed",
                source="polling",
                data={
                    "ticket_id": "TKT-001",
                    "old_status": "open",
                    "new_status": "in_progress",
                    "assignee": "tech1@example.com"
                },
                priority=3
            ))
        
        elif endpoint == "tasks":
            # Mock task events
            events.append(Event(
                id=f"task_event_{datetime.now().isoformat()}",
                timestamp=datetime.now(),
                event_type="task_completed",
                source="polling",
                data={
                    "task_id": "TASK-001",
                    "status": "completed",
                    "completion_time": datetime.now().isoformat()
                },
                priority=4
            ))
        
        return events
    
    async def _add_event_to_buffer(self, event: Event):
        """Add event to buffer with deduplication"""
        # Check for duplicates
        if event.id in self.processed_events:
            return
        
        # Add to buffer
        self.event_buffer.append(event)
        self.processed_events.add(event.id)
        
        # Clean up old processed events (keep last 10000)
        if len(self.processed_events) > 10000:
            # Remove oldest 1000 entries
            old_events = list(self.processed_events)[:1000]
            for old_event in old_events:
                self.processed_events.discard(old_event)
    
    async def _distribute_events_to_partitions(self, events: List[Event]):
        """Distribute events to partitions for parallel processing"""
        for event in events:
            # Use hash of event ID to determine partition
            partition_index = hash(event.id) % self.partition_count
            self.event_partitions[partition_index].append(event)
    
    async def _process_partitions(self):
        """Process all partitions in parallel"""
        tasks = []
        
        for i, partition in enumerate(self.event_partitions):
            if partition:
                task = asyncio.create_task(self._process_partition(i, partition))
                tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _process_partition(self, partition_index: int, partition: deque):
        """Process events in a specific partition"""
        while partition:
            event = partition.popleft()
            
            try:
                # Process event
                await self._process_event(event)
                
                # Mark as processed
                event.processed = True
                
            except Exception as e:
                self.logger.error(f"Error processing event {event.id}: {e}")
    
    async def _process_event(self, event: Event):
        """Process individual event"""
        # Update monitored tickets if ticket event
        if event.event_type.startswith("ticket_"):
            await self._update_monitored_ticket(event)
        
        # Check for SLA implications
        if event.event_type in ["ticket_created", "ticket_status_changed"]:
            await self._check_event_sla_impact(event)
        
        # Publish processed event
        await self._publish_message(AgentMessage(
            id=f"processed_{event.id}",
            timestamp=datetime.now(),
            source_agent=self.agent_name,
            target_topic="event-stream",
            message_type="event_processed",
            payload={
                "original_event": event.__dict__,
                "processing_timestamp": datetime.now().isoformat()
            },
            priority=event.priority
        ))
    
    async def _update_monitored_ticket(self, event: Event):
        """Update monitored ticket information"""
        ticket_data = event.data
        ticket_id = ticket_data.get("ticket_id")
        
        if not ticket_id:
            return
        
        # Update or add to monitored tickets
        if ticket_id not in self.monitored_tickets:
            self.monitored_tickets[ticket_id] = {
                "created_at": datetime.now(),
                "priority": ticket_data.get("priority", "medium"),
                "status": ticket_data.get("status", "open"),
                "last_updated": datetime.now()
            }
        else:
            self.monitored_tickets[ticket_id].update({
                "status": ticket_data.get("new_status", ticket_data.get("status")),
                "last_updated": datetime.now()
            })
    
    async def _check_event_sla_impact(self, event: Event):
        """Check if event has SLA implications"""
        ticket_data = event.data
        ticket_id = ticket_data.get("ticket_id")
        
        if not ticket_id:
            return
        
        # Check SLA for this ticket
        sla_breach = await self._check_ticket_sla(ticket_id)
        
        if sla_breach:
            # Publish SLA breach event
            await self._publish_message(AgentMessage(
                id=f"sla_breach_{ticket_id}_{datetime.now().isoformat()}",
                timestamp=datetime.now(),
                source_agent=self.agent_name,
                target_topic="event-stream",
                message_type="sla_breach_detected",
                payload={"sla_breach": sla_breach.__dict__},
                priority=1
            ))
    
    async def _check_all_slas(self) -> List[SLABreach]:
        """Check SLAs for all monitored tickets"""
        breaches = []
        
        for ticket_id in list(self.monitored_tickets.keys()):
            breach = await self._check_ticket_sla(ticket_id)
            if breach:
                breaches.append(breach)
        
        return breaches
    
    async def _check_ticket_sla(self, ticket_id: str) -> Optional[SLABreach]:
        """Check SLA for specific ticket"""
        if ticket_id not in self.monitored_tickets:
            return None
        
        ticket = self.monitored_tickets[ticket_id]
        priority = ticket.get("priority", "medium")
        status = ticket.get("status", "open")
        created_at = ticket.get("created_at", datetime.now())
        
        # Skip closed/resolved tickets
        if status in ["closed", "resolved"]:
            return None
        
        # Get SLA configuration
        sla_config = self.sla_configs.get(priority)
        if not sla_config:
            return None
        
        # Calculate time elapsed
        time_elapsed = (datetime.now() - created_at).total_seconds() / 3600  # hours
        
        # Check response time SLA
        response_sla = sla_config["response_time"]
        if time_elapsed > response_sla and status == "open":
            return SLABreach(
                ticket_id=ticket_id,
                sla_type="response",
                breach_time=created_at + timedelta(hours=response_sla),
                time_remaining=response_sla - time_elapsed,
                severity="breached" if time_elapsed > response_sla else "warning"
            )
        
        # Check resolution time SLA
        resolution_sla = sla_config["resolution_time"]
        if time_elapsed > resolution_sla * 0.8:  # Warning at 80%
            return SLABreach(
                ticket_id=ticket_id,
                sla_type="resolution",
                breach_time=created_at + timedelta(hours=resolution_sla),
                time_remaining=resolution_sla - time_elapsed,
                severity="breached" if time_elapsed > resolution_sla else "warning"
            )
        
        return None
    
    def _calculate_event_priority(self, event_data: Dict) -> int:
        """Calculate event priority based on event data"""
        event_type = event_data.get("event_type", "")
        
        # High priority events
        if any(keyword in event_type for keyword in ["sla_breach", "critical", "urgent"]):
            return 1
        
        # Medium priority events
        if any(keyword in event_type for keyword in ["ticket_created", "status_changed"]):
            return 3
        
        # Low priority events
        return 5
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        return {
            "monitored_tickets": len(self.monitored_tickets),
            "events_buffered": len(self.event_buffer),
            "processed_events": len(self.processed_events),
            "partition_sizes": [len(partition) for partition in self.event_partitions],
            "last_poll_timestamp": self.last_poll_timestamp.isoformat(),
            "sla_configs": len(self.sla_configs)
        }