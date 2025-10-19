"""Agents module for IT Technician functionality - Strands Implementation"""

from .it_technician_agent import ITTechnician
from .it_technician_strands_controller import ITTechnicianStrandsController, create_it_technician_controller
from .base_agent import BaseAgent
from .config import AgentConfig

# Maintain backward compatibility
ITTechnicianAgent = ITTechnician

__all__ = [
    "ITTechnician",
    "ITTechnicianAgent",  # For backward compatibility
    "ITTechnicianStrandsController",
    "create_it_technician_controller",
    "BaseAgent",
    "AgentConfig"
]
