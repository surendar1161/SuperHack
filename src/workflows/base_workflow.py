"""Base workflow class for all IT operations workflows"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from ..utils.logger import get_logger

class BaseWorkflow(ABC):
    """Base class for all workflows"""

    def __init__(self, name: str):
        self.name = name
        self.logger = get_logger(f"workflow.{name}")
        self.steps = []
        self.current_step = 0

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the workflow"""
        pass

    async def validate_context(self, context: Dict[str, Any]) -> bool:
        """Validate workflow context"""
        return True

    def add_step(self, step_name: str, step_function):
        """Add a step to the workflow"""
        self.steps.append({
            "name": step_name,
            "function": step_function
        })

    async def execute_step(self, step_index: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific workflow step"""
        if step_index >= len(self.steps):
            raise IndexError(f"Step {step_index} does not exist")

        step = self.steps[step_index]
        self.logger.info(f"Executing step: {step['name']}")

        try:
            result = await step["function"](context)
            self.current_step = step_index + 1
            return result
        except Exception as e:
            self.logger.error(f"Step {step['name']} failed: {e}")
            raise
