"""
SLA Monitor Subagent

Monitors SLA compliance for service requests and alerts the main agent when breaches occur.
This subagent continuously monitors ticket SLA status and triggers alerts for breaches.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from .base_subagent import BaseSubagent, AgentMessage, AgentMetrics
from ..config import AgentConfig
from ...tools.sla import (
    SLACalculatorTool,
    BreachDetectorTool,
    EscalationManagerTool,
    SLADataAccess,
    detect_sla_breaches,
    predict_sla_breaches,
    analyze_ticket_sla_risk,
    execute_sla_escalation,
    notify_sla_breach,
    escalate_ticket_priority
)
from ...clients.sla_superops_client import SLASuperOpsClient
from ...utils.logger import get_logger


@dataclass
class SLAAlert:
    """SLA breach alert structure"""
    ticket_id: str
    alert_type: str  # 'breach', 'warning', 'critical'
    severity: str    # 'low', 'medium', 'high', 'critical'
    time_remaining: int  # minutes until breach (negative if already breached)
    breach_duration: int  # minutes since breach (0 if not breached)
    customer_impact: str
    escalation_required: bool
    timestamp: datetime


class SLAMonitorAgent(BaseSubagent):
    """
    SLA Monitor Subagent
    
    Responsibilities:
    - Monitor active tickets for SLA compliance
    - Detect imminent and actual SLA breaches
    - Generate alerts for the main IT technician agent
    - Track SLA performance metrics
    - Coordinate escalations when needed
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config, "SLAMonitor")
        
        # SLA-specific components
        self.superops_client = SLASuperOpsClient(config)
        self.sla_data_access = None
        self.sla_calculator = SLACalculatorTool()
        self.breach_detector = None
        self.escalation_manager = None
        
        # Monitoring configuration
        self.monitoring_interval = 60  # Check every minute
        self.warning_threshold = 30    # Alert 30 minutes before breach
        self.critical_threshold = 10   # Critical alert 10 minutes before breach
        
        # Active monitoring state
        self.monitored_tickets = {}
        self.active_alerts = {}
        self.sla_policies = {}
        
        # Performance tracking
        self.breach_count = 0
        self.alerts_sent = 0
        self.escalations_triggered = 0
        
    def _get_worker_count(self) -> int:
        """Get optimal worker count for SLA monitoring"""
        return 2  # One for monitoring, one for alert processing
    
    async def _initialize_agent(self):
        """Initialize SLA monitoring components"""
        try:
            self.logger.info("Initializing SLA Monitor Agent")
            
            # Initialize data access
            self.sla_data_access = SLADataAccess(self.config, self.superops_client)
            await self.sla_data_access.initialize()
            
            # Initialize tools
            self.breach_detector = BreachDetectorTool(self.sla_data_access, None)
            self.escalation_manager = EscalationManagerTool(self.sla_data_access, self.superops_client)
            
            # Subscribe to relevant topics
            await self.subscribe_to_topic("ticket.created", self._handle_ticket_created)
            await self.subscribe_to_topic("ticket.updated", self._handle_ticket_updated)
            await self.subscribe_to_topic("ticket.assigned", self._handle_ticket_assigned)
            await self.subscribe_to_topic("sla.check_request", self._handle_sla_check_request)
            
            # Register as publisher for alerts
            await self.publish_to_topic("sla.breach_alert")
            await self.publish_to_topic("sla.warning_alert")
            await self.publish_to_topic("sla.escalation_required")
            
            # Load SLA policies
            await self._load_sla_policies()
            
            # Start monitoring loop
            asyncio.create_task(self._monitoring_loop())
            
            self.logger.info("SLA Monitor Agent initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize SLA Monitor Agent: {e}")
            raise
    
    async def _cleanup_agent(self):
        """Cleanup SLA monitoring resources"""
        self.logger.info("Cleaning up SLA Monitor Agent")
        # Any cleanup needed for SLA monitoring
    
    async def _process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process incoming messages"""
        try:
            handler = self.message_handlers.get(message.target_topic)
            if handler:
                return await handler(message)
            
            # Default message processing
            if message.message_type == "ticket_event":
                return await self._process_ticket_event(message)
            elif message.message_type == "sla_check":
                return await self._process_sla_check(message)
            elif message.message_type == "escalation_request":
                return await self._process_escalation_request(message)
            
            self.logger.warning(f"Unknown message type: {message.message_type}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            raise
    
    async def _monitoring_loop(self):
        """Main SLA monitoring loop"""
        self.logger.info("Starting SLA monitoring loop")
        
        while self.is_running:
            try:
                await self._check_all_active_tickets()
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)  # Brief pause before retrying
    
    async def _check_all_active_tickets(self):
        """Check SLA status for all active tickets"""
        try:
            # Get all active tickets
            active_tickets = await self.sla_data_access.get_active_tickets()
            
            for ticket in active_tickets:
                await self._check_ticket_sla(ticket)
                
        except Exception as e:
            self.logger.error(f"Error checking active tickets: {e}")
    
    async def _check_ticket_sla(self, ticket_data: Dict[str, Any]):
        """Check SLA status for a specific ticket"""
        try:
            ticket_id = ticket_data.get('id')
            priority = ticket_data.get('priority', 'medium')
            
            # Get SLA policy for this ticket
            sla_policy = await self._get_sla_policy(priority)
            if not sla_policy:
                return
            
            # Calculate current SLA status
            sla_status = self.sla_calculator.calculate_sla_status(ticket_data, sla_policy)
            
            # Check for breaches or warnings
            alert = await self._evaluate_sla_status(ticket_data, sla_status)
            
            if alert:
                await self._send_sla_alert(alert)
                
        except Exception as e:
            self.logger.error(f"Error checking SLA for ticket {ticket_data.get('id')}: {e}")
    
    async def _evaluate_sla_status(self, ticket_data: Dict[str, Any], sla_status: Dict[str, Any]) -> Optional[SLAAlert]:
        """Evaluate SLA status and determine if alerts are needed"""
        ticket_id = ticket_data.get('id')
        time_remaining = sla_status.get('time_remaining_minutes', 0)
        is_breached = sla_status.get('is_breached', False)
        breach_duration = sla_status.get('breach_duration_minutes', 0)
        
        # Skip if already alerted recently
        if ticket_id in self.active_alerts:
            last_alert = self.active_alerts[ticket_id]
            if (datetime.now() - last_alert.timestamp).seconds < 300:  # 5 minute cooldown
                return None
        
        alert_type = None
        severity = None
        escalation_required = False
        
        if is_breached:
            alert_type = 'breach'
            severity = 'critical' if breach_duration > 60 else 'high'
            escalation_required = True
            self.breach_count += 1
            
        elif time_remaining <= self.critical_threshold:
            alert_type = 'critical'
            severity = 'critical'
            escalation_required = True
            
        elif time_remaining <= self.warning_threshold:
            alert_type = 'warning'
            severity = 'medium'
            
        if alert_type:
            alert = SLAAlert(
                ticket_id=ticket_id,
                alert_type=alert_type,
                severity=severity,
                time_remaining=time_remaining,
                breach_duration=breach_duration,
                customer_impact=self._assess_customer_impact(ticket_data),
                escalation_required=escalation_required,
                timestamp=datetime.now()
            )
            
            # Cache the alert
            self.active_alerts[ticket_id] = alert
            
            return alert
        
        return None
    
    def _assess_customer_impact(self, ticket_data: Dict[str, Any]) -> str:
        """Assess customer impact level"""
        priority = ticket_data.get('priority', 'medium').lower()
        customer_tier = ticket_data.get('customer', {}).get('tier', 'standard').lower()
        
        if priority == 'critical' or customer_tier == 'premium':
            return 'high'
        elif priority == 'high' or customer_tier == 'business':
            return 'medium'
        else:
            return 'low'
    
    async def _send_sla_alert(self, alert: SLAAlert):
        """Send SLA alert to the main agent"""
        try:
            # Determine target topic based on alert type
            if alert.alert_type == 'breach':
                topic = "sla.breach_alert"
            elif alert.alert_type == 'critical':
                topic = "sla.critical_alert"
            else:
                topic = "sla.warning_alert"
            
            # Create alert message
            alert_message = AgentMessage(
                id=f"sla_alert_{alert.ticket_id}_{int(datetime.now().timestamp())}",
                timestamp=datetime.now(),
                source_agent=self.agent_name,
                target_topic=topic,
                message_type="sla_alert",
                payload={
                    "alert": {
                        "ticket_id": alert.ticket_id,
                        "alert_type": alert.alert_type,
                        "severity": alert.severity,
                        "time_remaining": alert.time_remaining,
                        "breach_duration": alert.breach_duration,
                        "customer_impact": alert.customer_impact,
                        "escalation_required": alert.escalation_required,
                        "timestamp": alert.timestamp.isoformat()
                    },
                    "recommended_actions": self._get_recommended_actions(alert)
                },
                priority=1 if alert.severity == 'critical' else 3
            )
            
            await self._publish_message(alert_message)
            self.alerts_sent += 1
            
            # Trigger escalation if required
            if alert.escalation_required:
                await self._trigger_escalation(alert)
            
            self.logger.info(f"SLA alert sent for ticket {alert.ticket_id}: {alert.alert_type}")
            
        except Exception as e:
            self.logger.error(f"Error sending SLA alert: {e}")
    
    def _get_recommended_actions(self, alert: SLAAlert) -> List[str]:
        """Get recommended actions based on alert type"""
        actions = []
        
        if alert.alert_type == 'breach':
            actions.extend([
                "Immediately escalate to senior technician",
                "Notify customer of delay",
                "Prioritize ticket resolution",
                "Document breach reason"
            ])
        elif alert.alert_type == 'critical':
            actions.extend([
                "Assign to available technician immediately",
                "Prepare escalation if not resolved soon",
                "Review ticket complexity"
            ])
        elif alert.alert_type == 'warning':
            actions.extend([
                "Check ticket assignment status",
                "Ensure technician is aware of deadline",
                "Review progress and blockers"
            ])
        
        if alert.customer_impact == 'high':
            actions.append("Provide proactive customer communication")
        
        return actions
    
    async def _trigger_escalation(self, alert: SLAAlert):
        """Trigger escalation process for SLA breach"""
        try:
            escalation_data = {
                "ticket_id": alert.ticket_id,
                "escalation_reason": f"SLA {alert.alert_type}",
                "severity": alert.severity,
                "customer_impact": alert.customer_impact,
                "breach_duration": alert.breach_duration
            }
            
            # Execute escalation through escalation manager
            result = await self.escalation_manager.execute_escalation(escalation_data)
            
            if result.get('success'):
                self.escalations_triggered += 1
                
                # Send escalation notification
                escalation_message = AgentMessage(
                    id=f"escalation_{alert.ticket_id}_{int(datetime.now().timestamp())}",
                    timestamp=datetime.now(),
                    source_agent=self.agent_name,
                    target_topic="sla.escalation_triggered",
                    message_type="escalation_notification",
                    payload={
                        "ticket_id": alert.ticket_id,
                        "escalation_result": result,
                        "alert_details": alert.__dict__
                    },
                    priority=1
                )
                
                await self._publish_message(escalation_message)
                
            self.logger.info(f"Escalation triggered for ticket {alert.ticket_id}")
            
        except Exception as e:
            self.logger.error(f"Error triggering escalation: {e}")
    
    async def _load_sla_policies(self):
        """Load SLA policies from data access"""
        try:
            policies = await self.sla_data_access.get_all_sla_policies()
            for policy in policies:
                self.sla_policies[policy.get('priority')] = policy
            
            self.logger.info(f"Loaded {len(self.sla_policies)} SLA policies")
            
        except Exception as e:
            self.logger.error(f"Error loading SLA policies: {e}")
    
    async def _get_sla_policy(self, priority: str) -> Optional[Dict[str, Any]]:
        """Get SLA policy for given priority"""
        return self.sla_policies.get(priority.lower())
    
    # Message handlers
    async def _handle_ticket_created(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle new ticket creation"""
        ticket_data = message.payload.get('ticket')
        if ticket_data:
            await self._check_ticket_sla(ticket_data)
        return None
    
    async def _handle_ticket_updated(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle ticket updates"""
        ticket_data = message.payload.get('ticket')
        if ticket_data:
            await self._check_ticket_sla(ticket_data)
        return None
    
    async def _handle_ticket_assigned(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle ticket assignment"""
        ticket_data = message.payload.get('ticket')
        if ticket_data:
            # Clear any existing alerts since ticket is now assigned
            ticket_id = ticket_data.get('id')
            if ticket_id in self.active_alerts:
                del self.active_alerts[ticket_id]
            
            await self._check_ticket_sla(ticket_data)
        return None
    
    async def _handle_sla_check_request(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle manual SLA check requests"""
        ticket_id = message.payload.get('ticket_id')
        if ticket_id:
            ticket_data = await self.sla_data_access.get_ticket_by_id(ticket_id)
            if ticket_data:
                await self._check_ticket_sla(ticket_data)
        return None
    
    async def _process_ticket_event(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process general ticket events"""
        event_type = message.payload.get('event_type')
        ticket_data = message.payload.get('ticket')
        
        if ticket_data:
            await self._check_ticket_sla(ticket_data)
        
        return None
    
    async def _process_sla_check(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process SLA check requests"""
        request_type = message.payload.get('request_type', 'single_ticket')
        
        if request_type == 'all_tickets':
            await self._check_all_active_tickets()
        elif request_type == 'single_ticket':
            ticket_id = message.payload.get('ticket_id')
            if ticket_id:
                ticket_data = await self.sla_data_access.get_ticket_by_id(ticket_id)
                if ticket_data:
                    await self._check_ticket_sla(ticket_data)
        
        return None
    
    async def _process_escalation_request(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process escalation requests"""
        ticket_id = message.payload.get('ticket_id')
        escalation_reason = message.payload.get('reason', 'Manual escalation')
        
        if ticket_id:
            # Create manual escalation alert
            alert = SLAAlert(
                ticket_id=ticket_id,
                alert_type='escalation',
                severity='high',
                time_remaining=0,
                breach_duration=0,
                customer_impact='medium',
                escalation_required=True,
                timestamp=datetime.now()
            )
            
            await self._trigger_escalation(alert)
        
        return None
    
    def get_sla_metrics(self) -> Dict[str, Any]:
        """Get SLA monitoring metrics"""
        base_metrics = self.get_metrics()
        
        sla_specific_metrics = {
            "sla_monitoring": {
                "monitored_tickets": len(self.monitored_tickets),
                "active_alerts": len(self.active_alerts),
                "breach_count": self.breach_count,
                "alerts_sent": self.alerts_sent,
                "escalations_triggered": self.escalations_triggered,
                "sla_policies_loaded": len(self.sla_policies),
                "monitoring_interval_seconds": self.monitoring_interval
            }
        }
        
        base_metrics.update(sla_specific_metrics)
        return base_metrics
    
    async def get_current_alerts(self) -> List[Dict[str, Any]]:
        """Get current active SLA alerts"""
        alerts = []
        for ticket_id, alert in self.active_alerts.items():
            alerts.append({
                "ticket_id": alert.ticket_id,
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "time_remaining": alert.time_remaining,
                "breach_duration": alert.breach_duration,
                "customer_impact": alert.customer_impact,
                "escalation_required": alert.escalation_required,
                "timestamp": alert.timestamp.isoformat()
            })
        
        return alerts
    
    async def force_sla_check(self, ticket_id: Optional[str] = None):
        """Force an immediate SLA check"""
        if ticket_id:
            ticket_data = await self.sla_data_access.get_ticket_by_id(ticket_id)
            if ticket_data:
                await self._check_ticket_sla(ticket_data)
        else:
            await self._check_all_active_tickets()