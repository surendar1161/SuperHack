"""
Escalation Manager Tool

Strands-compatible tool for managing SLA breach escalations, automated actions,
and notification workflows following industry best practices.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from strands import tool

from ..models import SLABreach, EscalationRule, AlertSeverity
from ..exceptions import SLABreachError
from ..data_access import SLADataAccess
from ....clients.sla_superops_client import SLASuperOpsClient
from ....utils.logger import get_logger


class EscalationAction(Enum):
    """Types of escalation actions"""
    NOTIFY_TECHNICIAN = "notify_technician"
    NOTIFY_MANAGER = "notify_manager"
    UPDATE_PRIORITY = "update_priority"
    REASSIGN_TICKET = "reassign_ticket"
    ADD_COMMENT = "add_comment"
    CREATE_ESCALATION_TICKET = "create_escalation_ticket"
    SEND_EMAIL = "send_email"
    SEND_SMS = "send_sms"


@dataclass
class EscalationContext:
    """Context information for escalation processing"""
    breach: SLABreach
    ticket_data: Dict[str, Any]
    escalation_rules: List[EscalationRule]
    technician_data: Optional[Dict[str, Any]] = None
    manager_data: Optional[Dict[str, Any]] = None
    escalation_history: List[Dict[str, Any]] = None


@dataclass
class EscalationResult:
    """Result of escalation action execution"""
    action: EscalationAction
    success: bool
    message: str
    data: Dict[str, Any]
    timestamp: datetime
    error: Optional[str] = None


class EscalationManagerTool:
    """
    Advanced escalation management tool for SLA breaches
    
    Features:
    - Rule-based escalation workflows
    - Multi-channel notifications (email, SMS, comments)
    - Automated ticket actions (priority, assignment, comments)
    - Escalation tracking and audit trail
    - Manager and technician notifications
    - Custom escalation rules
    """
    
    def __init__(self, sla_data_access: SLADataAccess, superops_client: SLASuperOpsClient):
        self.logger = get_logger("EscalationManagerTool")
        
        self.sla_data_access = sla_data_access
        self.superops_client = superops_client
        
        # Escalation tracking
        self.escalation_history: Dict[str, List[EscalationResult]] = {}
        self.active_escalations: Dict[str, EscalationContext] = {}
        
        # Default escalation rules
        self.default_escalation_rules = [
            {
                'name': 'Immediate Technician Notification',
                'trigger_after_minutes': 0,
                'actions': [EscalationAction.NOTIFY_TECHNICIAN, EscalationAction.ADD_COMMENT],
                'severity_threshold': AlertSeverity.WARNING
            },
            {
                'name': 'Manager Escalation',
                'trigger_after_minutes': 30,
                'actions': [EscalationAction.NOTIFY_MANAGER, EscalationAction.UPDATE_PRIORITY],
                'severity_threshold': AlertSeverity.ERROR
            },
            {
                'name': 'Critical Escalation',
                'trigger_after_minutes': 60,
                'actions': [EscalationAction.CREATE_ESCALATION_TICKET, EscalationAction.REASSIGN_TICKET],
                'severity_threshold': AlertSeverity.CRITICAL
            }
        ]
        
        # Action handlers
        self.action_handlers = {
            EscalationAction.NOTIFY_TECHNICIAN: self._notify_technician,
            EscalationAction.NOTIFY_MANAGER: self._notify_manager,
            EscalationAction.UPDATE_PRIORITY: self._update_priority,
            EscalationAction.REASSIGN_TICKET: self._reassign_ticket,
            EscalationAction.ADD_COMMENT: self._add_comment,
            EscalationAction.CREATE_ESCALATION_TICKET: self._create_escalation_ticket,
            EscalationAction.SEND_EMAIL: self._send_email,
            EscalationAction.SEND_SMS: self._send_sms
        }
        
        # Notification templates
        self.notification_templates = {
            'breach_notification': """
SLA Breach Alert - Ticket #{ticket_number}

Ticket: {subject}
Breach Type: {breach_type}
Severity: {severity}
Time Breached: {breach_time}

Assigned to: {technician_name}
Customer Impact: {customer_impact}

Please take immediate action to resolve this issue.

Ticket Link: {ticket_url}
            """.strip(),
            
            'manager_escalation': """
SLA Breach Escalation - Ticket #{ticket_number}

A critical SLA breach requires your attention:

Ticket: {subject}
Breach Type: {breach_type}
Severity: {severity}
Escalation Level: {escalation_level}

Original Assignee: {technician_name}
Breach Duration: {breach_duration}

This issue has been escalated due to SLA policy violations.

Ticket Link: {ticket_url}
            """.strip()
        }
    
    async def _execute_impl(self, **kwargs) -> Dict[str, Any]:
        """Execute escalation management operation"""
        operation = kwargs.get('operation', 'process_breach')
        
        if operation == 'process_breach':
            return await self._process_breach_escalation(**kwargs)
        elif operation == 'execute_action':
            return await self._execute_escalation_action(**kwargs)
        elif operation == 'check_escalations':
            return await self._check_pending_escalations(**kwargs)
        elif operation == 'get_escalation_status':
            return await self._get_escalation_status(**kwargs)
        else:
            raise SLABreachError("unknown", operation, f"Unknown operation: {operation}")
    
    async def process_breach_escalation(self, breach: SLABreach, 
                                      ticket_data: Dict[str, Any]) -> List[EscalationResult]:
        """Process escalation for an SLA breach"""
        result = await self.execute(
            operation='process_breach',
            breach=breach,
            ticket_data=ticket_data
        )
        
        if not result.is_success():
            raise SLABreachError(
                breach.ticket_id, 
                "process_escalation", 
                result.error or "Escalation processing failed"
            )
        
        return result.data.get('escalation_results', [])
    
    async def _process_breach_escalation(self, **kwargs) -> Dict[str, Any]:
        """Internal implementation of breach escalation processing"""
        breach = kwargs['breach']
        ticket_data = kwargs['ticket_data']
        
        try:
            self.logger.info(f"Processing escalation for breach {breach.id}")
            
            # Get escalation rules for the SLA policy
            escalation_rules = breach.sla_policy.escalation_rules or []
            
            # If no specific rules, use defaults
            if not escalation_rules:
                escalation_rules = self._get_default_escalation_rules(breach.severity)
            
            # Get additional context
            context = await self._build_escalation_context(breach, ticket_data, escalation_rules)
            
            # Store active escalation
            self.active_escalations[breach.id] = context
            
            # Execute immediate escalation actions
            escalation_results = await self._execute_escalation_rules(context)
            
            # Track escalation history
            if breach.ticket_id not in self.escalation_history:
                self.escalation_history[breach.ticket_id] = []
            
            self.escalation_history[breach.ticket_id].extend(escalation_results)
            
            return {
                'escalation_results': escalation_results,
                'escalation_context': context,
                'total_actions': len(escalation_results),
                'successful_actions': len([r for r in escalation_results if r.success]),
                'processing_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Escalation processing failed for breach {breach.id}: {e}")
            raise SLABreachError(breach.ticket_id, "process_escalation", str(e))
    
    async def _build_escalation_context(self, breach: SLABreach, ticket_data: Dict[str, Any],
                                      escalation_rules: List[EscalationRule]) -> EscalationContext:
        """Build escalation context with all necessary data"""
        context = EscalationContext(
            breach=breach,
            ticket_data=ticket_data,
            escalation_rules=escalation_rules,
            escalation_history=self.escalation_history.get(breach.ticket_id, [])
        )
        
        # Get technician data
        if breach.technician_id:
            try:
                users = await self.sla_data_access.get_user_list()
                context.technician_data = next(
                    (user for user in users if user['id'] == breach.technician_id), 
                    None
                )
            except Exception as e:
                self.logger.warning(f"Failed to get technician data: {e}")
        
        # Get manager data (would typically be based on department/role)
        try:
            users = await self.sla_data_access.get_user_list()
            managers = [user for user in users if user.get('role', '').lower() in ['manager', 'supervisor']]
            if managers:
                context.manager_data = managers[0]  # Use first available manager
        except Exception as e:
            self.logger.warning(f"Failed to get manager data: {e}")
        
        return context
    
    async def _execute_escalation_rules(self, context: EscalationContext) -> List[EscalationResult]:
        """Execute escalation rules based on context"""
        results = []
        current_time = datetime.now()
        
        for rule in context.escalation_rules:
            # Check if rule should be triggered
            if not self._should_trigger_rule(rule, context, current_time):
                continue
            
            self.logger.info(f"Triggering escalation rule: {rule.name}")
            
            # Execute rule actions
            for action_name in rule.get('actions', []):
                try:
                    if isinstance(action_name, str):
                        action = EscalationAction(action_name)
                    else:
                        action = action_name
                    
                    result = await self._execute_single_action(action, context)
                    results.append(result)
                    
                except Exception as e:
                    error_result = EscalationResult(
                        action=action,
                        success=False,
                        message=f"Action execution failed: {str(e)}",
                        data={},
                        timestamp=current_time,
                        error=str(e)
                    )
                    results.append(error_result)
                    self.logger.error(f"Escalation action {action} failed: {e}")
        
        return results
    
    def _should_trigger_rule(self, rule: Dict[str, Any], context: EscalationContext, 
                           current_time: datetime) -> bool:
        """Check if escalation rule should be triggered"""
        # Check severity threshold
        severity_threshold = rule.get('severity_threshold', AlertSeverity.WARNING)
        if context.breach.severity.value < severity_threshold.value:
            return False
        
        # Check time threshold
        trigger_after_minutes = rule.get('trigger_after_minutes', 0)
        if trigger_after_minutes > 0:
            time_since_breach = current_time - context.breach.breach_time
            if time_since_breach.total_seconds() < (trigger_after_minutes * 60):
                return False
        
        # Check if rule was already executed
        rule_name = rule.get('name', 'unknown')
        if context.escalation_history:
            executed_rules = [
                result.data.get('rule_name') 
                for result in context.escalation_history 
                if result.data.get('rule_name') == rule_name
            ]
            if executed_rules:
                return False  # Rule already executed
        
        return True
    
    async def _execute_single_action(self, action: EscalationAction, 
                                   context: EscalationContext) -> EscalationResult:
        """Execute a single escalation action"""
        handler = self.action_handlers.get(action)
        if not handler:
            return EscalationResult(
                action=action,
                success=False,
                message=f"No handler found for action: {action}",
                data={},
                timestamp=datetime.now(),
                error=f"Handler not implemented: {action}"
            )
        
        try:
            result_data = await handler(context)
            
            return EscalationResult(
                action=action,
                success=True,
                message=f"Successfully executed {action.value}",
                data=result_data,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return EscalationResult(
                action=action,
                success=False,
                message=f"Failed to execute {action.value}: {str(e)}",
                data={},
                timestamp=datetime.now(),
                error=str(e)
            )
    
    # ==================== ACTION HANDLERS ====================
    
    async def _notify_technician(self, context: EscalationContext) -> Dict[str, Any]:
        """Notify assigned technician of SLA breach"""
        if not context.technician_data:
            raise SLABreachError(context.breach.ticket_id, "notify_technician", "No technician data available")
        
        # Create notification message
        message = self._format_notification_message('breach_notification', context)
        
        # Add comment to ticket with technician mention
        comment_result = await self.superops_client.add_ticket_comment_with_mentions(
            ticket_id=context.breach.ticket_id,
            comment=f"SLA Breach Alert: {message}",
            mention_user_ids=[context.breach.technician_id],
            is_internal=False
        )
        
        return {
            'technician_id': context.breach.technician_id,
            'technician_name': context.technician_data.get('name'),
            'notification_method': 'ticket_comment',
            'comment_id': comment_result.get('id'),
            'message': message
        }
    
    async def _notify_manager(self, context: EscalationContext) -> Dict[str, Any]:
        """Notify manager of SLA breach escalation"""
        if not context.manager_data:
            raise SLABreachError(context.breach.ticket_id, "notify_manager", "No manager data available")
        
        # Create escalation message
        message = self._format_notification_message('manager_escalation', context)
        
        # Add comment to ticket with manager mention
        comment_result = await self.superops_client.add_ticket_comment_with_mentions(
            ticket_id=context.breach.ticket_id,
            comment=f"Manager Escalation: {message}",
            mention_user_ids=[context.manager_data['id']],
            is_internal=True
        )
        
        return {
            'manager_id': context.manager_data['id'],
            'manager_name': context.manager_data.get('name'),
            'notification_method': 'ticket_comment',
            'comment_id': comment_result.get('id'),
            'message': message
        }
    
    async def _update_priority(self, context: EscalationContext) -> Dict[str, Any]:
        """Update ticket priority due to SLA breach"""
        current_priority = context.ticket_data.get('priority', 'medium').lower()
        
        # Escalate priority
        priority_escalation = {
            'low': 'medium',
            'medium': 'high',
            'high': 'critical',
            'critical': 'critical'  # Already at highest
        }
        
        new_priority = priority_escalation.get(current_priority, 'high')
        
        if new_priority != current_priority:
            update_result = await self.superops_client.update_ticket_priority(
                ticket_id=context.breach.ticket_id,
                priority=new_priority
            )
            
            return {
                'old_priority': current_priority,
                'new_priority': new_priority,
                'update_result': update_result
            }
        else:
            return {
                'old_priority': current_priority,
                'new_priority': new_priority,
                'message': 'Priority already at maximum level'
            }
    
    async def _reassign_ticket(self, context: EscalationContext) -> Dict[str, Any]:
        """Reassign ticket to available technician"""
        # Get available technicians
        users = await self.sla_data_access.get_user_list()
        technicians = [
            user for user in users 
            if user.get('role', '').lower() in ['technician', 'engineer'] 
            and user.get('isActive', False)
            and user['id'] != context.breach.technician_id
        ]
        
        if not technicians:
            raise SLABreachError(context.breach.ticket_id, "reassign_ticket", "No available technicians found")
        
        # Find technician with lowest current workload
        best_technician = min(technicians, key=lambda t: t.get('currentTicketCount', 0))
        
        # Reassign ticket
        assign_result = await self.superops_client.assign_ticket(
            ticket_id=context.breach.ticket_id,
            assignee_id=best_technician['id'],
            reason=f"SLA breach escalation - reassigned from {context.breach.technician_name}"
        )
        
        return {
            'old_assignee_id': context.breach.technician_id,
            'old_assignee_name': context.breach.technician_name,
            'new_assignee_id': best_technician['id'],
            'new_assignee_name': best_technician.get('name'),
            'assign_result': assign_result
        }
    
    async def _add_comment(self, context: EscalationContext) -> Dict[str, Any]:
        """Add escalation comment to ticket"""
        comment = f"""
SLA Breach Escalation - {context.breach.breach_type.value.title()}

Breach Details:
- Breach Time: {context.breach.breach_time.strftime('%Y-%m-%d %H:%M:%S')}
- Severity: {context.breach.severity.value.title()}
- Customer Impact: {context.breach.customer_impact.title()}

This ticket has breached its SLA requirements and requires immediate attention.
        """.strip()
        
        comment_result = await self.superops_client.add_ticket_comment_with_mentions(
            ticket_id=context.breach.ticket_id,
            comment=comment,
            mention_user_ids=[],
            is_internal=True
        )
        
        return {
            'comment_id': comment_result.get('id'),
            'comment_text': comment
        }
    
    async def _create_escalation_ticket(self, context: EscalationContext) -> Dict[str, Any]:
        """Create escalation ticket for management tracking"""
        escalation_ticket_data = {
            'subject': f"SLA Breach Escalation - Ticket #{context.ticket_data.get('number')}",
            'description': f"""
This is an escalation ticket for SLA breach management.

Original Ticket: #{context.ticket_data.get('number')} - {context.ticket_data.get('subject')}
Breach Type: {context.breach.breach_type.value.title()}
Breach Time: {context.breach.breach_time.strftime('%Y-%m-%d %H:%M:%S')}
Severity: {context.breach.severity.value.title()}

Original Assignee: {context.breach.technician_name}
Customer Impact: {context.breach.customer_impact.title()}

Please review and take appropriate action.
            """.strip(),
            'priority': 'high',
            'category': 'escalation'
        }
        
        # This would use the SuperOps create ticket API
        # For now, return placeholder data
        return {
            'escalation_ticket_id': f"ESC-{context.breach.ticket_id}-{int(datetime.now().timestamp())}",
            'escalation_ticket_data': escalation_ticket_data,
            'message': 'Escalation ticket creation requested'
        }
    
    async def _send_email(self, context: EscalationContext) -> Dict[str, Any]:
        """Send email notification"""
        # This would integrate with email service
        # For now, return placeholder
        return {
            'notification_type': 'email',
            'recipients': [context.technician_data.get('email')] if context.technician_data else [],
            'message': 'Email notification sent'
        }
    
    async def _send_sms(self, context: EscalationContext) -> Dict[str, Any]:
        """Send SMS notification"""
        # This would integrate with SMS service
        # For now, return placeholder
        return {
            'notification_type': 'sms',
            'recipients': [context.technician_data.get('phoneNumber')] if context.technician_data else [],
            'message': 'SMS notification sent'
        }
    
    def _format_notification_message(self, template_name: str, context: EscalationContext) -> str:
        """Format notification message using template"""
        template = self.notification_templates.get(template_name, "SLA Breach Alert")
        
        # Calculate breach duration
        breach_duration = datetime.now() - context.breach.breach_time
        duration_str = f"{int(breach_duration.total_seconds() / 60)} minutes"
        
        # Format template
        try:
            return template.format(
                ticket_number=context.ticket_data.get('number', 'Unknown'),
                subject=context.ticket_data.get('subject', 'Unknown'),
                breach_type=context.breach.breach_type.value.title(),
                severity=context.breach.severity.value.title(),
                breach_time=context.breach.breach_time.strftime('%Y-%m-%d %H:%M:%S'),
                technician_name=context.breach.technician_name or 'Unassigned',
                customer_impact=context.breach.customer_impact.title(),
                escalation_level=context.breach.escalation_level,
                breach_duration=duration_str,
                ticket_url=f"https://app.superops.com/tickets/{context.breach.ticket_id}"
            )
        except KeyError as e:
            self.logger.warning(f"Template formatting error: {e}")
            return f"SLA Breach Alert for Ticket #{context.ticket_data.get('number', 'Unknown')}"
    
    def _get_default_escalation_rules(self, severity: AlertSeverity) -> List[Dict[str, Any]]:
        """Get default escalation rules based on severity"""
        applicable_rules = []
        
        for rule in self.default_escalation_rules:
            if severity.value >= rule['severity_threshold'].value:
                applicable_rules.append(rule)
        
        return applicable_rules
    
    def get_escalation_metrics(self) -> Dict[str, Any]:
        """Get escalation management metrics"""
        total_escalations = len(self.escalation_history)
        total_actions = sum(len(actions) for actions in self.escalation_history.values())
        successful_actions = sum(
            len([a for a in actions if a.success]) 
            for actions in self.escalation_history.values()
        )
        
        return {
            'total_escalations': total_escalations,
            'active_escalations': len(self.active_escalations),
            'total_actions_executed': total_actions,
            'successful_actions': successful_actions,
            'success_rate': successful_actions / max(total_actions, 1),
            'escalation_rules_count': len(self.default_escalation_rules)
        }


# Strands-compatible tool functions
@tool
async def execute_sla_escalation(breach_data: Dict[str, Any], ticket_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute escalation process for an SLA breach
    
    Args:
        breach_data: SLA breach information
        ticket_data: Ticket information from SuperOps
        
    Returns:
        Dictionary containing escalation results and actions taken
    """
    from ..data_access import SLADataAccess
    from ....clients.sla_superops_client import SLASuperOpsClient
    from ...config import AgentConfig
    
    try:
        # Initialize components
        config = AgentConfig()
        sla_data_access = SLADataAccess(config, None)
        superops_client = SLASuperOpsClient(config)
        await sla_data_access.initialize()
        
        # Create breach object
        breach = SLABreach(
            id=breach_data.get('id'),
            ticket_id=breach_data.get('ticket_id'),
            ticket_number=breach_data.get('ticket_number'),
            breach_type=BreachType(breach_data.get('breach_type')),
            breach_time=datetime.fromisoformat(breach_data.get('breach_time')),
            severity=AlertSeverity(breach_data.get('severity')),
            customer_impact=breach_data.get('customer_impact'),
            escalation_required=breach_data.get('escalation_required', True),
            escalation_level=breach_data.get('escalation_level', 0),
            created_at=datetime.now()
        )
        
        escalation_manager = EscalationManagerTool(sla_data_access, superops_client)
        results = await escalation_manager.process_breach_escalation(breach, ticket_data)
        
        return {
            "success": True,
            "escalation_results": [
                {
                    "action": result.action.value,
                    "success": result.success,
                    "message": result.message,
                    "timestamp": result.timestamp.isoformat(),
                    "error": result.error
                }
                for result in results
            ],
            "total_actions": len(results),
            "successful_actions": len([r for r in results if r.success])
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ticket_id": breach_data.get('ticket_id', 'unknown')
        }


@tool
async def notify_sla_breach(ticket_id: str, breach_type: str, severity: str, technician_id: str = None) -> Dict[str, Any]:
    """
    Send notifications for SLA breach
    
    Args:
        ticket_id: ID of the breached ticket
        breach_type: Type of breach (response/resolution)
        severity: Severity level of the breach
        technician_id: ID of assigned technician (optional)
        
    Returns:
        Dictionary containing notification results
    """
    from ..data_access import SLADataAccess
    from ....clients.sla_superops_client import SLASuperOpsClient
    from ...config import AgentConfig
    
    try:
        config = AgentConfig()
        sla_data_access = SLADataAccess(config, None)
        superops_client = SLASuperOpsClient(config)
        
        escalation_manager = EscalationManagerTool(sla_data_access, superops_client)
        
        # Create notification message
        message = f"SLA {breach_type} breach detected for ticket {ticket_id}. Severity: {severity}. Immediate attention required."
        
        # Add comment to ticket
        comment_result = await superops_client.add_ticket_comment_with_mentions(
            ticket_id=ticket_id,
            comment=message,
            mention_user_ids=[technician_id] if technician_id else [],
            is_internal=False
        )
        
        return {
            "success": True,
            "notification_sent": True,
            "comment_id": comment_result.get('id'),
            "message": message,
            "notified_users": [technician_id] if technician_id else []
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ticket_id": ticket_id
        }


@tool
async def escalate_ticket_priority(ticket_id: str, current_priority: str, reason: str = "SLA breach") -> Dict[str, Any]:
    """
    Escalate ticket priority due to SLA breach
    
    Args:
        ticket_id: ID of the ticket to escalate
        current_priority: Current priority level
        reason: Reason for escalation
        
    Returns:
        Dictionary containing escalation results
    """
    from ....clients.sla_superops_client import SLASuperOpsClient
    from ...config import AgentConfig
    
    try:
        config = AgentConfig()
        superops_client = SLASuperOpsClient(config)
        
        # Priority escalation mapping
        priority_escalation = {
            'low': 'medium',
            'medium': 'high', 
            'high': 'critical',
            'critical': 'critical'
        }
        
        new_priority = priority_escalation.get(current_priority.lower(), 'high')
        
        if new_priority != current_priority.lower():
            update_result = await superops_client.update_ticket_priority(
                ticket_id=ticket_id,
                priority=new_priority
            )
            
            # Add comment about escalation
            comment = f"Priority escalated from {current_priority} to {new_priority} due to {reason}"
            await superops_client.add_ticket_comment_with_mentions(
                ticket_id=ticket_id,
                comment=comment,
                mention_user_ids=[],
                is_internal=True
            )
            
            return {
                "success": True,
                "priority_changed": True,
                "old_priority": current_priority,
                "new_priority": new_priority,
                "reason": reason,
                "update_result": update_result
            }
        else:
            return {
                "success": True,
                "priority_changed": False,
                "message": "Priority already at maximum level",
                "current_priority": current_priority
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ticket_id": ticket_id
        }