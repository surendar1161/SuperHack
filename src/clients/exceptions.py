"""SuperOps API client exceptions"""

class SuperOpsAPIError(Exception):
    """Base exception for SuperOps API errors"""
    pass

class AuthenticationError(SuperOpsAPIError):
    """Authentication failed"""
    pass

class RateLimitError(SuperOpsAPIError):
    """Rate limit exceeded"""
    pass

class ValidationError(SuperOpsAPIError):
    """Request validation failed"""
    pass

class NotFoundError(SuperOpsAPIError):
    """Resource not found"""
    pass