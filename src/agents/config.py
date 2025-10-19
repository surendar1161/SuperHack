"""Agent configuration settings"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class AgentConfig(BaseSettings):
    """Configuration for the IT Technician Agent"""

    # API Configuration
    superops_api_key: str = ""
    superops_api_url: str = "https://api.superops.ai/msp/api"  # Updated to MSP API endpoint
    superops_customer_subdomain: Optional[str] = None  # Required for SuperOps API (e.g., 'hackathon')
    superops_tenant_id: Optional[str] = None  # Not required for SuperOps API

    # Anthropic Configuration
    anthropic_api_key: str = ""

    # Agent Model Configuration
    model_name: str = Field(default="claude-3-5-sonnet-20241022", alias="AGENT_MODEL")
    temperature: float = Field(default=0.7, alias="AGENT_TEMPERATURE")
    max_tokens: int = Field(default=1024, alias="AGENT_MAX_TOKENS")

    # Database Configuration
    database_url: str = "sqlite:///./technician_agent.db"

    # Memory Configuration
    memory_ttl: int = 3600
    memory_max_size: int = 1000

    # Logging Configuration
    log_level: str = "INFO"
    log_file: Optional[str] = None

    # mem0 Configuration
    mem0_api_key: str = ""
    mem0_enabled: bool = True

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }
