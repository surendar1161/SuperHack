"""
SLA Service Interfaces

Defines abstract interfaces for SLA management components.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

from .models import (
    SLAPolicy, 
    TicketSLAStatus, 
    TechnicianSLAMetrics, 
    SLABreach, 
    SLAReport,
    DateRange
)


class ISLADataAccess(ABC):
    """Interface for SLA data access operations"""
    
    @abstractmethod
    async def fetch_sla_policies_from_api(self) -> List[SLAPolicy]:
        """Fetch SLA policies from SuperOps API"""
        pass
    
    @abstractmethod
    async def get_cached_sla_policies(self) -> List[SLAPolicy]:
        """Get SLA policies from cache"""
        pass
    
    @abstractmethod
    async def fetch_ticket_sla_data(self, ticket_id: str) -> Dict[str, Any]:
        """Fetch ticket SLA data from SuperOps API"""
        pass
    
    @abstractmethod
    async def fetch_technician_metrics(self, technician_id: str, date_range: DateRange) -> Dict[str, Any]:
        """Fetch technician SLA metrics from SuperOps API"""
        pass
    
    @abstractmethod
    async def update_sla_cache(self, policies: List[SLAPolicy]) -> None:
        """Update SLA policies in cache"""
        pass
    
    @abstractmethod
    async def get_sla_policy_by_priority(self, priority: str) -> Optional[SLAPolicy]:
        """Get SLA policy by ticket priority"""
        pass


class ISLACalculator(ABC):
    """Interface for SLA calculation operations"""
    
    @abstractmethod
    async def calculate_sla_status(self, ticket_data: Dict[str, Any], sla_policy: SLAPolicy) -> TicketSLAStatus:
        """Calculate current SLA status for a ticket"""
        pass
    
    @abstractmethod
    async def calculate_time_remaining(self, created_at: datetime, target_minutes: int, business_hours_only: bool = True) -> Optional[int]:
        """Calculate time remaining until SLA breach"""
        pass
    
    @abstractmethod
    async def is_sla_breached(self, created_at: datetime, target_minutes: int, response_time: Optional[datetime] = None) -> bool:
        """Check if SLA is breached"""
        pass
    
    @abstractmethod
    async def calculate_technician_performance(self, technician_id: str, date_range: DateRange) -> TechnicianSLAMetrics:
        """Calculate technician SLA performance metrics"""
        pass


class ISLAMonitoring(ABC):
    """Interface for SLA monitoring operations"""
    
    @abstractmethod
    async def start_monitoring(self) -> None:
        """Start SLA monitoring service"""
        pass
    
    @abstractmethod
    async def stop_monitoring(self) -> None:
        """Stop SLA monitoring service"""
        pass
    
    @abstractmethod
    async def detect_potential_breaches(self) -> List[TicketSLAStatus]:
        """Detect tickets at risk of SLA breach"""
        pass
    
    @abstractmethod
    async def process_sla_breach(self, breach: SLABreach) -> None:
        """Process an SLA breach incident"""
        pass
    
    @abstractmethod
    async def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        pass


class IAlertManager(ABC):
    """Interface for SLA alert management"""
    
    @abstractmethod
    async def send_breach_alert(self, breach: SLABreach) -> None:
        """Send SLA breach alert"""
        pass
    
    @abstractmethod
    async def send_warning_alert(self, ticket_status: TicketSLAStatus) -> None:
        """Send SLA warning alert"""
        pass
    
    @abstractmethod
    async def escalate_breach(self, breach: SLABreach) -> None:
        """Escalate SLA breach to higher level"""
        pass
    
    @abstractmethod
    async def configure_alert_rules(self, rules: List[Dict[str, Any]]) -> None:
        """Configure alert rules"""
        pass
    
    @abstractmethod
    async def get_alert_history(self, date_range: DateRange) -> List[Dict[str, Any]]:
        """Get alert history for date range"""
        pass


class ISLAReporting(ABC):
    """Interface for SLA reporting operations"""
    
    @abstractmethod
    async def generate_sla_report(self, date_range: DateRange, filters: Dict[str, Any] = None) -> SLAReport:
        """Generate comprehensive SLA report"""
        pass
    
    @abstractmethod
    async def generate_technician_report(self, technician_id: str, date_range: DateRange) -> TechnicianSLAMetrics:
        """Generate technician-specific SLA report"""
        pass
    
    @abstractmethod
    async def export_report(self, report: SLAReport, format: str = "json") -> str:
        """Export report in specified format"""
        pass
    
    @abstractmethod
    async def schedule_report(self, report_config: Dict[str, Any]) -> str:
        """Schedule recurring report generation"""
        pass


class ISLAService(ABC):
    """Main interface for SLA service operations"""
    
    @abstractmethod
    async def get_sla_policies(self) -> List[SLAPolicy]:
        """Get all SLA policies"""
        pass
    
    @abstractmethod
    async def get_ticket_sla_status(self, ticket_id: str) -> TicketSLAStatus:
        """Get SLA status for specific ticket"""
        pass
    
    @abstractmethod
    async def get_technician_sla_performance(self, technician_id: str, date_range: DateRange) -> TechnicianSLAMetrics:
        """Get technician SLA performance"""
        pass
    
    @abstractmethod
    async def monitor_sla_breaches(self) -> List[SLABreach]:
        """Monitor and return current SLA breaches"""
        pass
    
    @abstractmethod
    async def generate_sla_report(self, date_range: DateRange, filters: Dict[str, Any] = None) -> SLAReport:
        """Generate SLA performance report"""
        pass
    
    @abstractmethod
    async def configure_sla_monitoring(self, config: Dict[str, Any]) -> None:
        """Configure SLA monitoring parameters"""
        pass


class ISLAConfiguration(ABC):
    """Interface for SLA configuration management"""
    
    @abstractmethod
    async def validate_sla_policy(self, policy: SLAPolicy) -> bool:
        """Validate SLA policy configuration"""
        pass
    
    @abstractmethod
    async def save_sla_policy(self, policy: SLAPolicy) -> None:
        """Save SLA policy configuration"""
        pass
    
    @abstractmethod
    async def delete_sla_policy(self, policy_id: str) -> None:
        """Delete SLA policy"""
        pass
    
    @abstractmethod
    async def get_configuration(self) -> Dict[str, Any]:
        """Get current SLA configuration"""
        pass
    
    @abstractmethod
    async def update_configuration(self, config: Dict[str, Any]) -> None:
        """Update SLA configuration"""
        pass