"""
Bottleneck Monitor/Alert Agent

Continuously evaluates ticket/task progress, detects delays, SLA breaches,
and workflow bottlenecks. Notifies relevant agents when issues are detected.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set
from strands import Agent

from .config import AgentConfig
from ..tools.sla import (
    detect_sla_breaches,
    predict_sla_breaches,
    analyze_ticket_sla_risk
)
from ..tools.analysis import (
    identify_bottlenecks,
    analyze_request
)
from ..tools.tracking import (
    monitor_progress
)
from ..tools.ticket.notify_technician import (
    notify_bottleneck_alert
)
from ..utils.logger import get_logger


class BottleneckMonitorAgent:
    """
    Bottleneck Monitor/Alert Agent
    
    Responsibilities:
    1. Continuously evaluate ticket/task progress
    2. Detect delays, SLA breaches, and workflow bottlenecks
    3. Notify AI Productivity Agent and Manager Agent when bottlenecks are detected
    4. Provide real-time alerts and recommendations
    5. Track bottleneck patterns and trends
    """
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.logger = get_logger("BottleneckMonitorAgent")
        
        # Initialize the Strands agent with monitoring tools
        self.agent = Agent(
            name="bottleneck_monitor",
            system_prompt="""
            You are the Bottleneck Monitor Agent responsible for continuous monitoring of IT support operations.
            
            Your responsibilities include:
            
            1. CONTINUOUS MONITORING:
               - Monitor all active tickets for progress delays
               - Track SLA compliance and breach risks
               - Identify workflow bottlenecks in real-time
               - Analyze resource utilization patterns
            
            2. DETECTION & ANALYSIS:
               - Detect various types of bottlenecks (resource, process, skill, system)
               - Analyze root causes of delays and inefficiencies
               - Predict potential future bottlenecks
               - Assess impact on overall system performance
            
            3. ALERTING & NOTIFICATION:
               - Send immediate alerts for critical bottlenecks
               - Notify appropriate agents and managers
               - Escalate based on severity and impact
               - Provide actionable recommendations
            
            4. PATTERN RECOGNITION:
               - Identify recurring bottleneck patterns
               - Track trends and seasonal variations
               - Learn from historical data
               - Suggest preventive measures
            
            Always prioritize system efficiency, proactive problem detection, and clear communication.
            Use data-driven analysis to provide accurate and actionable insights.
            """,
            tools=[
                detect_sla_breaches,
                predict_sla_breaches,
                analyze_ticket_sla_risk,
                identify_bottlenecks,
                monitor_progress,
                notify_bottleneck_alert
            ]
        )
        
        # Monitoring state
        self.monitored_tickets = {}
        self.detected_bottlenecks = {}
        self.alert_history = []
        self.monitoring_metrics = {
            'total_tickets_monitored': 0,
            'bottlenecks_detected': 0,
            'alerts_sent': 0,
            'sla_breaches_prevented': 0,
            'false_positives': 0
        }
        
        # Configuration
        self.monitoring_config = {
            'check_interval_seconds': 300,  # 5 minutes
            'sla_warning_threshold_minutes': 30,  # Alert 30 min before breach
            'progress_stall_threshold_hours': 2,  # Alert if no progress for 2 hours
            'workload_imbalance_threshold': 0.3,  # 30% variance in workload
            'system_capacity_threshold': 0.8  # 80% capacity utilization
        }
        
        # Bottleneck detection patterns
        self.bottleneck_patterns = {
            'sla_breach': {
                'severity_weights': {'critical': 1.0, 'high': 0.8, 'medium': 0.5, 'low': 0.3},
                'escalation_thresholds': {'immediate': 0, 'urgent': 15, 'standard': 60}
            },
            'resource_overload': {
                'technician_capacity_threshold': 0.9,
                'queue_length_threshold': 10,
                'response_time_degradation': 0.5
            },
            'workflow_stall': {
                'no_progress_hours': 4,
                'status_unchanged_hours': 8,
                'customer_waiting_hours': 24
            }
        }
        
        self.logger.info("Bottleneck Monitor Agent initialized")
    
    async def start_continuous_monitoring(self):
        """Start continuous monitoring of all tickets and workflows"""
        
        self.logger.info("Starting continuous bottleneck monitoring")
        
        while True:
            try:
                # Perform monitoring cycle
                monitoring_results = await self._perform_monitoring_cycle()
                
                # Process detected bottlenecks
                if monitoring_results.get('bottlenecks_detected'):
                    await self._process_detected_bottlenecks(monitoring_results['bottlenecks_detected'])
                
                # Update metrics
                self._update_monitoring_metrics(monitoring_results)
                
                # Wait for next cycle
                await asyncio.sleep(self.monitoring_config['check_interval_seconds'])
                
            except Exception as e:
                self.logger.error(f"Error in monitoring cycle: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def _perform_monitoring_cycle(self) -> Dict[str, Any]:
        """Perform a complete monitoring cycle"""
        
        try:
            self.logger.debug("Performing monitoring cycle")
            
            prompt = """
            Perform comprehensive bottleneck monitoring:
            
            Please analyze the current state and detect:
            1. SLA breaches and imminent breaches
            2. Workflow bottlenecks and delays
            3. Resource utilization issues
            4. Progress stalls and blocked tickets
            5. System capacity problems
            
            For each detected issue:
            - Assess severity and impact
            - Identify root causes
            - Determine affected stakeholders
            - Provide specific recommendations
            - Suggest escalation if needed
            
            Focus on actionable insights that can improve system efficiency.
            """
            
            result = self.agent(prompt)
            
            # Parse monitoring results (in real implementation, this would be structured)
            monitoring_results = {
                'cycle_timestamp': datetime.now(),
                'tickets_checked': len(self.monitored_tickets),
                'bottlenecks_detected': await self._detect_specific_bottlenecks(),
                'sla_alerts': await self._check_sla_status(),
                'system_health': await self._assess_system_health(),
                'agent_result': result
            }
            
            return monitoring_results
            
        except Exception as e:
            self.logger.error(f"Error in monitoring cycle: {e}")
            return {
                'cycle_timestamp': datetime.now(),
                'error': str(e),
                'bottlenecks_detected': []
            }
    
    async def _detect_specific_bottlenecks(self) -> List[Dict[str, Any]]:
        """Detect specific types of bottlenecks"""
        
        detected_bottlenecks = []
        
        try:
            # 1. SLA Breach Bottlenecks
            sla_bottlenecks = await self._detect_sla_bottlenecks()
            detected_bottlenecks.extend(sla_bottlenecks)
            
            # 2. Resource Overload Bottlenecks
            resource_bottlenecks = await self._detect_resource_bottlenecks()
            detected_bottlenecks.extend(resource_bottlenecks)
            
            # 3. Workflow Stall Bottlenecks
            workflow_bottlenecks = await self._detect_workflow_bottlenecks()
            detected_bottlenecks.extend(workflow_bottlenecks)
            
            # 4. System Capacity Bottlenecks
            capacity_bottlenecks = await self._detect_capacity_bottlenecks()
            detected_bottlenecks.extend(capacity_bottlenecks)
            
        except Exception as e:
            self.logger.error(f"Error detecting bottlenecks: {e}")
        
        return detected_bottlenecks
    
    async def _detect_sla_bottlenecks(self) -> List[Dict[str, Any]]:
        """Detect SLA-related bottlenecks"""
        
        bottlenecks = []
        
        try:
            # Check for current and predicted SLA breaches
            current_breaches = await detect_sla_breaches()
            predicted_breaches = await predict_sla_breaches(prediction_window_hours=2)
            
            # Process current breaches
            if current_breaches.get('success') and current_breaches.get('breach_count', 0) > 0:
                for breach in current_breaches.get('breaches', []):
                    bottlenecks.append({
                        'type': 'sla_breach',
                        'severity': 'critical',
                        'ticket_id': breach.get('ticket_id'),
                        'breach_type': breach.get('breach_type'),
                        'impact': 'high',
                        'description': f"SLA breach detected for ticket {breach.get('ticket_id')}",
                        'recommended_actions': [
                            'Immediate escalation required',
                            'Notify customer of delay',
                            'Assign additional resources'
                        ],
                        'detected_at': datetime.now()
                    })
            
            # Process predicted breaches
            if predicted_breaches.get('success') and predicted_breaches.get('prediction_count', 0) > 0:
                for prediction in predicted_breaches.get('predictions', []):
                    if prediction.get('confidence', 0) > 0.7:  # High confidence predictions
                        bottlenecks.append({
                            'type': 'sla_risk',
                            'severity': 'high',
                            'ticket_id': prediction.get('ticket_id'),
                            'predicted_breach_time': prediction.get('predicted_breach_time'),
                            'confidence': prediction.get('confidence'),
                            'impact': 'medium',
                            'description': f"High risk of SLA breach for ticket {prediction.get('ticket_id')}",
                            'recommended_actions': [
                                'Prioritize ticket resolution',
                                'Check technician availability',
                                'Consider reassignment if needed'
                            ],
                            'detected_at': datetime.now()
                        })
            
        except Exception as e:
            self.logger.error(f"Error detecting SLA bottlenecks: {e}")
        
        return bottlenecks
    
    async def _detect_resource_bottlenecks(self) -> List[Dict[str, Any]]:
        """Detect resource utilization bottlenecks"""
        
        bottlenecks = []
        
        try:
            # Analyze technician workloads (mock data for now)
            technician_workloads = await self._get_technician_workloads()
            
            # Check for overloaded technicians
            for tech_id, workload in technician_workloads.items():
                utilization = workload.get('utilization', 0)
                if utilization > self.bottleneck_patterns['resource_overload']['technician_capacity_threshold']:
                    bottlenecks.append({
                        'type': 'resource_overload',
                        'severity': 'high' if utilization > 0.95 else 'medium',
                        'technician_id': tech_id,
                        'utilization': utilization,
                        'active_tickets': workload.get('active_tickets', 0),
                        'impact': 'high',
                        'description': f"Technician {tech_id} is overloaded ({utilization:.1%} utilization)",
                        'recommended_actions': [
                            'Redistribute workload',
                            'Consider additional resources',
                            'Prioritize critical tickets'
                        ],
                        'detected_at': datetime.now()
                    })
            
            # Check for workload imbalance
            if len(technician_workloads) > 1:
                utilizations = [w.get('utilization', 0) for w in technician_workloads.values()]
                max_util = max(utilizations)
                min_util = min(utilizations)
                imbalance = max_util - min_util
                
                if imbalance > self.monitoring_config['workload_imbalance_threshold']:
                    bottlenecks.append({
                        'type': 'workload_imbalance',
                        'severity': 'medium',
                        'imbalance_ratio': imbalance,
                        'max_utilization': max_util,
                        'min_utilization': min_util,
                        'impact': 'medium',
                        'description': f"Significant workload imbalance detected ({imbalance:.1%} variance)",
                        'recommended_actions': [
                            'Rebalance ticket assignments',
                            'Review assignment criteria',
                            'Consider skill-based routing'
                        ],
                        'detected_at': datetime.now()
                    })
            
        except Exception as e:
            self.logger.error(f"Error detecting resource bottlenecks: {e}")
        
        return bottlenecks
    
    async def _detect_workflow_bottlenecks(self) -> List[Dict[str, Any]]:
        """Detect workflow and process bottlenecks"""
        
        bottlenecks = []
        
        try:
            # Check for stalled tickets
            stalled_tickets = await self._identify_stalled_tickets()
            
            for ticket in stalled_tickets:
                stall_duration = ticket.get('stall_duration_hours', 0)
                bottlenecks.append({
                    'type': 'workflow_stall',
                    'severity': 'high' if stall_duration > 8 else 'medium',
                    'ticket_id': ticket.get('ticket_id'),
                    'stall_duration_hours': stall_duration,
                    'last_activity': ticket.get('last_activity'),
                    'impact': 'medium',
                    'description': f"Ticket {ticket.get('ticket_id')} has been stalled for {stall_duration:.1f} hours",
                    'recommended_actions': [
                        'Contact assigned technician',
                        'Check for blockers',
                        'Consider reassignment',
                        'Update customer on status'
                    ],
                    'detected_at': datetime.now()
                })
            
            # Check for process bottlenecks
            process_bottlenecks = await self._identify_process_bottlenecks()
            bottlenecks.extend(process_bottlenecks)
            
        except Exception as e:
            self.logger.error(f"Error detecting workflow bottlenecks: {e}")
        
        return bottlenecks
    
    async def _detect_capacity_bottlenecks(self) -> List[Dict[str, Any]]:
        """Detect system capacity bottlenecks"""
        
        bottlenecks = []
        
        try:
            # Check overall system capacity
            system_metrics = await self._get_system_capacity_metrics()
            
            overall_utilization = system_metrics.get('overall_utilization', 0)
            if overall_utilization > self.monitoring_config['system_capacity_threshold']:
                bottlenecks.append({
                    'type': 'system_capacity',
                    'severity': 'critical' if overall_utilization > 0.95 else 'high',
                    'utilization': overall_utilization,
                    'active_tickets': system_metrics.get('active_tickets', 0),
                    'queue_length': system_metrics.get('queue_length', 0),
                    'impact': 'critical',
                    'description': f"System operating at {overall_utilization:.1%} capacity",
                    'recommended_actions': [
                        'Scale up resources immediately',
                        'Implement emergency procedures',
                        'Notify management',
                        'Consider temporary resource allocation'
                    ],
                    'detected_at': datetime.now()
                })
            
        except Exception as e:
            self.logger.error(f"Error detecting capacity bottlenecks: {e}")
        
        return bottlenecks
    
    async def _process_detected_bottlenecks(self, bottlenecks: List[Dict[str, Any]]):
        """Process and respond to detected bottlenecks"""
        
        for bottleneck in bottlenecks:
            try:
                # Store bottleneck
                bottleneck_id = f"{bottleneck['type']}_{int(datetime.now().timestamp())}"
                self.detected_bottlenecks[bottleneck_id] = bottleneck
                
                # Determine notification strategy
                notification_strategy = self._determine_notification_strategy(bottleneck)
                
                # Send notifications
                await self._send_bottleneck_notifications(bottleneck, notification_strategy)
                
                # Log bottleneck
                self.logger.warning(f"Bottleneck detected: {bottleneck['type']} - {bottleneck['description']}")
                
                # Update metrics
                self.monitoring_metrics['bottlenecks_detected'] += 1
                
            except Exception as e:
                self.logger.error(f"Error processing bottleneck: {e}")
    
    def _determine_notification_strategy(self, bottleneck: Dict[str, Any]) -> Dict[str, Any]:
        """Determine who and how to notify about a bottleneck"""
        
        severity = bottleneck.get('severity', 'medium')
        bottleneck_type = bottleneck.get('type', 'unknown')
        
        strategy = {
            'immediate_notification': severity in ['critical', 'high'],
            'notify_technicians': True,
            'notify_managers': severity in ['critical', 'high'],
            'notify_ai_agents': True,
            'escalation_required': severity == 'critical',
            'channels': []
        }
        
        # Determine notification channels based on severity
        if severity == 'critical':
            strategy['channels'] = ['in_app', 'email', 'sms']
        elif severity == 'high':
            strategy['channels'] = ['in_app', 'email']
        else:
            strategy['channels'] = ['in_app']
        
        # Add specific notifications based on bottleneck type
        if bottleneck_type in ['sla_breach', 'sla_risk']:
            strategy['notify_sla_team'] = True
        elif bottleneck_type in ['resource_overload', 'workload_imbalance']:
            strategy['notify_resource_managers'] = True
        elif bottleneck_type == 'system_capacity':
            strategy['notify_infrastructure_team'] = True
        
        return strategy
    
    async def _send_bottleneck_notifications(self, bottleneck: Dict[str, Any], strategy: Dict[str, Any]):
        """Send notifications about detected bottlenecks"""
        
        try:
            # Prepare notification data
            notification_data = {
                'bottleneck_type': bottleneck['type'],
                'severity': bottleneck['severity'],
                'description': bottleneck['description'],
                'recommended_actions': bottleneck.get('recommended_actions', []),
                'detected_at': bottleneck['detected_at'].isoformat(),
                'impact': bottleneck.get('impact', 'unknown')
            }
            
            # Notify technicians if affected
            if strategy.get('notify_technicians') and bottleneck.get('ticket_id'):
                technician_ids = await self._get_affected_technicians(bottleneck)
                if technician_ids:
                    await notify_bottleneck_alert(
                        technician_ids=technician_ids,
                        bottleneck_data=notification_data
                    )
            
            # Notify managers if required
            if strategy.get('notify_managers'):
                manager_ids = await self._get_relevant_managers(bottleneck)
                if manager_ids:
                    for manager_id in manager_ids:
                        await notify_bottleneck_alert(
                            technician_ids=[],
                            bottleneck_data=notification_data,
                            manager_id=manager_id
                        )
            
            # Update alert history
            self.alert_history.append({
                'bottleneck_id': f"{bottleneck['type']}_{int(bottleneck['detected_at'].timestamp())}",
                'notification_strategy': strategy,
                'sent_at': datetime.now()
            })
            
            self.monitoring_metrics['alerts_sent'] += 1
            
        except Exception as e:
            self.logger.error(f"Error sending bottleneck notifications: {e}")
    
    async def _check_sla_status(self) -> List[Dict[str, Any]]:
        """Check SLA status for all monitored tickets"""
        
        sla_alerts = []
        
        try:
            # This would integrate with actual SLA monitoring
            # For now, return mock data
            pass
            
        except Exception as e:
            self.logger.error(f"Error checking SLA status: {e}")
        
        return sla_alerts
    
    async def _assess_system_health(self) -> Dict[str, Any]:
        """Assess overall system health"""
        
        try:
            return {
                'overall_status': 'healthy',
                'capacity_utilization': 0.65,
                'average_response_time': 45,
                'sla_compliance_rate': 0.92,
                'active_bottlenecks': len(self.detected_bottlenecks),
                'last_assessment': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error assessing system health: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _get_technician_workloads(self) -> Dict[str, Dict[str, Any]]:
        """Get current technician workloads"""
        
        # Mock data - would integrate with actual system
        return {
            'tech-001': {'utilization': 0.85, 'active_tickets': 8, 'capacity': 10},
            'tech-002': {'utilization': 0.95, 'active_tickets': 9, 'capacity': 10},
            'tech-003': {'utilization': 0.60, 'active_tickets': 6, 'capacity': 10}
        }
    
    async def _identify_stalled_tickets(self) -> List[Dict[str, Any]]:
        """Identify tickets that have stalled in workflow"""
        
        # Mock data - would analyze actual ticket progress
        return [
            {
                'ticket_id': 'TICKET-123',
                'stall_duration_hours': 6.5,
                'last_activity': '2024-01-15T08:00:00Z',
                'assigned_technician': 'tech-002'
            }
        ]
    
    async def _identify_process_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identify process-level bottlenecks"""
        
        return []  # Would implement process analysis
    
    async def _get_system_capacity_metrics(self) -> Dict[str, Any]:
        """Get system capacity metrics"""
        
        return {
            'overall_utilization': 0.75,
            'active_tickets': 45,
            'queue_length': 12,
            'average_processing_time': 180
        }
    
    async def _get_affected_technicians(self, bottleneck: Dict[str, Any]) -> List[str]:
        """Get technicians affected by a bottleneck"""
        
        if bottleneck.get('technician_id'):
            return [bottleneck['technician_id']]
        elif bottleneck.get('ticket_id'):
            # Would look up assigned technician
            return ['tech-001']  # Mock
        
        return []
    
    async def _get_relevant_managers(self, bottleneck: Dict[str, Any]) -> List[str]:
        """Get managers who should be notified about a bottleneck"""
        
        return ['mgr-001']  # Mock data
    
    def _update_monitoring_metrics(self, monitoring_results: Dict[str, Any]):
        """Update monitoring metrics"""
        
        self.monitoring_metrics['total_tickets_monitored'] = monitoring_results.get('tickets_checked', 0)
        
        # Update other metrics based on results
        if monitoring_results.get('bottlenecks_detected'):
            self.monitoring_metrics['bottlenecks_detected'] += len(monitoring_results['bottlenecks_detected'])
    
    def get_monitoring_metrics(self) -> Dict[str, Any]:
        """Get comprehensive monitoring metrics"""
        
        return {
            'monitoring_metrics': self.monitoring_metrics,
            'active_bottlenecks': len(self.detected_bottlenecks),
            'recent_alerts': len([a for a in self.alert_history if 
                                (datetime.now() - a['sent_at']).seconds < 3600]),  # Last hour
            'monitoring_config': self.monitoring_config,
            'system_status': 'monitoring',
            'last_updated': datetime.now().isoformat()
        }
    
    async def shutdown(self):
        """Gracefully shutdown the bottleneck monitor"""
        self.logger.info("Shutting down Bottleneck Monitor Agent")