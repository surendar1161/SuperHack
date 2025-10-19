"""
SLA Calculator Tool

Strands-compatible tool for calculating SLA status, time remaining,
and breach detection with business hours support.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import pytz
from dateutil import parser
from strands import tool

from ..models import SLAPolicy, TicketSLAStatus, RiskLevel, BreachType
from ..exceptions import SLACalculationError
from ..interfaces import ISLACalculator
from ....utils.logger import get_logger


class SLACalculatorTool(ISLACalculator):
    """
    Advanced SLA calculation tool with business hours support
    
    Features:
    - Accurate SLA time calculations
    - Business hours and holiday support
    - Risk level assessment
    - Breach prediction
    - Multi-timezone support
    """
    
    def __init__(self):
        self.logger = get_logger("SLACalculatorTool")
        
        # Business hours configuration (default: 9 AM - 5 PM, Mon-Fri)
        self.business_hours = {
            'start_hour': 9,
            'end_hour': 17,
            'weekdays': [0, 1, 2, 3, 4],  # Monday = 0, Sunday = 6
            'timezone': 'UTC'
        }
        
        # Holidays (can be configured)
        self.holidays = set()
        
        # Risk level thresholds (percentage of time remaining)
        self.risk_thresholds = {
            RiskLevel.LOW: 0.5,      # > 50% time remaining
            RiskLevel.MEDIUM: 0.25,  # 25-50% time remaining  
            RiskLevel.HIGH: 0.1,     # 10-25% time remaining
            RiskLevel.CRITICAL: 0.0  # < 10% time remaining
        }
    
    async def calculate_sla_status(self, ticket_data: Dict[str, Any], sla_policy: SLAPolicy) -> TicketSLAStatus:
        """Calculate comprehensive SLA status for a ticket"""
        return await self._calculate_ticket_sla_status(ticket_data=ticket_data, sla_policy=sla_policy)
    
    async def _calculate_ticket_sla_status(self, **kwargs) -> TicketSLAStatus:
        """Internal implementation of SLA status calculation"""
        ticket_data = kwargs['ticket_data']
        sla_policy = kwargs['sla_policy']
        
        ticket_id = ticket_data.get('id', 'unknown')
        
        try:
            # Parse timestamps
            created_at = self._parse_timestamp(ticket_data.get('createdAt'))
            first_response_at = self._parse_timestamp(ticket_data.get('firstResponseAt'))
            resolved_at = self._parse_timestamp(ticket_data.get('resolvedAt'))
            
            current_time = datetime.now(pytz.UTC)
            
            # Calculate response SLA
            response_sla = await self._calculate_response_sla(
                created_at, first_response_at, sla_policy, current_time
            )
            
            # Calculate resolution SLA
            resolution_sla = await self._calculate_resolution_sla(
                created_at, resolved_at, sla_policy, current_time
            )
            
            # Determine overall risk level
            risk_level = self._determine_risk_level(response_sla, resolution_sla)
            
            # Create SLA status object
            sla_status = TicketSLAStatus(
                ticket_id=ticket_id,
                ticket_number=ticket_data.get('number', ''),
                sla_policy=sla_policy,
                created_at=created_at,
                first_response_at=first_response_at,
                resolved_at=resolved_at,
                response_time_remaining=response_sla.get('time_remaining'),
                resolution_time_remaining=resolution_sla.get('time_remaining'),
                is_response_breached=response_sla.get('is_breached', False),
                is_resolution_breached=resolution_sla.get('is_breached', False),
                breach_risk_level=risk_level,
                escalation_level=0,  # TODO: Calculate based on escalation rules
                last_updated=current_time
            )
            
            return sla_status
            
        except Exception as e:
            self.logger.error(f"SLA calculation failed for ticket {ticket_id}: {e}")
            raise SLACalculationError(ticket_id, 'calculate_status', str(e))
    
    async def _calculate_response_sla(self, created_at: datetime, first_response_at: Optional[datetime], 
                                    sla_policy: SLAPolicy, current_time: datetime) -> Dict[str, Any]:
        """Calculate response SLA details"""
        target_minutes = sla_policy.response_time_minutes
        
        if first_response_at:
            # Response already provided
            actual_response_time = first_response_at - created_at
            is_breached = actual_response_time.total_seconds() > (target_minutes * 60)
            
            return {
                'is_breached': is_breached,
                'actual_time': actual_response_time,
                'target_time': timedelta(minutes=target_minutes),
                'time_remaining': None,
                'breach_time': first_response_at if is_breached else None
            }
        else:
            # Response pending
            if sla_policy.business_hours_only:
                time_remaining = await self._calculate_business_time_remaining(
                    created_at, current_time, target_minutes
                )
            else:
                elapsed_time = current_time - created_at
                time_remaining = timedelta(minutes=target_minutes) - elapsed_time
            
            is_breached = time_remaining.total_seconds() <= 0
            
            return {
                'is_breached': is_breached,
                'actual_time': None,
                'target_time': timedelta(minutes=target_minutes),
                'time_remaining': time_remaining if not is_breached else timedelta(0),
                'breach_time': current_time if is_breached else None
            }
    
    async def _calculate_resolution_sla(self, created_at: datetime, resolved_at: Optional[datetime],
                                      sla_policy: SLAPolicy, current_time: datetime) -> Dict[str, Any]:
        """Calculate resolution SLA details"""
        target_hours = sla_policy.resolution_time_hours
        target_minutes = target_hours * 60
        
        if resolved_at:
            # Ticket already resolved
            actual_resolution_time = resolved_at - created_at
            is_breached = actual_resolution_time.total_seconds() > (target_minutes * 60)
            
            return {
                'is_breached': is_breached,
                'actual_time': actual_resolution_time,
                'target_time': timedelta(hours=target_hours),
                'time_remaining': None,
                'breach_time': resolved_at if is_breached else None
            }
        else:
            # Resolution pending
            if sla_policy.business_hours_only:
                time_remaining = await self._calculate_business_time_remaining(
                    created_at, current_time, target_minutes
                )
            else:
                elapsed_time = current_time - created_at
                time_remaining = timedelta(hours=target_hours) - elapsed_time
            
            is_breached = time_remaining.total_seconds() <= 0
            
            return {
                'is_breached': is_breached,
                'actual_time': None,
                'target_time': timedelta(hours=target_hours),
                'time_remaining': time_remaining if not is_breached else timedelta(0),
                'breach_time': current_time if is_breached else None
            }
    
    async def calculate_time_remaining(self, created_at: datetime, target_minutes: int, 
                                     business_hours_only: bool = True) -> Optional[int]:
        """Calculate time remaining until SLA breach"""
        result = await self._calculate_time_remaining_impl(
            created_at=created_at,
            target_minutes=target_minutes,
            business_hours_only=business_hours_only
        )
        return result.get('time_remaining_minutes')
    
    async def _calculate_time_remaining_impl(self, **kwargs) -> Dict[str, Any]:
        """Internal implementation of time remaining calculation"""
        created_at = kwargs['created_at']
        target_minutes = kwargs['target_minutes']
        business_hours_only = kwargs.get('business_hours_only', True)
        
        current_time = datetime.now(pytz.UTC)
        
        if business_hours_only:
            time_remaining = await self._calculate_business_time_remaining(
                created_at, current_time, target_minutes
            )
        else:
            elapsed_time = current_time - created_at
            time_remaining = timedelta(minutes=target_minutes) - elapsed_time
        
        return {
            'time_remaining_minutes': max(0, int(time_remaining.total_seconds() / 60)),
            'time_remaining_delta': time_remaining,
            'is_breached': time_remaining.total_seconds() <= 0
        }
    
    async def is_sla_breached(self, created_at: datetime, target_minutes: int, 
                            response_time: Optional[datetime] = None) -> bool:
        """Check if SLA is breached"""
        result = await self._check_breach_impl(
            created_at=created_at,
            target_minutes=target_minutes,
            response_time=response_time
        )
        return result.get('is_breached', False)
    
    async def _check_breach_impl(self, **kwargs) -> Dict[str, Any]:
        """Internal implementation of breach checking"""
        created_at = kwargs['created_at']
        target_minutes = kwargs['target_minutes']
        response_time = kwargs.get('response_time')
        
        if response_time:
            # Check actual response time
            actual_time = response_time - created_at
            is_breached = actual_time.total_seconds() > (target_minutes * 60)
            
            return {
                'is_breached': is_breached,
                'actual_minutes': int(actual_time.total_seconds() / 60),
                'target_minutes': target_minutes,
                'breach_margin': int(actual_time.total_seconds() / 60) - target_minutes
            }
        else:
            # Check current time
            current_time = datetime.now(pytz.UTC)
            elapsed_time = current_time - created_at
            is_breached = elapsed_time.total_seconds() > (target_minutes * 60)
            
            return {
                'is_breached': is_breached,
                'elapsed_minutes': int(elapsed_time.total_seconds() / 60),
                'target_minutes': target_minutes,
                'breach_margin': int(elapsed_time.total_seconds() / 60) - target_minutes
            }
    
    async def calculate_technician_performance(self, technician_id: str, date_range) -> Dict[str, Any]:
        """Calculate technician SLA performance metrics"""
        # This would typically aggregate multiple ticket calculations
        # For now, return a placeholder implementation
        return {
            'technician_id': technician_id,
            'period_start': date_range.start_date,
            'period_end': date_range.end_date,
            'total_tickets': 0,
            'sla_compliant_tickets': 0,
            'compliance_rate': 0.0,
            'average_response_time': None,
            'average_resolution_time': None
        }
    
    async def _calculate_business_time_remaining(self, start_time: datetime, current_time: datetime, 
                                               target_minutes: int) -> timedelta:
        """Calculate time remaining considering business hours"""
        # Convert to business timezone
        tz = pytz.timezone(self.business_hours['timezone'])
        start_local = start_time.astimezone(tz)
        current_local = current_time.astimezone(tz)
        
        # Calculate business minutes elapsed
        business_minutes_elapsed = self._calculate_business_minutes(start_local, current_local)
        
        # Calculate remaining business minutes
        remaining_minutes = target_minutes - business_minutes_elapsed
        
        if remaining_minutes <= 0:
            return timedelta(0)
        
        # Convert back to timedelta (approximate)
        # In a real implementation, this would calculate the exact time
        # when the remaining business minutes will be reached
        return timedelta(minutes=remaining_minutes)
    
    def _calculate_business_minutes(self, start_time: datetime, end_time: datetime) -> int:
        """Calculate business minutes between two timestamps"""
        if start_time >= end_time:
            return 0
        
        total_minutes = 0
        current = start_time.replace(second=0, microsecond=0)
        
        while current < end_time:
            if self._is_business_time(current):
                total_minutes += 1
            current += timedelta(minutes=1)
        
        return total_minutes
    
    def _is_business_time(self, dt: datetime) -> bool:
        """Check if datetime falls within business hours"""
        # Check if it's a weekday
        if dt.weekday() not in self.business_hours['weekdays']:
            return False
        
        # Check if it's within business hours
        if not (self.business_hours['start_hour'] <= dt.hour < self.business_hours['end_hour']):
            return False
        
        # Check if it's a holiday
        date_key = dt.date()
        if date_key in self.holidays:
            return False
        
        return True
    
    def _determine_risk_level(self, response_sla: Dict[str, Any], resolution_sla: Dict[str, Any]) -> RiskLevel:
        """Determine overall risk level based on SLA status"""
        # If already breached, return critical
        if response_sla.get('is_breached') or resolution_sla.get('is_breached'):
            return RiskLevel.CRITICAL
        
        # Calculate risk based on time remaining
        min_risk_ratio = 1.0
        
        for sla_data in [response_sla, resolution_sla]:
            time_remaining = sla_data.get('time_remaining')
            target_time = sla_data.get('target_time')
            
            if time_remaining and target_time:
                ratio = time_remaining.total_seconds() / target_time.total_seconds()
                min_risk_ratio = min(min_risk_ratio, ratio)
        
        # Determine risk level based on minimum ratio
        if min_risk_ratio > self.risk_thresholds[RiskLevel.LOW]:
            return RiskLevel.LOW
        elif min_risk_ratio > self.risk_thresholds[RiskLevel.MEDIUM]:
            return RiskLevel.MEDIUM
        elif min_risk_ratio > self.risk_thresholds[RiskLevel.HIGH]:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def _parse_timestamp(self, timestamp_str: Optional[str]) -> Optional[datetime]:
        """Parse timestamp string to datetime object"""
        if not timestamp_str:
            return None
        
        try:
            # Try parsing with dateutil (handles various formats)
            dt = parser.parse(timestamp_str)
            
            # Ensure timezone awareness
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=pytz.UTC)
            
            return dt
        except Exception as e:
            self.logger.warning(f"Failed to parse timestamp '{timestamp_str}': {e}")
            return None
    
    def configure_business_hours(self, start_hour: int = 9, end_hour: int = 17, 
                               weekdays: List[int] = None, timezone: str = 'UTC'):
        """Configure business hours settings"""
        self.business_hours = {
            'start_hour': start_hour,
            'end_hour': end_hour,
            'weekdays': weekdays or [0, 1, 2, 3, 4],
            'timezone': timezone
        }
        self.logger.info(f"Updated business hours: {self.business_hours}")
    
    def add_holidays(self, holidays: List[str]):
        """Add holidays (YYYY-MM-DD format)"""
        for holiday_str in holidays:
            try:
                holiday_date = datetime.strptime(holiday_str, '%Y-%m-%d').date()
                self.holidays.add(holiday_date)
            except ValueError as e:
                self.logger.warning(f"Invalid holiday date format '{holiday_str}': {e}")
        
        self.logger.info(f"Added {len(holidays)} holidays")
    
    def configure_risk_thresholds(self, thresholds: Dict[RiskLevel, float]):
        """Configure risk level thresholds"""
        self.risk_thresholds.update(thresholds)
        self.logger.info(f"Updated risk thresholds: {self.risk_thresholds}")


# Strands-compatible tool functions
@tool
async def calculate_sla_status(ticket_data: Dict[str, Any], sla_policy_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate comprehensive SLA status for a ticket
    
    Args:
        ticket_data: Ticket information from SuperOps
        sla_policy_data: SLA policy configuration
        
    Returns:
        Dictionary containing SLA status, time remaining, breach status, and risk level
    """
    calculator = SLACalculatorTool()
    
    # Convert policy data to SLAPolicy object
    sla_policy = SLAPolicy(
        id=sla_policy_data.get('id'),
        name=sla_policy_data.get('name'),
        priority_level=sla_policy_data.get('priority_level'),
        response_time_minutes=sla_policy_data.get('response_time_minutes'),
        resolution_time_hours=sla_policy_data.get('resolution_time_hours'),
        business_hours_only=sla_policy_data.get('business_hours_only', True),
        escalation_rules=sla_policy_data.get('escalation_rules', [])
    )
    
    try:
        sla_status = await calculator.calculate_sla_status(ticket_data, sla_policy)
        
        return {
            "success": True,
            "sla_status": {
                "ticket_id": sla_status.ticket_id,
                "is_response_breached": sla_status.is_response_breached,
                "is_resolution_breached": sla_status.is_resolution_breached,
                "response_time_remaining_minutes": int(sla_status.response_time_remaining.total_seconds() / 60) if sla_status.response_time_remaining else None,
                "resolution_time_remaining_minutes": int(sla_status.resolution_time_remaining.total_seconds() / 60) if sla_status.resolution_time_remaining else None,
                "breach_risk_level": sla_status.breach_risk_level.value,
                "escalation_level": sla_status.escalation_level,
                "last_updated": sla_status.last_updated.isoformat()
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ticket_id": ticket_data.get('id', 'unknown')
        }


@tool
async def calculate_time_remaining(created_at_str: str, target_minutes: int, business_hours_only: bool = True) -> Dict[str, Any]:
    """
    Calculate time remaining until SLA breach
    
    Args:
        created_at_str: Ticket creation timestamp (ISO format)
        target_minutes: Target SLA time in minutes
        business_hours_only: Whether to consider only business hours
        
    Returns:
        Dictionary containing time remaining and breach status
    """
    calculator = SLACalculatorTool()
    
    try:
        created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
        time_remaining = await calculator.calculate_time_remaining(created_at, target_minutes, business_hours_only)
        
        return {
            "success": True,
            "time_remaining_minutes": time_remaining,
            "is_breached": time_remaining <= 0 if time_remaining is not None else False
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@tool
async def check_sla_breach(created_at_str: str, target_minutes: int, response_time_str: Optional[str] = None) -> Dict[str, Any]:
    """
    Check if SLA is breached
    
    Args:
        created_at_str: Ticket creation timestamp (ISO format)
        target_minutes: Target SLA time in minutes
        response_time_str: Response timestamp (ISO format), optional
        
    Returns:
        Dictionary containing breach status and timing information
    """
    calculator = SLACalculatorTool()
    
    try:
        created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
        response_time = None
        if response_time_str:
            response_time = datetime.fromisoformat(response_time_str.replace('Z', '+00:00'))
        
        is_breached = await calculator.is_sla_breached(created_at, target_minutes, response_time)
        
        return {
            "success": True,
            "is_breached": is_breached,
            "created_at": created_at_str,
            "target_minutes": target_minutes,
            "response_time": response_time_str
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }