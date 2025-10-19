"""
Technician Notification Tool

Strands-compatible tool for notifying technicians about ticket assignments,
updates, and important events through multiple channels.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from strands import tool

from ...utils.logger import get_logger
from ...clients.superops_client import SuperOpsClient


logger = get_logger("TechnicianNotificationTool")


@tool
async def notify_technician_assignment(
    technician_id: str,
    ticket_data: Dict[str, Any],
    assignment_details: Dict[str, Any],
    notification_channels: List[str] = None
) -> Dict[str, Any]:
    """
    Notify technician about new ticket assignment
    
    Args:
        technician_id: ID of the technician to notify
        ticket_data: Ticket information
        assignment_details: Assignment context and details
        notification_channels: List of channels (email, sms, in_app, comment)
        
    Returns:
        Dictionary containing notification results
    """
    try:
        if not notification_channels:
            notification_channels = ['in_app', 'comment']
        
        logger.info(f"Notifying technician {technician_id} about ticket {ticket_data.get('id')}")
        
        # Get technician details
        technician = await _get_technician_details(technician_id)
        if not technician:
            return {
                "success": False,
                "error": f"Technician {technician_id} not found"
            }
        
        # Prepare notification content
        notification_content = _prepare_assignment_notification(ticket_data, assignment_details, technician)
        
        # Send notifications through specified channels
        notification_results = []
        
        for channel in notification_channels:
            try:
                result = await _send_notification(channel, technician, notification_content)
                notification_results.append({
                    "channel": channel,
                    "success": result.get("success", False),
                    "message": result.get("message", ""),
                    "notification_id": result.get("notification_id")
                })
            except Exception as e:
                logger.error(f"Failed to send {channel} notification: {e}")
                notification_results.append({
                    "channel": channel,
                    "success": False,
                    "error": str(e)
                })
        
        successful_notifications = [r for r in notification_results if r["success"]]
        
        return {
            "success": len(successful_notifications) > 0,
            "technician_id": technician_id,
            "ticket_id": ticket_data.get('id'),
            "notification_results": notification_results,
            "successful_channels": len(successful_notifications),
            "total_channels": len(notification_channels),
            "notification_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error notifying technician: {e}")
        return {
            "success": False,
            "error": str(e),
            "technician_id": technician_id,
            "ticket_id": ticket_data.get('id', 'unknown')
        }


@tool
async def notify_sla_alert(
    technician_id: str,
    ticket_data: Dict[str, Any],
    sla_alert: Dict[str, Any],
    urgency_level: str = "high"
) -> Dict[str, Any]:
    """
    Notify technician about SLA alerts and breaches
    
    Args:
        technician_id: ID of the technician to notify
        ticket_data: Ticket information
        sla_alert: SLA alert details
        urgency_level: Urgency of the alert (low, medium, high, critical)
        
    Returns:
        Dictionary containing notification results
    """
    try:
        logger.info(f"Sending SLA alert to technician {technician_id} for ticket {ticket_data.get('id')}")
        
        technician = await _get_technician_details(technician_id)
        if not technician:
            return {
                "success": False,
                "error": f"Technician {technician_id} not found"
            }
        
        # Determine notification channels based on urgency
        channels = _get_channels_for_urgency(urgency_level)
        
        # Prepare SLA alert content
        notification_content = _prepare_sla_alert_notification(ticket_data, sla_alert, urgency_level)
        
        # Send notifications
        notification_results = []
        
        for channel in channels:
            try:
                result = await _send_notification(channel, technician, notification_content)
                notification_results.append({
                    "channel": channel,
                    "success": result.get("success", False),
                    "message": result.get("message", ""),
                    "notification_id": result.get("notification_id")
                })
            except Exception as e:
                logger.error(f"Failed to send {channel} SLA alert: {e}")
                notification_results.append({
                    "channel": channel,
                    "success": False,
                    "error": str(e)
                })
        
        successful_notifications = [r for r in notification_results if r["success"]]
        
        return {
            "success": len(successful_notifications) > 0,
            "alert_type": "sla_alert",
            "urgency_level": urgency_level,
            "technician_id": technician_id,
            "ticket_id": ticket_data.get('id'),
            "notification_results": notification_results,
            "successful_channels": len(successful_notifications),
            "notification_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error sending SLA alert: {e}")
        return {
            "success": False,
            "error": str(e),
            "technician_id": technician_id,
            "ticket_id": ticket_data.get('id', 'unknown')
        }


@tool
async def notify_bottleneck_alert(
    technician_ids: List[str],
    bottleneck_data: Dict[str, Any],
    manager_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Notify technicians and managers about detected bottlenecks
    
    Args:
        technician_ids: List of technician IDs to notify
        bottleneck_data: Bottleneck detection results
        manager_id: Optional manager ID for escalation
        
    Returns:
        Dictionary containing notification results
    """
    try:
        logger.info(f"Sending bottleneck alerts to {len(technician_ids)} technicians")
        
        notification_results = []
        
        # Notify technicians
        for tech_id in technician_ids:
            technician = await _get_technician_details(tech_id)
            if not technician:
                continue
            
            content = _prepare_bottleneck_notification(bottleneck_data, "technician")
            
            # Use medium urgency channels for bottleneck alerts
            channels = ['in_app', 'comment']
            
            for channel in channels:
                try:
                    result = await _send_notification(channel, technician, content)
                    notification_results.append({
                        "recipient_type": "technician",
                        "recipient_id": tech_id,
                        "channel": channel,
                        "success": result.get("success", False),
                        "message": result.get("message", "")
                    })
                except Exception as e:
                    logger.error(f"Failed to send bottleneck alert to {tech_id}: {e}")
                    notification_results.append({
                        "recipient_type": "technician",
                        "recipient_id": tech_id,
                        "channel": channel,
                        "success": False,
                        "error": str(e)
                    })
        
        # Notify manager if provided
        if manager_id:
            manager = await _get_technician_details(manager_id)  # Assuming managers are in same user table
            if manager:
                content = _prepare_bottleneck_notification(bottleneck_data, "manager")
                
                # Use high urgency channels for manager notifications
                channels = ['in_app', 'email']
                
                for channel in channels:
                    try:
                        result = await _send_notification(channel, manager, content)
                        notification_results.append({
                            "recipient_type": "manager",
                            "recipient_id": manager_id,
                            "channel": channel,
                            "success": result.get("success", False),
                            "message": result.get("message", "")
                        })
                    except Exception as e:
                        logger.error(f"Failed to send bottleneck alert to manager {manager_id}: {e}")
                        notification_results.append({
                            "recipient_type": "manager",
                            "recipient_id": manager_id,
                            "channel": channel,
                            "success": False,
                            "error": str(e)
                        })
        
        successful_notifications = [r for r in notification_results if r["success"]]
        
        return {
            "success": len(successful_notifications) > 0,
            "alert_type": "bottleneck_alert",
            "notification_results": notification_results,
            "successful_notifications": len(successful_notifications),
            "total_notifications": len(notification_results),
            "notification_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error sending bottleneck alerts: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def _get_technician_details(technician_id: str) -> Optional[Dict[str, Any]]:
    """Get technician details from SuperOps API"""
    try:
        # This would integrate with SuperOps API
        # For now, return mock data
        mock_technicians = {
            "tech-001": {
                "id": "tech-001",
                "name": "John Doe",
                "email": "john.doe@company.com",
                "phone": "+1-555-0101",
                "role": "technician",
                "preferences": {
                    "email_notifications": True,
                    "sms_notifications": True,
                    "in_app_notifications": True
                }
            },
            "tech-002": {
                "id": "tech-002",
                "name": "Jane Smith", 
                "email": "jane.smith@company.com",
                "phone": "+1-555-0102",
                "role": "senior_technician",
                "preferences": {
                    "email_notifications": True,
                    "sms_notifications": False,
                    "in_app_notifications": True
                }
            },
            "mgr-001": {
                "id": "mgr-001",
                "name": "Mike Johnson",
                "email": "mike.johnson@company.com",
                "phone": "+1-555-0201",
                "role": "manager",
                "preferences": {
                    "email_notifications": True,
                    "sms_notifications": True,
                    "in_app_notifications": True
                }
            }
        }
        
        return mock_technicians.get(technician_id)
        
    except Exception as e:
        logger.error(f"Error getting technician details: {e}")
        return None


def _prepare_assignment_notification(
    ticket_data: Dict[str, Any], 
    assignment_details: Dict[str, Any],
    technician: Dict[str, Any]
) -> Dict[str, Any]:
    """Prepare notification content for ticket assignment"""
    
    priority = ticket_data.get('priority', 'medium').upper()
    ticket_number = ticket_data.get('number', ticket_data.get('id', 'Unknown'))
    
    subject = f"New {priority} Priority Ticket Assigned: #{ticket_number}"
    
    message = f"""
Hello {technician['name']},

You have been assigned a new ticket:

Ticket: #{ticket_number}
Subject: {ticket_data.get('subject', 'No subject')}
Priority: {priority}
Customer: {ticket_data.get('customer', {}).get('name', 'Unknown')}

Assignment Details:
- Match Score: {assignment_details.get('score', 'N/A')}
- Required Skills: {', '.join(assignment_details.get('required_skills', []))}
- Estimated Effort: {assignment_details.get('estimated_effort_hours', 'Unknown')} hours

SLA Requirements:
- Response Time: {assignment_details.get('sla_requirements', {}).get('response_time_minutes', 'N/A')} minutes
- Resolution Time: {assignment_details.get('sla_requirements', {}).get('resolution_time_hours', 'N/A')} hours

Please review and start working on this ticket as soon as possible.

Best regards,
IT Support System
    """.strip()
    
    return {
        "subject": subject,
        "message": message,
        "priority": priority.lower(),
        "ticket_id": ticket_data.get('id'),
        "ticket_number": ticket_number
    }


def _prepare_sla_alert_notification(
    ticket_data: Dict[str, Any],
    sla_alert: Dict[str, Any], 
    urgency_level: str
) -> Dict[str, Any]:
    """Prepare notification content for SLA alerts"""
    
    alert_type = sla_alert.get('alert_type', 'warning').upper()
    ticket_number = ticket_data.get('number', ticket_data.get('id', 'Unknown'))
    time_remaining = sla_alert.get('time_remaining_minutes', 0)
    
    if time_remaining > 0:
        time_msg = f"{time_remaining} minutes remaining"
    else:
        time_msg = f"BREACHED by {abs(time_remaining)} minutes"
    
    subject = f"SLA {alert_type}: Ticket #{ticket_number} - {time_msg}"
    
    message = f"""
URGENT: SLA Alert for Ticket #{ticket_number}

Alert Type: {alert_type}
Ticket: {ticket_data.get('subject', 'No subject')}
Priority: {ticket_data.get('priority', 'medium').upper()}
Customer: {ticket_data.get('customer', {}).get('name', 'Unknown')}

SLA Status:
- Time Remaining: {time_msg}
- Breach Type: {sla_alert.get('breach_type', 'Unknown')}
- Customer Impact: {sla_alert.get('customer_impact', 'Unknown')}

Recommended Actions:
{chr(10).join(f"- {action}" for action in sla_alert.get('recommended_actions', ['Review ticket immediately']))}

Please take immediate action to address this SLA alert.

Best regards,
IT Support System
    """.strip()
    
    return {
        "subject": subject,
        "message": message,
        "priority": "high",
        "alert_type": alert_type.lower(),
        "ticket_id": ticket_data.get('id'),
        "ticket_number": ticket_number
    }


def _prepare_bottleneck_notification(bottleneck_data: Dict[str, Any], recipient_type: str) -> Dict[str, Any]:
    """Prepare notification content for bottleneck alerts"""
    
    bottleneck_type = bottleneck_data.get('bottleneck_type', 'workflow')
    affected_tickets = bottleneck_data.get('affected_tickets', [])
    
    if recipient_type == "manager":
        subject = f"Workflow Bottleneck Detected - {len(affected_tickets)} tickets affected"
        message = f"""
Bottleneck Alert - Manager Notification

A workflow bottleneck has been detected that requires your attention:

Bottleneck Details:
- Type: {bottleneck_type.title()}
- Affected Tickets: {len(affected_tickets)}
- Severity: {bottleneck_data.get('severity', 'medium').upper()}
- Detection Time: {bottleneck_data.get('detection_time', 'Unknown')}

Impact Analysis:
- Average Delay: {bottleneck_data.get('average_delay_hours', 'Unknown')} hours
- SLA Risk: {bottleneck_data.get('sla_risk_level', 'Unknown')}

Recommended Actions:
{chr(10).join(f"- {action}" for action in bottleneck_data.get('recommended_actions', ['Review resource allocation']))}

Please review and take appropriate action to resolve this bottleneck.
        """.strip()
    else:
        subject = f"Workflow Alert - Please review your current tickets"
        message = f"""
Workflow Optimization Alert

Our system has detected a potential workflow bottleneck that may be affecting your tickets:

Details:
- Affected Area: {bottleneck_type.title()}
- Your Tickets in Queue: {len([t for t in affected_tickets if t.get('assignee_id') == 'current_user'])}

Suggestions:
{chr(10).join(f"- {action}" for action in bottleneck_data.get('technician_suggestions', ['Review ticket priorities', 'Update ticket status']))}

If you need assistance or have questions about your workload, please contact your manager.
        """.strip()
    
    return {
        "subject": subject,
        "message": message,
        "priority": "medium",
        "bottleneck_type": bottleneck_type
    }


def _get_channels_for_urgency(urgency_level: str) -> List[str]:
    """Get notification channels based on urgency level"""
    
    channel_mapping = {
        'critical': ['in_app', 'email', 'sms', 'comment'],
        'high': ['in_app', 'email', 'comment'],
        'medium': ['in_app', 'comment'],
        'low': ['in_app']
    }
    
    return channel_mapping.get(urgency_level, ['in_app'])


async def _send_notification(
    channel: str, 
    recipient: Dict[str, Any], 
    content: Dict[str, Any]
) -> Dict[str, Any]:
    """Send notification through specified channel"""
    
    try:
        if channel == 'in_app':
            return await _send_in_app_notification(recipient, content)
        elif channel == 'email':
            return await _send_email_notification(recipient, content)
        elif channel == 'sms':
            return await _send_sms_notification(recipient, content)
        elif channel == 'comment':
            return await _send_ticket_comment_notification(recipient, content)
        else:
            return {
                "success": False,
                "error": f"Unknown notification channel: {channel}"
            }
    
    except Exception as e:
        logger.error(f"Error sending {channel} notification: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def _send_in_app_notification(recipient: Dict[str, Any], content: Dict[str, Any]) -> Dict[str, Any]:
    """Send in-app notification through SuperOps"""
    # This would integrate with SuperOps notification API
    logger.info(f"Sending in-app notification to {recipient['name']}")
    
    return {
        "success": True,
        "message": "In-app notification sent successfully",
        "notification_id": f"in_app_{int(datetime.now().timestamp())}"
    }


async def _send_email_notification(recipient: Dict[str, Any], content: Dict[str, Any]) -> Dict[str, Any]:
    """Send email notification"""
    if not recipient.get('preferences', {}).get('email_notifications', True):
        return {
            "success": False,
            "error": "Email notifications disabled for user"
        }
    
    # This would integrate with email service
    logger.info(f"Sending email to {recipient['email']}")
    
    return {
        "success": True,
        "message": f"Email sent to {recipient['email']}",
        "notification_id": f"email_{int(datetime.now().timestamp())}"
    }


async def _send_sms_notification(recipient: Dict[str, Any], content: Dict[str, Any]) -> Dict[str, Any]:
    """Send SMS notification"""
    if not recipient.get('preferences', {}).get('sms_notifications', False):
        return {
            "success": False,
            "error": "SMS notifications disabled for user"
        }
    
    if not recipient.get('phone'):
        return {
            "success": False,
            "error": "No phone number available for SMS"
        }
    
    # This would integrate with SMS service
    logger.info(f"Sending SMS to {recipient['phone']}")
    
    return {
        "success": True,
        "message": f"SMS sent to {recipient['phone']}",
        "notification_id": f"sms_{int(datetime.now().timestamp())}"
    }


async def _send_ticket_comment_notification(recipient: Dict[str, Any], content: Dict[str, Any]) -> Dict[str, Any]:
    """Send notification as ticket comment with mention"""
    ticket_id = content.get('ticket_id')
    if not ticket_id:
        return {
            "success": False,
            "error": "No ticket ID provided for comment notification"
        }
    
    # This would use SuperOps API to add comment with mention
    logger.info(f"Adding comment notification to ticket {ticket_id}")
    
    comment_text = f"@{recipient['name']} - {content['subject']}\n\n{content['message']}"
    
    return {
        "success": True,
        "message": f"Comment added to ticket {ticket_id}",
        "notification_id": f"comment_{ticket_id}_{int(datetime.now().timestamp())}"
    }