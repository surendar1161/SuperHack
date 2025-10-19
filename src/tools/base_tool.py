"""Base tool class for all SuperOps IT Technician Agent tools"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime
from ..utils.logger import get_logger


class BaseTool(ABC):
    """
    Abstract base class for all tools in the SuperOps IT Technician Agent
    
    Provides common functionality and interface for all tools
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = get_logger(f"tool.{name}")
        self.call_count = 0
        self.last_call = None
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool with given parameters
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            Dictionary containing execution results
        """
        pass
    
    async def __call__(self, **kwargs) -> Dict[str, Any]:
        """
        Call the tool (wrapper around execute)
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            Dictionary containing execution results
        """
        self.call_count += 1
        self.last_call = datetime.now()
        
        self.logger.info(f"Executing tool '{self.name}' (call #{self.call_count})")
        
        try:
            result = await self.execute(**kwargs)
            self.logger.info(f"Tool '{self.name}' executed successfully")
            return result
        except Exception as e:
            self.logger.error(f"Tool '{self.name}' execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool_name": self.name,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get tool information
        
        Returns:
            Dictionary containing tool metadata
        """
        return {
            "name": self.name,
            "description": self.description,
            "call_count": self.call_count,
            "last_call": self.last_call.isoformat() if self.last_call else None
        }
    
    def reset_stats(self):
        """Reset tool statistics"""
        self.call_count = 0
        self.last_call = None
        self.logger.info(f"Reset statistics for tool '{self.name}'")


class ToolError(Exception):
    """Base exception for tool-related errors"""
    
    def __init__(self, message: str, tool_name: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.tool_name = tool_name
        self.details = details or {}
        self.timestamp = datetime.now()


class ToolValidationError(ToolError):
    """Exception for tool parameter validation errors"""
    pass


class ToolExecutionError(ToolError):
    """Exception for tool execution errors"""
    pass


class ToolConfigurationError(ToolError):
    """Exception for tool configuration errors"""
    pass