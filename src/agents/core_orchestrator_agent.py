"""
Core Orchestrator Agent

The main orchestrator responsible for analyzing requests, assigning tickets,
managing workflows, and coordinating between different agents and systems.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from strands import Agent

from .config import AgentConfig
from ..tools.ticket import (
    assign_ticket,
    create_ticket
)
from ..tools.ticket.categorize_ticket import (
    categorize_support_request,
    determine_assignment_logic
)
from ..tools.ticket.notify_technician import (
    notify_technician_assignment
)
from ..tools.sla import (
    calculate_sla_status,
    detect_sla_breaches
)
from ..tools.tracking import (
    track_time,
    monitor_progress
)
from ..tools.analysis import (
    analyze_request,
    generate_suggestions,
    identify_bottlenecks
)
from ..utils.logger import get_logger


class CoreOrchestratorAgent:
    """
    Core Orchestrator Agent
    
    Responsibilities:
    1. Analyze and tag each request (categorization, urgency, SLA, assignment logic)
    2. Assign tickets and notify the right technician
    3. Start and manage auto-tracking of time
    4. Monitor progress and check for bottlenecks
    5. Provide proactive suggestions to technicians
    """
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.logger = get_logger("CoreOrchestratorAgent")
        
        # Initialize the Strands agent with all necessary tools
        self.agent = Agent(
            name="core_orchestrator",
            system_prompt="""
            You are the Core Orchestrator Agent for IT support operations. Your responsibilities include:
            
            1. ANALYZE & CATEGORIZE: Analyze incoming support requests to determine:
               - Category and subcategory
               - Urgency level and priority
               - SLA requirements
               - Required skills and complexity
            
            2. ASSIGN & NOTIFY: Determine the best technician assignment based on:
               - Skills matching
               - Current workload
               - Availability
               - Urgency requirements
            
            3. TRACK & MONITOR: Start automatic tracking and monitoring:
               - Time tracking for SLA compliance
               - Progress monitoring
               - Bottleneck detection
            
            4. COORDINATE & SUGGEST: Provide proactive coordination:
               - Suggestions to technicians
               - Escalation when needed
               - Resource optimization
            
            Always prioritize customer satisfaction, SLA compliance, and efficient resource utilization.
            Use the available tools to make data-driven decisions and maintain comprehensive tracking.
            """,
            tools=[
                categorize_support_request,
                determine_assignment_logic,
                notify_technician_assignment,
                assign_ticket,
                create_ticket,
                calculate_sla_status,
                detect_sla_breaches,
                track_time,
                monitor_progress,
                analyze_request,
                generate_suggestions,
                identify_bottlenecks
            ]
        )
        
        # State tracking
        self.active_tickets = {}
        self.technician_workloads = {}
        self.performance_metrics = {
            'tickets_processed': 0,
            'successful_assignments': 0,
            'sla_breaches_prevented': 0,
            'bottlenecks_detected': 0
        }
        
        self.logger.info("Core Orchestrator Agent initialized")
    
    async def process_support_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for processing new support requests
        
        Args:
            request_data: Support request information
            
        Returns:
            Dictionary containing processing results and actions taken
        """
        try:
            self.logger.info(f"Processing support request: {request_data.get('subject', 'No subject')}")
            
            # Step 1: Analyze and categorize the request
            prompt = f"""
            Analyze and process this support request:
            
            Subject: {request_data.get('subject', 'No subject')}
            Description: {request_data.get('description', 'No description')}
            Customer: {request_data.get('customer', {}).get('name', 'Unknown')}
            Priority: {request_data.get('priority', 'medium')}
            
            Please:
            1. Categorize this request (category, urgency, SLA requirements)
            2. Determine the best technician assignment
            3. Create/assign the ticket
            4. Start time tracking
            5. Set up monitoring
            6. Provide initial suggestions
            
            Ensure all actions are properly coordinated and tracked.
            """
            
            # Process through the agent
            result = self.agent(prompt)
            
            # Update metrics
            self.performance_metrics['tickets_processed'] += 1
            
            # Track the ticket
            ticket_id = request_data.get('id') or f"ticket_{int(datetime.now().timestamp())}"
            self.active_tickets[ticket_id] = {
                'request_data': request_data,
                'processing_result': result,
                'created_at': datetime.now(),
                'status': 'assigned'
            }
            
            self.logger.info(f"Successfully processed support request {ticket_id}")
            
            return {
                'success': True,
                'ticket_id': ticket_id,
                'processing_result': result,
                'actions_taken': self._extract_actions_from_result(result),
                'processing_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error processing support request: {e}")
            return {
                'success': False,
                'error': str(e),
                'request_data': request_data
            }
    
    async def monitor_active_tickets(self) -> Dict[str, Any]:
        """
        Monitor all active tickets for progress, bottlenecks, and SLA compliance
        
        Returns:
            Dictionary containing monitoring results and alerts
        """
        try:
            self.logger.info(f"Monitoring {len(self.active_tickets)} active tickets")
            
            monitoring_results = {
                'tickets_monitored': len(self.active_tickets),
                'sla_alerts': [],
                'bottlenecks_detected': [],
                'suggestions_generated': [],
                'escalations_needed': []
            }
            
            for ticket_id, ticket_info in self.active_tickets.items():
                # Monitor individual ticket
                ticket_monitoring = await self._monitor_individual_ticket(ticket_id, ticket_info)
                
                # Aggregate results
                if ticket_monitoring.get('sla_alert'):
                    monitoring_results['sla_alerts'].append(ticket_monitoring['sla_alert'])
                
                if ticket_monitoring.get('bottleneck'):
                    monitoring_results['bottlenecks_detected'].append(ticket_monitoring['bottleneck'])
                
                if ticket_monitoring.get('suggestions'):
                    monitoring_results['suggestions_generated'].extend(ticket_monitoring['suggestions'])
                
                if ticket_monitoring.get('escalation_needed'):
                    monitoring_results['escalations_needed'].append(ticket_monitoring['escalation_needed'])
            
            # Detect system-wide bottlenecks
            system_bottlenecks = await self._detect_system_bottlenecks()
            monitoring_results['system_bottlenecks'] = system_bottlenecks
            
            self.logger.info(f"Monitoring completed: {len(monitoring_results['sla_alerts'])} SLA alerts, "
                           f"{len(monitoring_results['bottlenecks_detected'])} bottlenecks detected")
            
            return monitoring_results
            
        except Exception as e:
            self.logger.error(f"Error monitoring active tickets: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def provide_proactive_suggestions(self, technician_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate proactive suggestions for technicians based on their current workload and context
        
        Args:
            technician_id: ID of the technician
            context: Optional context information
            
        Returns:
            Dictionary containing suggestions and recommendations
        """
        try:
            self.logger.info(f"Generating proactive suggestions for technician {technician_id}")
            
            # Get technician's current tickets
            technician_tickets = [
                ticket for ticket in self.active_tickets.values()
                if ticket.get('assigned_technician') == technician_id
            ]
            
            prompt = f"""
            Generate proactive suggestions for technician {technician_id}:
            
            Current Workload:
            - Active Tickets: {len(technician_tickets)}
            - Context: {context or 'No additional context'}
            
            Please analyze their workload and provide:
            1. Priority recommendations
            2. Time management suggestions
            3. Potential bottleneck warnings
            4. Skill development opportunities
            5. Efficiency improvements
            
            Focus on actionable, specific recommendations that will improve their productivity and job satisfaction.
            """
            
            result = self.agent(prompt)
            
            return {
                'success': True,
                'technician_id': technician_id,
                'suggestions': result,
                'workload_summary': {
                    'active_tickets': len(technician_tickets),
                    'context': context
                },
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating suggestions for technician {technician_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'technician_id': technician_id
            }
    
    async def handle_escalation(self, escalation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle escalation requests from other agents or systems
        
        Args:
            escalation_data: Escalation information and context
            
        Returns:
            Dictionary containing escalation handling results
        """
        try:
            escalation_type = escalation_data.get('type', 'general')
            ticket_id = escalation_data.get('ticket_id')
            
            self.logger.info(f"Handling {escalation_type} escalation for ticket {ticket_id}")
            
            prompt = f"""
            Handle this escalation request:
            
            Type: {escalation_type}
            Ticket ID: {ticket_id}
            Reason: {escalation_data.get('reason', 'No reason provided')}
            Severity: {escalation_data.get('severity', 'medium')}
            
            Escalation Details:
            {escalation_data}
            
            Please:
            1. Assess the escalation severity and impact
            2. Determine appropriate escalation actions
            3. Notify relevant stakeholders
            4. Update ticket priority/assignment if needed
            5. Set up enhanced monitoring
            
            Ensure rapid resolution while maintaining quality standards.
            """
            
            result = self.agent(prompt)
            
            # Update ticket status if applicable
            if ticket_id and ticket_id in self.active_tickets:
                self.active_tickets[ticket_id]['escalated'] = True
                self.active_tickets[ticket_id]['escalation_time'] = datetime.now()
            
            return {
                'success': True,
                'escalation_type': escalation_type,
                'ticket_id': ticket_id,
                'escalation_result': result,
                'handled_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error handling escalation: {e}")
            return {
                'success': False,
                'error': str(e),
                'escalation_data': escalation_data
            }
    
    async def optimize_resource_allocation(self) -> Dict[str, Any]:
        """
        Analyze current resource allocation and suggest optimizations
        
        Returns:
            Dictionary containing optimization recommendations
        """
        try:
            self.logger.info("Analyzing resource allocation for optimization")
            
            # Gather current state data
            workload_analysis = await self._analyze_workload_distribution()
            bottleneck_analysis = await self._detect_system_bottlenecks()
            performance_analysis = self._analyze_performance_metrics()
            
            prompt = f"""
            Analyze current resource allocation and provide optimization recommendations:
            
            Current State:
            - Workload Distribution: {workload_analysis}
            - Detected Bottlenecks: {bottleneck_analysis}
            - Performance Metrics: {performance_analysis}
            
            Please provide:
            1. Resource allocation assessment
            2. Workload balancing recommendations
            3. Skill gap analysis
            4. Process improvement suggestions
            5. Technology optimization opportunities
            
            Focus on actionable recommendations that will improve overall system efficiency.
            """
            
            result = self.agent(prompt)
            
            return {
                'success': True,
                'optimization_recommendations': result,
                'current_state': {
                    'workload_distribution': workload_analysis,
                    'bottlenecks': bottleneck_analysis,
                    'performance_metrics': performance_analysis
                },
                'analyzed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing resource allocation: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _monitor_individual_ticket(self, ticket_id: str, ticket_info: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor individual ticket for issues and opportunities"""
        
        monitoring_result = {}
        
        try:
            # Check SLA status
            request_data = ticket_info['request_data']
            created_at = ticket_info['created_at']
            
            # Calculate time elapsed
            time_elapsed = datetime.now() - created_at
            
            # Mock SLA check (would use actual SLA tools)
            if time_elapsed > timedelta(hours=2):  # Example threshold
                monitoring_result['sla_alert'] = {
                    'ticket_id': ticket_id,
                    'alert_type': 'approaching_breach',
                    'time_elapsed_hours': time_elapsed.total_seconds() / 3600,
                    'recommended_action': 'Check progress and consider escalation'
                }
            
            # Check for bottlenecks
            if time_elapsed > timedelta(hours=4) and ticket_info.get('status') == 'assigned':
                monitoring_result['bottleneck'] = {
                    'ticket_id': ticket_id,
                    'bottleneck_type': 'stalled_ticket',
                    'duration_hours': time_elapsed.total_seconds() / 3600,
                    'recommended_action': 'Contact assigned technician'
                }
            
            # Generate suggestions
            monitoring_result['suggestions'] = [
                {
                    'ticket_id': ticket_id,
                    'suggestion': 'Regular progress updates recommended',
                    'priority': 'medium'
                }
            ]
            
        except Exception as e:
            self.logger.error(f"Error monitoring ticket {ticket_id}: {e}")
        
        return monitoring_result
    
    async def _detect_system_bottlenecks(self) -> List[Dict[str, Any]]:
        """Detect system-wide bottlenecks"""
        
        bottlenecks = []
        
        try:
            # Analyze ticket distribution
            total_tickets = len(self.active_tickets)
            if total_tickets > 50:  # Example threshold
                bottlenecks.append({
                    'type': 'high_ticket_volume',
                    'severity': 'medium',
                    'description': f'{total_tickets} active tickets may indicate resource strain',
                    'recommendation': 'Consider additional resource allocation'
                })
            
            # Analyze age of tickets
            old_tickets = [
                ticket for ticket in self.active_tickets.values()
                if (datetime.now() - ticket['created_at']).days > 3
            ]
            
            if len(old_tickets) > 10:
                bottlenecks.append({
                    'type': 'aging_tickets',
                    'severity': 'high',
                    'description': f'{len(old_tickets)} tickets are older than 3 days',
                    'recommendation': 'Review and prioritize aging tickets'
                })
            
        except Exception as e:
            self.logger.error(f"Error detecting system bottlenecks: {e}")
        
        return bottlenecks
    
    async def _analyze_workload_distribution(self) -> Dict[str, Any]:
        """Analyze current workload distribution across technicians"""
        
        try:
            # Group tickets by assigned technician
            technician_workloads = {}
            
            for ticket in self.active_tickets.values():
                tech_id = ticket.get('assigned_technician', 'unassigned')
                if tech_id not in technician_workloads:
                    technician_workloads[tech_id] = 0
                technician_workloads[tech_id] += 1
            
            # Calculate distribution metrics
            if technician_workloads:
                workload_values = list(technician_workloads.values())
                avg_workload = sum(workload_values) / len(workload_values)
                max_workload = max(workload_values)
                min_workload = min(workload_values)
                
                return {
                    'technician_workloads': technician_workloads,
                    'average_workload': avg_workload,
                    'max_workload': max_workload,
                    'min_workload': min_workload,
                    'workload_variance': max_workload - min_workload,
                    'balance_score': 1 - (max_workload - min_workload) / max(max_workload, 1)
                }
            
            return {'message': 'No active tickets to analyze'}
            
        except Exception as e:
            self.logger.error(f"Error analyzing workload distribution: {e}")
            return {'error': str(e)}
    
    def _analyze_performance_metrics(self) -> Dict[str, Any]:
        """Analyze current performance metrics"""
        
        return {
            'tickets_processed': self.performance_metrics['tickets_processed'],
            'successful_assignments': self.performance_metrics['successful_assignments'],
            'assignment_success_rate': (
                self.performance_metrics['successful_assignments'] / 
                max(self.performance_metrics['tickets_processed'], 1)
            ),
            'sla_breaches_prevented': self.performance_metrics['sla_breaches_prevented'],
            'bottlenecks_detected': self.performance_metrics['bottlenecks_detected']
        }
    
    def _extract_actions_from_result(self, result: str) -> List[str]:
        """Extract actions taken from agent result"""
        
        # This would parse the agent's response to extract specific actions
        # For now, return a simple list
        return [
            'Request analyzed and categorized',
            'Technician assignment determined',
            'Ticket created and assigned',
            'Time tracking initiated',
            'Monitoring activated'
        ]
    
    def get_orchestrator_metrics(self) -> Dict[str, Any]:
        """Get comprehensive orchestrator performance metrics"""
        
        return {
            'performance_metrics': self.performance_metrics,
            'active_tickets_count': len(self.active_tickets),
            'technician_workloads': self.technician_workloads,
            'system_status': 'operational',
            'last_updated': datetime.now().isoformat()
        }
    
    async def shutdown(self):
        """Gracefully shutdown the orchestrator"""
        self.logger.info("Shutting down Core Orchestrator Agent")
        # Perform any cleanup needed