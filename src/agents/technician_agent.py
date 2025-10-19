"""
Technician Agent

Manages the lifecycle of tickets assigned to technicians, handles work updates,
and integrates with productivity suggestions from the AI system.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from strands import Agent

from .config import AgentConfig
from ..tools.ticket import (
    update_ticket,
    resolve_ticket,
    assign_ticket
)
from ..tools.tracking import (
    track_time,
    log_work,
    monitor_progress
)
from ..tools.analysis import (
    generate_suggestions
)
from ..clients.superops_client import SuperOpsClient
from ..utils.logger import get_logger


class TechnicianAgent:
    """
    Technician Agent
    
    Responsibilities:
    1. Accept tickets and start work
    2. Update ticket/progress status (calls SuperOps APIs)
    3. Complete work and trigger resolution/closure
    4. Receive and act on productivity suggestions from AI
    5. Manage personal workload and time tracking
    """
    
    def __init__(self, config: AgentConfig, technician_id: str, technician_name: str):
        self.config = config
        self.technician_id = technician_id
        self.technician_name = technician_name
        self.logger = get_logger(f"TechnicianAgent.{technician_name}")
        
        # Initialize SuperOps client
        self.superops_client = SuperOpsClient(config)
        
        # Initialize the Strands agent with technician-specific tools
        self.agent = Agent(
            name=f"technician_{technician_id}",
            system_prompt=f"""
            You are {technician_name}, an IT technician agent responsible for managing your assigned tickets.
            
            Your responsibilities include:
            
            1. TICKET MANAGEMENT:
               - Accept new ticket assignments
               - Update ticket status and progress
               - Resolve and close completed tickets
               - Communicate with customers when needed
            
            2. WORK TRACKING:
               - Track time spent on tickets
               - Log work performed and solutions implemented
               - Monitor progress against SLA requirements
               - Update stakeholders on status
            
            3. PRODUCTIVITY OPTIMIZATION:
               - Follow AI-generated productivity suggestions
               - Prioritize work based on urgency and SLA
               - Identify and report bottlenecks
               - Collaborate with other technicians when needed
            
            4. QUALITY ASSURANCE:
               - Ensure thorough problem resolution
               - Document solutions for knowledge base
               - Follow established procedures and best practices
               - Maintain high customer satisfaction
            
            Always prioritize customer satisfaction, SLA compliance, and quality work.
            Use the available tools to efficiently manage your workload and communicate progress.
            """,
            tools=[
                update_ticket,
                resolve_ticket,
                track_time,
                log_work,
                monitor_progress,
                generate_suggestions
            ]
        )
        
        # Technician state
        self.assigned_tickets = {}
        self.current_work_session = None
        self.daily_metrics = {
            'tickets_completed': 0,
            'total_work_time': 0,
            'customer_satisfaction': 0.0,
            'sla_compliance_rate': 0.0
        }
        
        # Productivity settings
        self.productivity_preferences = {
            'work_session_duration': 120,  # 2 hours
            'break_reminder_interval': 30,  # 30 minutes
            'priority_focus_mode': False,
            'collaboration_availability': True
        }
        
        self.logger.info(f"Technician Agent initialized for {technician_name}")
    
    async def accept_ticket_assignment(self, ticket_data: Dict[str, Any], assignment_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Accept a new ticket assignment and start work
        
        Args:
            ticket_data: Ticket information
            assignment_context: Context about why this ticket was assigned
            
        Returns:
            Dictionary containing acceptance results and next steps
        """
        try:
            ticket_id = ticket_data.get('id')
            self.logger.info(f"Accepting ticket assignment: {ticket_id}")
            
            prompt = f"""
            I've been assigned a new ticket. Please help me accept it and start work:
            
            Ticket Details:
            - ID: {ticket_id}
            - Subject: {ticket_data.get('subject', 'No subject')}
            - Priority: {ticket_data.get('priority', 'medium')}
            - Customer: {ticket_data.get('customer', {}).get('name', 'Unknown')}
            - Description: {ticket_data.get('description', 'No description')}
            
            Assignment Context:
            {assignment_context or 'No additional context'}
            
            Please:
            1. Accept the ticket assignment
            2. Update ticket status to "In Progress"
            3. Start time tracking
            4. Log initial work entry
            5. Analyze the issue and create work plan
            6. Provide initial assessment and next steps
            
            Focus on understanding the problem and setting up for efficient resolution.
            """
            
            result = self.agent(prompt)
            
            # Track the ticket locally
            self.assigned_tickets[ticket_id] = {
                'ticket_data': ticket_data,
                'assignment_context': assignment_context,
                'accepted_at': datetime.now(),
                'status': 'in_progress',
                'work_sessions': [],
                'total_time_spent': 0
            }
            
            # Start work session
            await self._start_work_session(ticket_id)
            
            return {
                'success': True,
                'ticket_id': ticket_id,
                'technician_id': self.technician_id,
                'acceptance_result': result,
                'status': 'accepted_and_started',
                'accepted_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error accepting ticket assignment: {e}")
            return {
                'success': False,
                'error': str(e),
                'ticket_id': ticket_data.get('id', 'unknown')
            }
    
    async def update_ticket_progress(self, ticket_id: str, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update ticket progress and status
        
        Args:
            ticket_id: ID of the ticket to update
            progress_data: Progress information and updates
            
        Returns:
            Dictionary containing update results
        """
        try:
            self.logger.info(f"Updating progress for ticket {ticket_id}")
            
            if ticket_id not in self.assigned_tickets:
                return {
                    'success': False,
                    'error': f'Ticket {ticket_id} not assigned to this technician'
                }
            
            ticket_info = self.assigned_tickets[ticket_id]
            
            prompt = f"""
            Update progress for ticket {ticket_id}:
            
            Current Status: {ticket_info['status']}
            Time Spent: {ticket_info['total_time_spent']} minutes
            
            Progress Update:
            - Work Performed: {progress_data.get('work_performed', 'No details provided')}
            - Status Change: {progress_data.get('new_status', 'No status change')}
            - Completion Percentage: {progress_data.get('completion_percentage', 'Not specified')}%
            - Next Steps: {progress_data.get('next_steps', 'To be determined')}
            - Blockers/Issues: {progress_data.get('blockers', 'None reported')}
            
            Please:
            1. Update the ticket status in SuperOps
            2. Log the work performed
            3. Update time tracking
            4. Add progress comments for stakeholders
            5. Assess if escalation or assistance is needed
            6. Provide recommendations for next steps
            
            Ensure all stakeholders are informed of progress and any issues.
            """
            
            result = self.agent(prompt)
            
            # Update local tracking
            ticket_info['status'] = progress_data.get('new_status', ticket_info['status'])
            ticket_info['last_updated'] = datetime.now()
            
            # Log work session
            if self.current_work_session and self.current_work_session['ticket_id'] == ticket_id:
                work_time = (datetime.now() - self.current_work_session['start_time']).total_seconds() / 60
                ticket_info['total_time_spent'] += work_time
            
            return {
                'success': True,
                'ticket_id': ticket_id,
                'update_result': result,
                'new_status': ticket_info['status'],
                'total_time_spent': ticket_info['total_time_spent'],
                'updated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error updating ticket progress: {e}")
            return {
                'success': False,
                'error': str(e),
                'ticket_id': ticket_id
            }
    
    async def complete_ticket_work(self, ticket_id: str, completion_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete work on a ticket and trigger resolution/closure
        
        Args:
            ticket_id: ID of the ticket to complete
            completion_data: Completion details and resolution information
            
        Returns:
            Dictionary containing completion results
        """
        try:
            self.logger.info(f"Completing work for ticket {ticket_id}")
            
            if ticket_id not in self.assigned_tickets:
                return {
                    'success': False,
                    'error': f'Ticket {ticket_id} not assigned to this technician'
                }
            
            ticket_info = self.assigned_tickets[ticket_id]
            
            prompt = f"""
            Complete work for ticket {ticket_id}:
            
            Ticket Summary:
            - Subject: {ticket_info['ticket_data'].get('subject')}
            - Total Time Spent: {ticket_info['total_time_spent']} minutes
            - Work Sessions: {len(ticket_info['work_sessions'])}
            
            Completion Details:
            - Resolution: {completion_data.get('resolution', 'No resolution provided')}
            - Root Cause: {completion_data.get('root_cause', 'Not specified')}
            - Solution Implemented: {completion_data.get('solution', 'No solution details')}
            - Customer Satisfaction: {completion_data.get('customer_satisfaction', 'Not rated')}
            - Knowledge Base Entry: {completion_data.get('kb_entry_needed', False)}
            
            Please:
            1. Resolve the ticket in SuperOps with detailed resolution
            2. Log final work entry with complete solution
            3. Stop time tracking and finalize hours
            4. Update customer with resolution details
            5. Create knowledge base entry if needed
            6. Mark ticket as resolved/closed
            7. Generate completion summary
            
            Ensure proper closure and documentation for future reference.
            """
            
            result = self.agent(prompt)
            
            # End work session
            if self.current_work_session and self.current_work_session['ticket_id'] == ticket_id:
                await self._end_work_session()
            
            # Update local tracking
            ticket_info['status'] = 'completed'
            ticket_info['completed_at'] = datetime.now()
            ticket_info['completion_data'] = completion_data
            
            # Update daily metrics
            self.daily_metrics['tickets_completed'] += 1
            self.daily_metrics['total_work_time'] += ticket_info['total_time_spent']
            
            # Move to completed tickets
            completed_ticket = self.assigned_tickets.pop(ticket_id)
            
            return {
                'success': True,
                'ticket_id': ticket_id,
                'completion_result': result,
                'total_time_spent': completed_ticket['total_time_spent'],
                'completed_at': datetime.now().isoformat(),
                'resolution_summary': completion_data.get('resolution', 'Work completed successfully')
            }
            
        except Exception as e:
            self.logger.error(f"Error completing ticket work: {e}")
            return {
                'success': False,
                'error': str(e),
                'ticket_id': ticket_id
            }
    
    async def receive_productivity_suggestion(self, suggestion_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Receive and process productivity suggestions from AI agents
        
        Args:
            suggestion_data: Productivity suggestions and recommendations
            
        Returns:
            Dictionary containing response to suggestions
        """
        try:
            suggestion_type = suggestion_data.get('type', 'general')
            self.logger.info(f"Received {suggestion_type} productivity suggestion")
            
            prompt = f"""
            I've received a productivity suggestion. Please help me evaluate and respond:
            
            Suggestion Details:
            - Type: {suggestion_type}
            - Priority: {suggestion_data.get('priority', 'medium')}
            - Source: {suggestion_data.get('source', 'AI System')}
            
            Suggestion Content:
            {suggestion_data.get('content', 'No content provided')}
            
            Recommendations:
            {chr(10).join(f"- {rec}" for rec in suggestion_data.get('recommendations', []))}
            
            Current Context:
            - Active Tickets: {len(self.assigned_tickets)}
            - Current Work Session: {self.current_work_session is not None}
            - Daily Metrics: {self.daily_metrics}
            
            Please:
            1. Evaluate the suggestion relevance and feasibility
            2. Determine which recommendations to implement
            3. Create action plan for implementation
            4. Identify any conflicts with current work
            5. Provide feedback on suggestion quality
            6. Update productivity preferences if needed
            
            Focus on practical implementation that improves efficiency without disrupting current work.
            """
            
            result = self.agent(prompt)
            
            # Update productivity preferences based on suggestions
            if suggestion_data.get('update_preferences'):
                self.productivity_preferences.update(suggestion_data['update_preferences'])
            
            return {
                'success': True,
                'suggestion_type': suggestion_type,
                'technician_response': result,
                'implementation_planned': True,
                'received_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error processing productivity suggestion: {e}")
            return {
                'success': False,
                'error': str(e),
                'suggestion_data': suggestion_data
            }
    
    async def request_assistance(self, ticket_id: str, assistance_type: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Request assistance from other technicians or escalate to management
        
        Args:
            ticket_id: ID of the ticket needing assistance
            assistance_type: Type of assistance needed (collaboration, escalation, expertise)
            details: Additional details about the assistance request
            
        Returns:
            Dictionary containing assistance request results
        """
        try:
            self.logger.info(f"Requesting {assistance_type} assistance for ticket {ticket_id}")
            
            if ticket_id not in self.assigned_tickets:
                return {
                    'success': False,
                    'error': f'Ticket {ticket_id} not assigned to this technician'
                }
            
            ticket_info = self.assigned_tickets[ticket_id]
            
            prompt = f"""
            Request assistance for ticket {ticket_id}:
            
            Ticket Details:
            - Subject: {ticket_info['ticket_data'].get('subject')}
            - Priority: {ticket_info['ticket_data'].get('priority')}
            - Time Spent: {ticket_info['total_time_spent']} minutes
            - Current Status: {ticket_info['status']}
            
            Assistance Request:
            - Type: {assistance_type}
            - Reason: {details.get('reason', 'Not specified')}
            - Urgency: {details.get('urgency', 'medium')}
            - Specific Skills Needed: {details.get('skills_needed', 'General support')}
            - Blockers: {details.get('blockers', 'None specified')}
            
            Please:
            1. Document the assistance request
            2. Identify appropriate resources (technicians/managers)
            3. Create assistance request with context
            4. Update ticket with assistance status
            5. Set expectations for response time
            6. Continue work on other aspects if possible
            
            Ensure the request includes all necessary context for effective assistance.
            """
            
            result = self.agent(prompt)
            
            # Update ticket status
            ticket_info['assistance_requested'] = {
                'type': assistance_type,
                'requested_at': datetime.now(),
                'details': details,
                'status': 'pending'
            }
            
            return {
                'success': True,
                'ticket_id': ticket_id,
                'assistance_type': assistance_type,
                'request_result': result,
                'requested_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error requesting assistance: {e}")
            return {
                'success': False,
                'error': str(e),
                'ticket_id': ticket_id
            }
    
    async def _start_work_session(self, ticket_id: str):
        """Start a new work session for a ticket"""
        
        if self.current_work_session:
            await self._end_work_session()
        
        self.current_work_session = {
            'ticket_id': ticket_id,
            'start_time': datetime.now(),
            'session_id': f"session_{int(datetime.now().timestamp())}"
        }
        
        self.logger.info(f"Started work session for ticket {ticket_id}")
    
    async def _end_work_session(self):
        """End the current work session"""
        
        if not self.current_work_session:
            return
        
        session_duration = (datetime.now() - self.current_work_session['start_time']).total_seconds() / 60
        ticket_id = self.current_work_session['ticket_id']
        
        # Log session to ticket
        if ticket_id in self.assigned_tickets:
            self.assigned_tickets[ticket_id]['work_sessions'].append({
                'session_id': self.current_work_session['session_id'],
                'start_time': self.current_work_session['start_time'],
                'end_time': datetime.now(),
                'duration_minutes': session_duration
            })
        
        self.logger.info(f"Ended work session for ticket {ticket_id}, duration: {session_duration:.1f} minutes")
        self.current_work_session = None
    
    def get_workload_summary(self) -> Dict[str, Any]:
        """Get current workload summary"""
        
        return {
            'technician_id': self.technician_id,
            'technician_name': self.technician_name,
            'assigned_tickets': len(self.assigned_tickets),
            'active_work_session': self.current_work_session is not None,
            'daily_metrics': self.daily_metrics,
            'productivity_preferences': self.productivity_preferences,
            'tickets_by_status': self._get_tickets_by_status(),
            'total_active_time': self._calculate_total_active_time(),
            'last_updated': datetime.now().isoformat()
        }
    
    def _get_tickets_by_status(self) -> Dict[str, int]:
        """Get count of tickets by status"""
        
        status_counts = {}
        for ticket in self.assigned_tickets.values():
            status = ticket['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return status_counts
    
    def _calculate_total_active_time(self) -> float:
        """Calculate total active work time today"""
        
        total_time = 0
        for ticket in self.assigned_tickets.values():
            total_time += ticket['total_time_spent']
        
        return total_time
    
    async def shutdown(self):
        """Gracefully shutdown the technician agent"""
        
        if self.current_work_session:
            await self._end_work_session()
        
        self.logger.info(f"Shutting down Technician Agent for {self.technician_name}")