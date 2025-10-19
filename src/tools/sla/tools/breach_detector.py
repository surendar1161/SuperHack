"""
SLA Breach Detector Tool

Strands-compatible tool for detecting SLA breaches, predicting potential breaches,
and triggering appropriate escalation workflows.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from strands import tool

from .sla_calculator import SLACalculatorTool
from ..models import SLABreach, TicketSLAStatus, BreachType, AlertSeverity, RiskLevel
from ..exceptions import SLABreachError
from ..data_access import SLADataAccess
from ....utils.logger import get_logger


@dataclass
class BreachPrediction:
    """Prediction of potential SLA breach"""
    ticket_id: str
    breach_type: BreachType
    predicted_breach_time: datetime
    confidence: float  # 0.0 to 1.0
    time_to_breach: timedelta
    risk_factors: List[str]


class BreachDetectorTool:
    """
    Advanced SLA breach detection and prediction tool
    
    Features:
    - Real-time breach detection
    - Predictive breach analysis
    - Risk factor identification
    - Automated escalation triggers
    - Historical pattern analysis
    """
    
    def __init__(self, sla_data_access: SLADataAccess, sla_calculator: SLACalculatorTool = None):
        self.logger = get_logger("BreachDetectorTool")
        
        self.sla_data_access = sla_data_access
        self.sla_calculator = sla_calculator
        
        # Detection thresholds
        self.prediction_window = timedelta(hours=2)  # Look ahead 2 hours
        self.confidence_threshold = 0.7  # Minimum confidence for predictions
        
        # Risk factors and weights
        self.risk_factors = {
            'high_priority_ticket': 0.3,
            'complex_category': 0.2,
            'technician_overload': 0.25,
            'historical_delays': 0.15,
            'time_of_day': 0.1
        }
        
        # Tracking
        self.detected_breaches: Set[str] = set()
        self.predicted_breaches: Dict[str, BreachPrediction] = {}
        
    async def _execute_impl(self, **kwargs) -> Dict[str, Any]:
        """Execute breach detection operation"""
        operation = kwargs.get('operation', 'detect_breaches')
        
        if operation == 'detect_breaches':
            return await self._detect_current_breaches(**kwargs)
        elif operation == 'predict_breaches':
            return await self._predict_potential_breaches(**kwargs)
        elif operation == 'analyze_ticket':
            return await self._analyze_single_ticket(**kwargs)
        elif operation == 'get_risk_assessment':
            return await self._get_risk_assessment(**kwargs)
        else:
            raise SLABreachError("unknown", operation, f"Unknown operation: {operation}")
    
    async def detect_current_breaches(self, ticket_filters: Dict[str, Any] = None) -> List[SLABreach]:
        """Detect current SLA breaches"""
        result = await self.execute(
            operation='detect_breaches',
            ticket_filters=ticket_filters or {}
        )
        
        if not result.is_success():
            raise SLABreachError("detection", "detect_breaches", result.error or "Detection failed")
        
        return result.data.get('breaches', [])
    
    async def _detect_current_breaches(self, **kwargs) -> Dict[str, Any]:
        """Internal implementation of breach detection"""
        ticket_filters = kwargs.get('ticket_filters', {})
        
        try:
            # Get active tickets
            tickets = await self.sla_data_access.get_ticket_list(ticket_filters)
            
            detected_breaches = []
            new_breaches = []
            
            for ticket in tickets:
                # Skip resolved tickets
                if ticket.get('status', '').lower() in ['resolved', 'closed']:
                    continue
                
                try:
                    # Get SLA policy for ticket
                    priority = ticket.get('priority', 'medium').lower()
                    sla_policy = await self.sla_data_access.get_sla_policy_by_priority(priority)
                    
                    if not sla_policy:
                        continue
                    
                    # Calculate SLA status
                    sla_status = await self.sla_calculator.calculate_sla_status(ticket, sla_policy)
                    
                    # Check for breaches
                    breaches = self._check_ticket_breaches(ticket, sla_status)
                    
                    for breach in breaches:
                        detected_breaches.append(breach)
                        
                        # Track new breaches
                        breach_key = f"{breach.ticket_id}_{breach.breach_type.value}"
                        if breach_key not in self.detected_breaches:
                            new_breaches.append(breach)
                            self.detected_breaches.add(breach_key)
                
                except Exception as e:
                    self.logger.warning(f"Failed to check breach for ticket {ticket.get('id')}: {e}")
                    continue
            
            return {
                'breaches': detected_breaches,
                'new_breaches': new_breaches,
                'total_count': len(detected_breaches),
                'new_count': len(new_breaches),
                'detection_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Breach detection failed: {e}")
            raise SLABreachError("detection", "detect_breaches", str(e))
    
    async def predict_potential_breaches(self, prediction_window: timedelta = None) -> List[BreachPrediction]:
        """Predict potential SLA breaches"""
        result = await self.execute(
            operation='predict_breaches',
            prediction_window=prediction_window or self.prediction_window
        )
        
        if not result.is_success():
            raise SLABreachError("prediction", "predict_breaches", result.error or "Prediction failed")
        
        return result.data.get('predictions', [])
    
    async def _predict_potential_breaches(self, **kwargs) -> Dict[str, Any]:
        """Internal implementation of breach prediction"""
        prediction_window = kwargs.get('prediction_window', self.prediction_window)
        
        try:
            # Get tickets at risk
            at_risk_tickets = await self.sla_data_access.get_tickets_at_risk("MEDIUM")
            
            predictions = []
            
            for ticket in at_risk_tickets:
                try:
                    prediction = await self._predict_ticket_breach(ticket, prediction_window)
                    if prediction and prediction.confidence >= self.confidence_threshold:
                        predictions.append(prediction)
                        
                        # Cache prediction
                        self.predicted_breaches[ticket['id']] = prediction
                
                except Exception as e:
                    self.logger.warning(f"Failed to predict breach for ticket {ticket.get('id')}: {e}")
                    continue
            
            return {
                'predictions': predictions,
                'prediction_count': len(predictions),
                'prediction_window_hours': prediction_window.total_seconds() / 3600,
                'confidence_threshold': self.confidence_threshold,
                'prediction_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Breach prediction failed: {e}")
            raise SLABreachError("prediction", "predict_breaches", str(e))
    
    async def analyze_ticket_risk(self, ticket_id: str) -> Dict[str, Any]:
        """Analyze risk factors for a specific ticket"""
        result = await self.execute(
            operation='analyze_ticket',
            ticket_id=ticket_id
        )
        
        if not result.is_success():
            raise SLABreachError(ticket_id, "analyze_ticket", result.error or "Analysis failed")
        
        return result.data
    
    async def _analyze_single_ticket(self, **kwargs) -> Dict[str, Any]:
        """Internal implementation of single ticket analysis"""
        ticket_id = kwargs['ticket_id']
        
        try:
            # Get ticket data
            tickets = await self.sla_data_access.get_ticket_list({'id': ticket_id})
            if not tickets:
                raise SLABreachError(ticket_id, "analyze_ticket", "Ticket not found")
            
            ticket = tickets[0]
            
            # Get SLA policy
            priority = ticket.get('priority', 'medium').lower()
            sla_policy = await self.sla_data_access.get_sla_policy_by_priority(priority)
            
            if not sla_policy:
                raise SLABreachError(ticket_id, "analyze_ticket", "No SLA policy found")
            
            # Calculate SLA status
            sla_status = await self.sla_calculator.calculate_sla_status(ticket, sla_policy)
            
            # Analyze risk factors
            risk_analysis = await self._analyze_risk_factors(ticket, sla_status)
            
            # Check for current breaches
            current_breaches = self._check_ticket_breaches(ticket, sla_status)
            
            # Predict future breaches
            prediction = await self._predict_ticket_breach(ticket, self.prediction_window)
            
            return {
                'ticket_id': ticket_id,
                'sla_status': sla_status,
                'risk_analysis': risk_analysis,
                'current_breaches': current_breaches,
                'breach_prediction': prediction,
                'analysis_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Ticket analysis failed for {ticket_id}: {e}")
            raise SLABreachError(ticket_id, "analyze_ticket", str(e))
    
    def _check_ticket_breaches(self, ticket: Dict[str, Any], sla_status: TicketSLAStatus) -> List[SLABreach]:
        """Check if ticket has current SLA breaches"""
        breaches = []
        current_time = datetime.now()
        
        # Check response breach
        if sla_status.is_response_breached:
            breach = SLABreach(
                id=f"{ticket['id']}_response_{int(current_time.timestamp())}",
                ticket_id=ticket['id'],
                ticket_number=ticket.get('number', ''),
                breach_type=BreachType.RESPONSE,
                breach_time=current_time,
                sla_policy=sla_status.sla_policy,
                technician_id=ticket.get('assignee', {}).get('id'),
                technician_name=ticket.get('assignee', {}).get('name'),
                severity=self._determine_breach_severity(sla_status, BreachType.RESPONSE),
                customer_impact=self._assess_customer_impact(ticket),
                escalation_required=True,
                escalation_level=sla_status.escalation_level,
                created_at=current_time
            )
            breaches.append(breach)
        
        # Check resolution breach
        if sla_status.is_resolution_breached:
            breach = SLABreach(
                id=f"{ticket['id']}_resolution_{int(current_time.timestamp())}",
                ticket_id=ticket['id'],
                ticket_number=ticket.get('number', ''),
                breach_type=BreachType.RESOLUTION,
                breach_time=current_time,
                sla_policy=sla_status.sla_policy,
                technician_id=ticket.get('assignee', {}).get('id'),
                technician_name=ticket.get('assignee', {}).get('name'),
                severity=self._determine_breach_severity(sla_status, BreachType.RESOLUTION),
                customer_impact=self._assess_customer_impact(ticket),
                escalation_required=True,
                escalation_level=sla_status.escalation_level,
                created_at=current_time
            )
            breaches.append(breach)
        
        return breaches
    
    async def _predict_ticket_breach(self, ticket: Dict[str, Any], 
                                   prediction_window: timedelta) -> Optional[BreachPrediction]:
        """Predict potential breach for a ticket"""
        try:
            # Get SLA policy
            priority = ticket.get('priority', 'medium').lower()
            sla_policy = await self.sla_data_access.get_sla_policy_by_priority(priority)
            
            if not sla_policy:
                return None
            
            # Calculate current SLA status
            sla_status = await self.sla_calculator.calculate_sla_status(ticket, sla_policy)
            
            # Skip if already breached
            if sla_status.is_breached:
                return None
            
            # Analyze risk factors
            risk_analysis = await self._analyze_risk_factors(ticket, sla_status)
            
            # Determine most likely breach type and time
            breach_predictions = []
            
            # Response breach prediction
            if not sla_status.is_response_breached and sla_status.response_time_remaining:
                response_prediction = self._calculate_breach_prediction(
                    ticket, sla_status, BreachType.RESPONSE, risk_analysis, prediction_window
                )
                if response_prediction:
                    breach_predictions.append(response_prediction)
            
            # Resolution breach prediction
            if not sla_status.is_resolution_breached and sla_status.resolution_time_remaining:
                resolution_prediction = self._calculate_breach_prediction(
                    ticket, sla_status, BreachType.RESOLUTION, risk_analysis, prediction_window
                )
                if resolution_prediction:
                    breach_predictions.append(resolution_prediction)
            
            # Return the most likely prediction
            if breach_predictions:
                return max(breach_predictions, key=lambda p: p.confidence)
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Failed to predict breach for ticket {ticket.get('id')}: {e}")
            return None
    
    def _calculate_breach_prediction(self, ticket: Dict[str, Any], sla_status: TicketSLAStatus,
                                   breach_type: BreachType, risk_analysis: Dict[str, Any],
                                   prediction_window: timedelta) -> Optional[BreachPrediction]:
        """Calculate breach prediction for specific type"""
        current_time = datetime.now()
        
        if breach_type == BreachType.RESPONSE:
            time_remaining = sla_status.response_time_remaining
        else:
            time_remaining = sla_status.resolution_time_remaining
        
        if not time_remaining or time_remaining.total_seconds() <= 0:
            return None
        
        # Calculate predicted breach time
        predicted_breach_time = current_time + time_remaining
        
        # Check if within prediction window
        if predicted_breach_time > current_time + prediction_window:
            return None
        
        # Calculate confidence based on risk factors
        base_confidence = 0.5
        risk_score = risk_analysis.get('total_risk_score', 0.0)
        
        # Adjust confidence based on time remaining
        time_factor = 1.0 - (time_remaining.total_seconds() / prediction_window.total_seconds())
        
        confidence = min(1.0, base_confidence + (risk_score * 0.3) + (time_factor * 0.2))
        
        return BreachPrediction(
            ticket_id=ticket['id'],
            breach_type=breach_type,
            predicted_breach_time=predicted_breach_time,
            confidence=confidence,
            time_to_breach=time_remaining,
            risk_factors=risk_analysis.get('active_risk_factors', [])
        )
    
    async def _analyze_risk_factors(self, ticket: Dict[str, Any], 
                                  sla_status: TicketSLAStatus) -> Dict[str, Any]:
        """Analyze risk factors for a ticket"""
        risk_scores = {}
        active_factors = []
        
        # High priority ticket risk
        priority = ticket.get('priority', 'medium').lower()
        if priority in ['high', 'critical']:
            risk_scores['high_priority_ticket'] = self.risk_factors['high_priority_ticket']
            active_factors.append('high_priority_ticket')
        
        # Complex category risk
        category = ticket.get('category', '').lower()
        complex_categories = ['infrastructure', 'security', 'integration']
        if any(cat in category for cat in complex_categories):
            risk_scores['complex_category'] = self.risk_factors['complex_category']
            active_factors.append('complex_category')
        
        # Technician overload risk
        assignee = ticket.get('assignee', {})
        if assignee:
            # This would typically check technician's current workload
            # For now, use a placeholder
            current_tickets = assignee.get('currentTicketCount', 0)
            max_tickets = assignee.get('maxConcurrentTickets', 10)
            
            if current_tickets >= max_tickets * 0.8:  # 80% capacity
                risk_scores['technician_overload'] = self.risk_factors['technician_overload']
                active_factors.append('technician_overload')
        
        # Time of day risk (outside business hours)
        current_hour = datetime.now().hour
        if current_hour < 9 or current_hour > 17:  # Outside 9-5
            risk_scores['time_of_day'] = self.risk_factors['time_of_day']
            active_factors.append('time_of_day')
        
        # Historical delays risk
        # This would typically analyze historical data for similar tickets
        # For now, use breach risk level as indicator
        if sla_status.breach_risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            risk_scores['historical_delays'] = self.risk_factors['historical_delays']
            active_factors.append('historical_delays')
        
        total_risk_score = sum(risk_scores.values())
        
        return {
            'risk_scores': risk_scores,
            'active_risk_factors': active_factors,
            'total_risk_score': total_risk_score,
            'risk_level': self._categorize_risk_score(total_risk_score)
        }
    
    def _categorize_risk_score(self, risk_score: float) -> str:
        """Categorize total risk score"""
        if risk_score >= 0.7:
            return "CRITICAL"
        elif risk_score >= 0.5:
            return "HIGH"
        elif risk_score >= 0.3:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _determine_breach_severity(self, sla_status: TicketSLAStatus, breach_type: BreachType) -> AlertSeverity:
        """Determine severity of SLA breach"""
        priority = sla_status.sla_policy.priority_level
        
        if priority.value == 'critical':
            return AlertSeverity.CRITICAL
        elif priority.value == 'high':
            return AlertSeverity.ERROR
        elif priority.value == 'medium':
            return AlertSeverity.WARNING
        else:
            return AlertSeverity.INFO
    
    def _assess_customer_impact(self, ticket: Dict[str, Any]) -> str:
        """Assess customer impact level"""
        priority = ticket.get('priority', 'medium').lower()
        category = ticket.get('category', '').lower()
        
        # High impact categories
        high_impact_categories = ['outage', 'security', 'critical']
        
        if priority == 'critical' or any(cat in category for cat in high_impact_categories):
            return "high"
        elif priority == 'high':
            return "medium"
        else:
            return "low"
    
    def get_breach_statistics(self) -> Dict[str, Any]:
        """Get breach detection statistics"""
        return {
            'total_detected_breaches': len(self.detected_breaches),
            'active_predictions': len(self.predicted_breaches),
            'confidence_threshold': self.confidence_threshold,
            'prediction_window_hours': self.prediction_window.total_seconds() / 3600,
            'risk_factors': self.risk_factors
        }
    
    def clear_breach_history(self):
        """Clear breach detection history"""
        self.detected_breaches.clear()
        self.predicted_breaches.clear()
        self.logger.info("Cleared breach detection history")


# Strands-compatible tool functions
@tool
async def detect_sla_breaches(ticket_filters: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Detect current SLA breaches for active tickets
    
    Args:
        ticket_filters: Optional filters for ticket selection
        
    Returns:
        Dictionary containing detected breaches and statistics
    """
    from ..data_access import SLADataAccess
    from ...config import AgentConfig
    
    try:
        # Initialize components (in real implementation, these would be injected)
        config = AgentConfig()
        sla_data_access = SLADataAccess(config, None)
        await sla_data_access.initialize()
        
        detector = BreachDetectorTool(sla_data_access)
        breaches = await detector.detect_current_breaches(ticket_filters or {})
        
        return {
            "success": True,
            "breaches": [
                {
                    "ticket_id": breach.ticket_id,
                    "breach_type": breach.breach_type.value,
                    "severity": breach.severity.value,
                    "breach_time": breach.breach_time.isoformat(),
                    "customer_impact": breach.customer_impact,
                    "escalation_required": breach.escalation_required
                }
                for breach in breaches
            ],
            "breach_count": len(breaches),
            "detection_time": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "breach_count": 0
        }


@tool
async def predict_sla_breaches(prediction_window_hours: int = 2) -> Dict[str, Any]:
    """
    Predict potential SLA breaches within the specified time window
    
    Args:
        prediction_window_hours: Hours to look ahead for predictions
        
    Returns:
        Dictionary containing breach predictions and confidence scores
    """
    from ..data_access import SLADataAccess
    from ...config import AgentConfig
    
    try:
        config = AgentConfig()
        sla_data_access = SLADataAccess(config, None)
        await sla_data_access.initialize()
        
        detector = BreachDetectorTool(sla_data_access)
        prediction_window = timedelta(hours=prediction_window_hours)
        predictions = await detector.predict_potential_breaches(prediction_window)
        
        return {
            "success": True,
            "predictions": [
                {
                    "ticket_id": pred.ticket_id,
                    "breach_type": pred.breach_type.value,
                    "predicted_breach_time": pred.predicted_breach_time.isoformat(),
                    "confidence": pred.confidence,
                    "time_to_breach_minutes": int(pred.time_to_breach.total_seconds() / 60),
                    "risk_factors": pred.risk_factors
                }
                for pred in predictions
            ],
            "prediction_count": len(predictions),
            "prediction_window_hours": prediction_window_hours
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "prediction_count": 0
        }


@tool
async def analyze_ticket_sla_risk(ticket_id: str) -> Dict[str, Any]:
    """
    Analyze SLA risk factors for a specific ticket
    
    Args:
        ticket_id: ID of the ticket to analyze
        
    Returns:
        Dictionary containing risk analysis and recommendations
    """
    from ..data_access import SLADataAccess
    from ...config import AgentConfig
    
    try:
        config = AgentConfig()
        sla_data_access = SLADataAccess(config, None)
        await sla_data_access.initialize()
        
        detector = BreachDetectorTool(sla_data_access)
        analysis = await detector.analyze_ticket_risk(ticket_id)
        
        return {
            "success": True,
            "ticket_id": ticket_id,
            "risk_analysis": analysis,
            "analysis_time": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ticket_id": ticket_id
        }