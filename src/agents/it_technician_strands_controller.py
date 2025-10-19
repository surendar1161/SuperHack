"""
IT Technical Agent - Strands Graph Controller

Main controller agent that orchestrates all IT support workflows using Strands multi-agent pattern.
This agent controls and coordinates all other specialized agents and subagents.
"""

import logging
from typing import Dict, Any
from datetime import datetime
import json

from strands import Agent
from strands.multiagent import GraphBuilder
from strands.models.anthropic import AnthropicModel

from .config import AgentConfig
from ..tools.ticket.create_ticket import create_ticket
from ..tools.ticket.update_ticket import update_ticket
from ..tools.ticket.assign_ticket import assign_ticket
from ..tools.ticket.resolve_ticket import resolve_ticket
from ..tools.task.create_task import create_task
from ..tools.analysis.analyze_request import analyze_request
from ..tools.analysis.generate_suggestions import generate_suggestions
from ..tools.analysis.identify_bottlenecks import identify_bottlenecks
from ..tools.analytics.performance_metrics import performance_metrics
from ..tools.analytics.view_analytics import view_analytics
from ..memory.memory_manager import MemoryManager
from ..clients.superops_client import SuperOpsClient
from ..clients.sla_superops_client import SLASuperOpsClient
from ..workflows.ticket_lifecycle import TicketLifecycleWorkflow
from ..utils.logger import get_logger
from .subagents.sla_monitor_agent import SLAMonitorAgent

# Enable debug logs for strands
logging.getLogger("strands.multiagent").setLevel(logging.DEBUG)
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler()]
)


class ITTechnicianStrandsController:
    """
    Main IT Technical Agent using Strands multi-agent pattern

    This is the central controller that orchestrates all IT support workflows,
    SLA management, and coordinates all specialized agents and subagents.
    """

    def __init__(self, config: AgentConfig):
        self.config = config
        self.logger = get_logger("ITTechnicianStrandsController")

        # Initialize clients and memory
        self.superops_client = SuperOpsClient(config)
        self.sla_superops_client = SLASuperOpsClient(config)
        self.memory_manager = MemoryManager(config)
        
        # Create Anthropic model instance for all agents
        self.anthropic_model = AnthropicModel(
            model_id=config.model_name,
            max_tokens=config.max_tokens,
            params={
                "temperature": config.temperature
            }
        )

        # Strands agents and graphs
        self.main_agents = {}
        self.subagents = {}
        self.main_graph = None
        self.sla_monitor = None
        self.subagent_graph = None

        # Performance tracking
        self.execution_history = []
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'sla_breaches_handled': 0,
            'tickets_created': 0,
            'tickets_resolved': 0
        }

        # Active workflows
        self.active_workflows = {}

    async def initialize(self):
        """Initialize the complete IT support system with Strands graphs"""
        try:
            self.logger.info("Initializing IT Technician Strands Controller")

            # Initialize base services
            await self._initialize_base_services()

            # Create all specialized agents
            await self._create_main_agents()
            await self._create_subagents()

            # Build the main coordination graph
            self._build_main_graph()

            # Initialize specialized subagents
            await self._initialize_specialized_agents()

            self.logger.info("IT Technician Strands Controller initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize IT Technician Controller: {e}")
            raise

    async def _initialize_base_services(self):
        """Initialize base services and connections"""
        # Memory manager initialization - simplified
        self.logger.info("Base services initialized")

    async def _create_main_agents(self):
        """Create the main coordination agents using Strands pattern"""

        # Request Processor Agent - Main entry point
        self.main_agents['request_processor'] = Agent(
            name="request_processor",
            model=self.anthropic_model,
            system_prompt="""
            You are the main IT support request processor. Your responsibilities:
            
            1. Receive and analyze all incoming IT support requests
            2. Categorize requests by type, priority, and complexity
            3. Route requests to appropriate specialized agents
            4. Coordinate with SLA management for time-sensitive issues
            5. Track overall request lifecycle and status
            
            Request categories to identify:
            - Incident tickets (problems, outages, issues)
            - Service requests (new access, software installation)
            - Change requests (system modifications, updates)
            - SLA-sensitive issues requiring immediate attention
            
            Always provide clear categorization and routing decisions.
            """,
            tools=[
                analyze_request,
                generate_suggestions
            ]
        )

        # Ticket Manager Agent - Handles all ticket operations
        self.main_agents['ticket_manager'] = Agent(
            name="ticket_manager",
            model=self.anthropic_model,
            system_prompt="""
            You are the ticket management specialist. Your responsibilities:
            
            1. Create, update, and manage tickets in SuperOps
            2. Assign tickets to appropriate technicians
            3. Track ticket status and progress
            4. Handle ticket escalations and transfers
            5. Ensure proper documentation and closure
            
            Ticket management rules:
            - Always validate ticket data before creation
            - Follow proper assignment logic based on skills/availability
            - Maintain accurate status updates throughout lifecycle
            - Ensure all work is properly logged and tracked
            
            Provide detailed ticket management actions and status updates.
            """,
            tools=[
                create_ticket,
                update_ticket,
                assign_ticket,
                resolve_ticket,
                create_task
            ]
        )

        # Workflow Coordinator Agent - Orchestrates complex workflows
        self.main_agents['workflow_coordinator'] = Agent(
            name="workflow_coordinator",
            model=self.anthropic_model,
            system_prompt="""
            You are the workflow coordination specialist. Your responsibilities:
            
            1. Orchestrate complex multi-step IT workflows
            2. Coordinate between different specialized agents
            3. Handle workflow dependencies and sequencing
            4. Monitor workflow progress and handle exceptions
            5. Ensure workflow completion and proper handoffs
            
            Workflow types to manage:
            - Incident response workflows
            - Change management processes  
            - Service request fulfillment
            - Problem resolution procedures
            
            Always ensure proper coordination and completion tracking.
            """,
            tools=[
                create_ticket,
                update_ticket,
                assign_ticket,
                create_task
            ]
        )

        # Performance Monitor Agent - Tracks system performance
        self.main_agents['performance_monitor'] = Agent(
            name="performance_monitor",
            model=self.anthropic_model,
            system_prompt="""
            You are the performance monitoring specialist. Your responsibilities:
            
            1. Monitor IT support system performance and metrics
            2. Track SLA compliance and performance indicators
            3. Generate performance reports and analytics
            4. Identify performance bottlenecks and improvements
            5. Provide real-time system health status
            
            Key metrics to track:
            - Ticket resolution times
            - SLA compliance rates
            - Agent performance metrics
            - Customer satisfaction scores
            - System resource utilization
            
            Provide actionable insights and performance recommendations.
            """,
            tools=[
                performance_metrics,
                view_analytics,
                identify_bottlenecks
            ]
        )

    async def _create_subagents(self):
        """Create specialized subagents for specific tasks"""

        # Triage Agent - Handles initial request triage
        self.subagents['triage_agent'] = Agent(
            name="triage_agent",
            model=self.anthropic_model,
            system_prompt="""
            You are an IT support triage specialist. Your responsibilities:
            
            1. Perform initial assessment of support requests
            2. Classify urgency and impact levels
            3. Route requests to appropriate teams/agents
            4. Identify SLA requirements and constraints
            5. Handle immediate emergency responses
            
            Triage decisions should be fast but accurate.
            """,
            tools=[
                analyze_request,
                assign_ticket
            ]
        )

        # Event Monitor Agent - Monitors system events
        self.subagents['event_monitor_agent'] = Agent(
            name="event_monitor_agent",
            model=self.anthropic_model,
            system_prompt="""
            You are a system event monitoring specialist. Your responsibilities:
            
            1. Monitor IT infrastructure and system events
            2. Detect anomalies and potential issues
            3. Trigger proactive alerts and notifications
            4. Correlate events with known problems
            5. Initiate automatic response procedures
            
            Focus on proactive monitoring and early detection.
            """,
            tools=[
                performance_metrics,
                identify_bottlenecks
            ]
        )

    def _build_main_graph(self):
        """Build the main coordination graph using Strands pattern"""

        builder = GraphBuilder()

        # Add main coordination nodes
        builder.add_node(self.main_agents['request_processor'], "process_request")
        builder.add_node(self.main_agents['ticket_manager'], "manage_ticket")
        builder.add_node(self.main_agents['workflow_coordinator'], "coordinate_workflow")
        builder.add_node(self.main_agents['performance_monitor'], "monitor_performance")

        # Add subagent nodes
        builder.add_node(self.subagents['triage_agent'], "triage")
        builder.add_node(self.subagents['event_monitor_agent'], "monitor_events")

        # Define the main workflow edges
        # Request -> Triage -> Process -> Ticket Management
        builder.add_edge("process_request", "triage")
        builder.add_edge("triage", "manage_ticket")

        # Ticket -> Workflow Coordination
        builder.add_edge("manage_ticket", "coordinate_workflow")

        # All agents report to performance monitoring
        builder.add_edge("process_request", "monitor_performance")
        builder.add_edge("manage_ticket", "monitor_performance")
        builder.add_edge("coordinate_workflow", "monitor_performance")

        # Event monitoring can trigger any workflow
        builder.add_edge("monitor_events", "process_request")
        builder.add_edge("monitor_events", "triage")

        # Set main entry point
        builder.set_entry_point("process_request")

        # Configure execution limits
        builder.set_execution_timeout(900)  # 15 minute timeout

        # Build the main graph
        self.main_graph = builder.build()

        self.logger.info("Main IT support graph built successfully")

    async def _initialize_specialized_agents(self):
        """Initialize specialized subagents for SLA monitoring and other domains"""

        # Initialize SLA monitoring subagent
        self.sla_monitor = SLAMonitorAgent(self.config)
        await self.sla_monitor.start()

        self.logger.info("Specialized subagents initialized successfully")

    async def handle_support_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for handling IT support requests

        Args:
            request_data: Support request information

        Returns:
            Comprehensive handling results
        """
        try:
            self.metrics['total_requests'] += 1
            start_time = datetime.now()

            self.logger.info(f"Processing IT support request: {request_data.get('title', 'Unknown')}")

            # Prepare the prompt for the main graph
            prompt = f"""
            Handle IT support request:
            
            Request Details:
            - Title: {request_data.get('title', 'N/A')}
            - Description: {request_data.get('description', 'N/A')}
            - Priority: {request_data.get('priority', 'medium')}
            - Category: {request_data.get('category', 'general')}
            - Reporter: {request_data.get('reporter', {}).get('name', 'Unknown')}
            - Contact: {request_data.get('contact_info', 'N/A')}
            
            Required Actions:
            1. Analyze and categorize the request
            2. Perform initial triage and priority assessment
            3. Create appropriate ticket in SuperOps
            4. Route to specialized agents if needed
            5. Coordinate workflow execution
            6. Monitor and track progress
            7. Ensure SLA compliance
            8. Provide status updates and resolution
            
            Execute complete IT support workflow with proper coordination.
            """

            # Execute through the main graph
            result = self.main_graph(prompt)

            # Handle SLA requirements if needed
            sla_result = None
            if self._requires_sla_management(request_data):
                # Send ticket event to SLA monitor subagent
                await self._send_to_sla_monitor(request_data)

            # Track execution
            execution_time = (datetime.now() - start_time).total_seconds()

            execution_record = {
                'request_id': request_data.get('id', 'unknown'),
                'execution_time': execution_time,
                'status': result.status,
                'timestamp': start_time.isoformat(),
                'sla_handled': sla_result is not None
            }

            self.execution_history.append(execution_record)

            if result.status == 'success':
                self.metrics['successful_requests'] += 1
            else:
                self.metrics['failed_requests'] += 1

            self.logger.info(f"IT support request completed - Status: {result.status}")

            return {
                'status': result.status,
                'request_id': request_data.get('id'),
                'execution_time': execution_time,
                'result_data': result.data if hasattr(result, 'data') else None,
                'sla_result': sla_result,
                'timestamp': start_time.isoformat()
            }

        except Exception as e:
            self.metrics['failed_requests'] += 1
            self.logger.error(f"Error processing support request: {e}")

            return {
                'status': 'error',
                'request_id': request_data.get('id'),
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def handle_ticket_event(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ticket-related events"""
        try:
            self.logger.info(f"Processing ticket event for ticket {ticket_data.get('id')}")

            # Always check SLA requirements for ticket events
            await self._send_to_sla_monitor(ticket_data)

            # Update metrics if SLA breach was handled
            if sla_result and sla_result.get('status') == 'success':
                self.metrics['sla_breaches_handled'] += 1

            return {
                'status': 'success',
                'ticket_id': ticket_data.get('id'),
                'sla_result': sla_result,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error processing ticket event: {e}")
            return {
                'status': 'error',
                'ticket_id': ticket_data.get('id'),
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _requires_sla_management(self, request_data: Dict[str, Any]) -> bool:
        """Determine if request requires SLA management"""
        priority = request_data.get('priority', 'medium').lower()
        category = request_data.get('category', '').lower()

        # High/critical priority or incident categories require SLA management
        return (priority in ['high', 'critical', 'urgent'] or
                'incident' in category or
                'outage' in category or
                'emergency' in category)

    async def _send_to_sla_monitor(self, ticket_data: Dict[str, Any]):
        """Send ticket data to SLA monitor subagent"""
        if self.sla_monitor and self.sla_monitor.is_running:
            from .subagents.base_subagent import AgentMessage
            from datetime import datetime
            
            message = AgentMessage(
                id=f"ticket_event_{ticket_data.get('id', 'unknown')}_{int(datetime.now().timestamp())}",
                timestamp=datetime.now(),
                source_agent="ITTechnicianController",
                target_topic="ticket.updated",
                message_type="ticket_event",
                payload={"ticket": ticket_data},
                priority=3
            )
            
            await self.sla_monitor.send_message(message)

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system performance metrics"""

        total_requests = self.metrics['total_requests']
        success_rate = (self.metrics['successful_requests'] / max(total_requests, 1)) * 100

        # Recent execution performance
        recent_executions = self.execution_history[-20:] if self.execution_history else []
        avg_execution_time = 0
        if recent_executions:
            avg_execution_time = sum(ex['execution_time'] for ex in recent_executions) / len(recent_executions)

        sla_metrics = {}
        if self.sla_monitor:
            sla_metrics = self.sla_monitor.get_sla_metrics()

        return {
            'system_status': 'operational',
            'main_graph_status': 'initialized' if self.main_graph else 'not_initialized',
            'sla_monitor_status': 'initialized' if self.sla_monitor else 'not_initialized',
            'total_agents': len(self.main_agents) + len(self.subagents),
            'execution_metrics': {
                'total_requests': total_requests,
                'successful_requests': self.metrics['successful_requests'],
                'failed_requests': self.metrics['failed_requests'],
                'success_rate_percent': round(success_rate, 2),
                'sla_breaches_handled': self.metrics['sla_breaches_handled'],
                'tickets_created': self.metrics['tickets_created'],
                'tickets_resolved': self.metrics['tickets_resolved']
            },
            'performance_metrics': {
                'average_execution_time_seconds': round(avg_execution_time, 2),
                'recent_executions_count': len(recent_executions)
            },
            'agent_counts': {
                'main_agents': len(self.main_agents),
                'subagents': len(self.subagents),
                'active_workflows': len(self.active_workflows)
            },
            'sla_metrics': sla_metrics,
            'last_request': self.execution_history[-1]['timestamp'] if self.execution_history else None
        }

    # Tool creation methods for agents
    def _create_request_analysis_tool(self):
        """Create request analysis tool"""
        def analyze_request(request_data):
            analyzer = AnalyzeRequestTool()
            return {"category": "incident", "complexity": "medium", "confidence": 0.8}
        return analyze_request

    def _create_priority_assessment_tool(self):
        """Create priority assessment tool"""
        def assess_priority(request_data):
            return {"priority": "medium", "urgency": "normal", "impact": "low"}
        return assess_priority

    def _create_update_ticket_tool(self):
        """Create update ticket tool"""
        def update_ticket(ticket_data):
            tool = UpdateTicketTool(self.superops_client)
            return {"updated": True, "ticket_id": ticket_data.get('id')}
        return update_ticket

    def _create_assign_ticket_tool(self):
        """Create assign ticket tool"""
        def assign_ticket(assignment_data):
            tool = AssignTicketTool(self.superops_client)
            return {"assigned": True, "assignee": assignment_data.get('assignee')}
        return assign_ticket

    def _create_resolve_ticket_tool(self):
        """Create resolve ticket tool"""
        def resolve_ticket(resolution_data):
            tool = ResolveTicketTool(self.superops_client)
            return {"resolved": True, "resolution": resolution_data.get('resolution')}
        return resolve_ticket

    def _create_workflow_orchestration_tool(self):
        """Create workflow orchestration tool"""
        def orchestrate_workflow(workflow_data):
            workflow = TicketLifecycleWorkflow(self.config)
            return {"workflow_started": True, "steps": 5}
        return orchestrate_workflow

    def _create_dependency_management_tool(self):
        """Create dependency management tool"""
        def manage_dependencies(dependency_data):
            return {"dependencies_resolved": True}
        return manage_dependencies

    def _create_performance_tracking_tool(self):
        """Create performance tracking tool"""
        def track_performance(performance_data):
            return {"performance_tracked": True, "metrics_updated": True}
        return track_performance

    def _create_analytics_tool(self):
        """Create analytics tool"""
        def generate_analytics(analytics_data):
            return {"analytics_generated": True}
        return generate_analytics

    def _create_triage_tool(self):
        """Create triage tool"""
        def triage_request(triage_data):
            return {"triage_category": "incident", "escalation_required": False}
        return triage_request

    def _create_routing_tool(self):
        """Create routing tool"""
        def route_request(routing_data):
            return {"route_to": "level2_support", "routing_reason": "complex_technical_issue"}
        return route_request

    def _create_event_monitoring_tool(self):
        """Create event monitoring tool"""
        def monitor_events(monitoring_data):
            return {"events_detected": [], "alerts_triggered": []}
        return monitor_events

    def _create_alert_tool(self):
        """Create alert tool"""
        def send_alert(alert_data):
            return {"alert_sent": True, "recipients": ["admin", "oncall"]}
        return send_alert


# Factory function to create the IT Technical Agent controller
async def create_it_technician_controller(config: AgentConfig) -> ITTechnicianStrandsController:
    """
    Factory function to create and initialize IT Technical Agent Controller

    Args:
        config: Agent configuration

    Returns:
        Initialized ITTechnicianStrandsController instance
    """
    controller = ITTechnicianStrandsController(config)
    await controller.initialize()
    return controller


# Add cleanup method to the ITTechnicianStrandsController class
def add_cleanup_methods():
    """Add cleanup methods to the controller class"""
    
    async def cleanup(self):
        """Cleanup all resources and connections"""
        try:
            self.logger.info("Cleaning up IT Technician Strands Controller")
            
            # Close SuperOps client sessions
            if hasattr(self.superops_client, 'close'):
                await self.superops_client.close()
            
            if hasattr(self.sla_superops_client, 'close'):
                await self.sla_superops_client.close()
            
            # Stop subagents
            if self.sla_monitor:
                await self.sla_monitor.stop()
            
            # Cleanup memory manager
            if hasattr(self.memory_manager, 'cleanup'):
                await self.memory_manager.cleanup()
            
            self.logger.info("IT Technician Strands Controller cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    # Add methods to the class
    ITTechnicianStrandsController.cleanup = cleanup

# Apply the cleanup methods
add_cleanup_methods()

# Legacy compatibility - replace the old ITTechnician class
ITTechnician = ITTechnicianStrandsController