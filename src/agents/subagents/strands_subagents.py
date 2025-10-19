"""
Strands-Based Subagents

Updated subagents to work seamlessly with the new Strands-based IT Technical Agent controller.
These provide specialized functionality that can be called by the main Strands agents.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import asyncio

from ..config import AgentConfig
from ...tools.analysis.analyze_request import AnalyzeRequestTool
from ...tools.analysis.generate_suggestions import GenerateSuggestionsTool
from ...tools.ticket.create_ticket import get_create_ticket_tool
from ...tools.ticket.update_ticket import UpdateTicketTool
from ...clients.superops_client import SuperOpsClient
from ...utils.logger import get_logger


class StrandsSubagentInterface:
    """
    Base interface for subagents that work with Strands-based main agents

    These subagents provide specialized tools and capabilities that can be
    called by the main Strands agents through the graph execution.
    """

    def __init__(self, agent_id: str, config: AgentConfig):
        self.agent_id = agent_id
        self.config = config
        self.logger = get_logger(f"StrandsSubagent.{agent_id}")

        # Performance tracking
        self.execution_count = 0
        self.success_count = 0
        self.error_count = 0

    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute subagent task and return results"""
        self.execution_count += 1
        start_time = datetime.now()

        try:
            result = await self._execute_task(task_data)
            self.success_count += 1

            execution_time = (datetime.now() - start_time).total_seconds()

            return {
                'status': 'success',
                'result': result,
                'execution_time': execution_time,
                'agent_id': self.agent_id,
                'timestamp': start_time.isoformat()
            }

        except Exception as e:
            self.error_count += 1
            execution_time = (datetime.now() - start_time).total_seconds()

            self.logger.error(f"Error in subagent {self.agent_id}: {e}")

            return {
                'status': 'error',
                'error': str(e),
                'execution_time': execution_time,
                'agent_id': self.agent_id,
                'timestamp': start_time.isoformat()
            }

    async def _execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Override this method in subclasses"""
        raise NotImplementedError("Subclasses must implement _execute_task")

    def get_metrics(self) -> Dict[str, Any]:
        """Get subagent performance metrics"""
        return {
            'agent_id': self.agent_id,
            'execution_count': self.execution_count,
            'success_count': self.success_count,
            'error_count': self.error_count,
            'success_rate': self.success_count / max(self.execution_count, 1),
        }


class TriageStrandsSubagent(StrandsSubagentInterface):
    """Strands-compatible triage subagent"""

    def __init__(self, config: AgentConfig):
        super().__init__("triage_subagent", config)

    async def _execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute triage task"""
        request_data = task_data.get('request_data', {})

        # Perform triage assessment
        triage_result = {
            'priority': self._assess_priority(request_data),
            'urgency': self._assess_urgency(request_data),
            'impact': self._assess_impact(request_data),
            'category': self._categorize_request(request_data),
            'skill_requirements': self._identify_skill_requirements(request_data),
            'estimated_effort': self._estimate_effort(request_data),
            'routing_recommendation': self._get_routing_recommendation(request_data),
            'sla_requirements': self._get_sla_requirements(request_data)
        }

        return triage_result

    def _assess_priority(self, request_data: Dict[str, Any]) -> str:
        """Assess request priority"""
        description = request_data.get('description', '').lower()

        # High priority keywords
        high_priority_keywords = ['critical', 'urgent', 'down', 'outage', 'security', 'breach']
        if any(keyword in description for keyword in high_priority_keywords):
            return 'high'

        # Medium priority keywords
        medium_priority_keywords = ['slow', 'error', 'problem', 'issue', 'help']
        if any(keyword in description for keyword in medium_priority_keywords):
            return 'medium'

        return 'low'

    def _assess_urgency(self, request_data: Dict[str, Any]) -> str:
        """Assess request urgency"""
        priority = self._assess_priority(request_data)

        # Map priority to urgency
        urgency_mapping = {
            'high': 'urgent',
            'medium': 'normal',
            'low': 'low'
        }

        return urgency_mapping.get(priority, 'normal')

    def _assess_impact(self, request_data: Dict[str, Any]) -> str:
        """Assess business impact"""
        description = request_data.get('description', '').lower()

        # High impact keywords
        high_impact_keywords = ['all users', 'everyone', 'entire', 'company', 'business critical']
        if any(keyword in description for keyword in high_impact_keywords):
            return 'high'

        # Medium impact keywords
        medium_impact_keywords = ['team', 'department', 'group', 'multiple']
        if any(keyword in description for keyword in medium_impact_keywords):
            return 'medium'

        return 'low'

    def _categorize_request(self, request_data: Dict[str, Any]) -> str:
        """Categorize the request type"""
        description = request_data.get('description', '').lower()

        categories = {
            'incident': ['down', 'not working', 'broken', 'error', 'failed'],
            'service_request': ['need', 'request', 'install', 'setup', 'access'],
            'change_request': ['update', 'upgrade', 'change', 'modify'],
            'question': ['how to', 'help', 'question', 'information']
        }

        for category, keywords in categories.items():
            if any(keyword in description for keyword in keywords):
                return category

        return 'general'

    def _identify_skill_requirements(self, request_data: Dict[str, Any]) -> List[str]:
        """Identify required skills for resolution"""
        description = request_data.get('description', '').lower()

        skill_keywords = {
            'network': ['network', 'internet', 'wifi', 'connection', 'vpn'],
            'hardware': ['computer', 'laptop', 'printer', 'monitor', 'device'],
            'software': ['application', 'program', 'software', 'office', 'email'],
            'security': ['password', 'login', 'access', 'permission', 'security']
        }

        required_skills = []
        for skill, keywords in skill_keywords.items():
            if any(keyword in description for keyword in keywords):
                required_skills.append(skill)

        return required_skills if required_skills else ['general']

    def _estimate_effort(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate effort required"""
        category = self._categorize_request(request_data)
        priority = self._assess_priority(request_data)

        # Base effort estimates (in minutes)
        base_estimates = {
            'incident': 60,
            'service_request': 30,
            'change_request': 120,
            'question': 15,
            'general': 45
        }

        base_time = base_estimates.get(category, 45)

        # Adjust for priority
        priority_multiplier = {'high': 1.5, 'medium': 1.0, 'low': 0.8}
        estimated_time = base_time * priority_multiplier.get(priority, 1.0)

        return {
            'estimated_minutes': int(estimated_time),
            'complexity': 'high' if estimated_time > 90 else 'medium' if estimated_time > 30 else 'low'
        }

    def _get_routing_recommendation(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend routing for the request"""
        skills = self._identify_skill_requirements(request_data)
        priority = self._assess_priority(request_data)

        # Route based on skills and priority
        if 'security' in skills or priority == 'high':
            return {'route_to': 'level2_support', 'reason': 'High priority or security related'}
        elif len(skills) > 2:
            return {'route_to': 'specialist_team', 'reason': 'Multiple skill areas required'}
        else:
            return {'route_to': 'level1_support', 'reason': 'Standard support request'}

    def _get_sla_requirements(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Determine SLA requirements"""
        priority = self._assess_priority(request_data)
        urgency = self._assess_urgency(request_data)

        sla_matrix = {
            ('high', 'urgent'): {'response_minutes': 15, 'resolution_hours': 4},
            ('high', 'normal'): {'response_minutes': 30, 'resolution_hours': 8},
            ('medium', 'normal'): {'response_minutes': 60, 'resolution_hours': 24},
            ('low', 'low'): {'response_minutes': 240, 'resolution_hours': 72}
        }

        return sla_matrix.get((priority, urgency), {'response_minutes': 60, 'resolution_hours': 24})


class EventMonitorStrandsSubagent(StrandsSubagentInterface):
    """Strands-compatible event monitoring subagent"""

    def __init__(self, config: AgentConfig):
        super().__init__("event_monitor_subagent", config)
        self.monitored_events = []

    async def _execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute event monitoring task"""
        monitoring_config = task_data.get('monitoring_config', {})

        # Simulate event detection
        detected_events = await self._scan_for_events(monitoring_config)

        # Process events and generate alerts
        alerts = []
        for event in detected_events:
            alert = self._process_event(event)
            if alert:
                alerts.append(alert)

        return {
            'events_detected': len(detected_events),
            'alerts_generated': len(alerts),
            'events': detected_events,
            'alerts': alerts,
            'monitoring_status': 'active'
        }

    async def _scan_for_events(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scan for system events"""
        # Simulate event detection
        events = [
            {
                'type': 'system_alert',
                'source': 'server_monitor',
                'severity': 'warning',
                'message': 'High CPU usage detected',
                'timestamp': datetime.now().isoformat()
            }
        ]

        return events

    def _process_event(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process event and determine if alert is needed"""
        severity = event.get('severity', 'info')

        if severity in ['warning', 'error', 'critical']:
            return {
                'alert_type': f"{severity}_alert",
                'message': event.get('message', 'System event detected'),
                'source_event': event,
                'recommended_action': self._get_recommended_action(event),
                'created_at': datetime.now().isoformat()
            }

        return None

    def _get_recommended_action(self, event: Dict[str, Any]) -> str:
        """Get recommended action for event"""
        event_type = event.get('type', '')

        action_mapping = {
            'system_alert': 'Investigate system performance',
            'security_alert': 'Review security logs and access',
            'network_alert': 'Check network connectivity and configuration'
        }

        return action_mapping.get(event_type, 'Review event details and take appropriate action')


# Factory functions for creating subagents
def create_strands_subagents(config: AgentConfig) -> Dict[str, StrandsSubagentInterface]:
    """Create all Strands-compatible subagents"""
    return {
        'triage': TriageStrandsSubagent(config),
        'event_monitor': EventMonitorStrandsSubagent(config)
    }
