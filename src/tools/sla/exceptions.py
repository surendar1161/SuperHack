"""
SLA-specific exception classes

Defines custom exceptions for SLA management operations.
"""


class SLAError(Exception):
    """Base exception for all SLA-related errors"""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "SLA_ERROR"
        self.details = details or {}
    
    def __str__(self):
        if self.details:
            return f"{self.message} (Code: {self.error_code}, Details: {self.details})"
        return f"{self.message} (Code: {self.error_code})"


class SLAPolicyNotFoundError(SLAError):
    """Raised when an SLA policy cannot be found"""
    
    def __init__(self, policy_id: str = None, priority: str = None):
        if policy_id:
            message = f"SLA policy not found: {policy_id}"
            details = {"policy_id": policy_id}
        elif priority:
            message = f"No SLA policy found for priority: {priority}"
            details = {"priority": priority}
        else:
            message = "SLA policy not found"
            details = {}
        
        super().__init__(
            message=message,
            error_code="SLA_POLICY_NOT_FOUND",
            details=details
        )


class SLACalculationError(SLAError):
    """Raised when SLA calculations fail"""
    
    def __init__(self, ticket_id: str, calculation_type: str, reason: str):
        message = f"SLA calculation failed for ticket {ticket_id}: {reason}"
        super().__init__(
            message=message,
            error_code="SLA_CALCULATION_ERROR",
            details={
                "ticket_id": ticket_id,
                "calculation_type": calculation_type,
                "reason": reason
            }
        )


class SLABreachError(SLAError):
    """Raised when SLA breach processing fails"""
    
    def __init__(self, ticket_id: str, breach_type: str, reason: str):
        message = f"SLA breach processing failed for ticket {ticket_id}: {reason}"
        super().__init__(
            message=message,
            error_code="SLA_BREACH_ERROR",
            details={
                "ticket_id": ticket_id,
                "breach_type": breach_type,
                "reason": reason
            }
        )


class SLAConfigurationError(SLAError):
    """Raised when SLA configuration is invalid"""
    
    def __init__(self, config_field: str, reason: str):
        message = f"Invalid SLA configuration for {config_field}: {reason}"
        super().__init__(
            message=message,
            error_code="SLA_CONFIGURATION_ERROR",
            details={
                "config_field": config_field,
                "reason": reason
            }
        )


class SLADataAccessError(SLAError):
    """Raised when SLA data access operations fail"""
    
    def __init__(self, operation: str, reason: str, source: str = None):
        message = f"SLA data access failed for {operation}: {reason}"
        details = {"operation": operation, "reason": reason}
        if source:
            details["source"] = source
        
        super().__init__(
            message=message,
            error_code="SLA_DATA_ACCESS_ERROR",
            details=details
        )


class SLAMonitoringError(SLAError):
    """Raised when SLA monitoring operations fail"""
    
    def __init__(self, monitoring_type: str, reason: str):
        message = f"SLA monitoring failed for {monitoring_type}: {reason}"
        super().__init__(
            message=message,
            error_code="SLA_MONITORING_ERROR",
            details={
                "monitoring_type": monitoring_type,
                "reason": reason
            }
        )


class SLAAlertError(SLAError):
    """Raised when SLA alert operations fail"""
    
    def __init__(self, alert_type: str, reason: str, alert_id: str = None):
        message = f"SLA alert failed for {alert_type}: {reason}"
        details = {"alert_type": alert_type, "reason": reason}
        if alert_id:
            details["alert_id"] = alert_id
        
        super().__init__(
            message=message,
            error_code="SLA_ALERT_ERROR",
            details=details
        )


class SLAReportError(SLAError):
    """Raised when SLA report generation fails"""
    
    def __init__(self, report_type: str, reason: str, period: str = None):
        message = f"SLA report generation failed for {report_type}: {reason}"
        details = {"report_type": report_type, "reason": reason}
        if period:
            details["period"] = period
        
        super().__init__(
            message=message,
            error_code="SLA_REPORT_ERROR",
            details=details
        )


class SLAValidationError(SLAError):
    """Raised when SLA data validation fails"""
    
    def __init__(self, field: str, value: str, reason: str):
        message = f"SLA validation failed for {field}='{value}': {reason}"
        super().__init__(
            message=message,
            error_code="SLA_VALIDATION_ERROR",
            details={
                "field": field,
                "value": value,
                "reason": reason
            }
        )