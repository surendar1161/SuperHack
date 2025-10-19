"""Base agent class for common functionality"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from anthropic import Anthropic

from .config import AgentConfig
from ..utils.logger import get_logger

class BaseAgent(ABC):
    """Base class for all agents"""

    def __init__(self, config: Optional[AgentConfig] = None):
        self.config = config or AgentConfig()
        self.logger = get_logger(self.__class__.__name__)
        self.anthropic_client = Anthropic(api_key=self.config.anthropic_api_key)

    @abstractmethod
    def get_tools(self) -> List[Any]:
        """Return list of tools for this agent"""
        pass

    @abstractmethod
    async def process_request(self, request: str, context: Optional[Dict] = None) -> str:
        """Process a request and return response"""
        pass

    async def run_agent(self, prompt: str) -> str:
        """Run the agent with a given prompt"""
        try:
            response = self.anthropic_client.messages.create(
                model=self.config.model_name,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            return response.content[0].text if response.content else "No response generated"
        except Exception as e:
            self.logger.error(f"Error running agent: {e}")
            raise
