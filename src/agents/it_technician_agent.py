"""
IT Technical Agent - Strands Implementation

Re-export the new Strands-based controller as the main IT Technical Agent.
Legacy custom graph implementation has been removed.
"""

# Import the new Strands-based implementation
from .it_technician_strands_controller import (
    ITTechnicianStrandsController,
    create_it_technician_controller
)

# Main interface for IT Technical Agent
ITTechnician = ITTechnicianStrandsController

__all__ = [
    'ITTechnician',
    'ITTechnicianStrandsController',
    'create_it_technician_controller'
]
