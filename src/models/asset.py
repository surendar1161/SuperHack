"""Asset data models"""

from typing import Optional, Dict, Any
from enum import Enum
from pydantic import Field
from .common import BaseModel, TimestampMixin

class AssetType(str, Enum):
    DESKTOP = "desktop"
    LAPTOP = "laptop"
    SERVER = "server"
    PRINTER = "printer"
    NETWORK_DEVICE = "network_device"
    MOBILE_DEVICE = "mobile_device"
    SOFTWARE = "software"

class Asset(TimestampMixin):
    """Asset model"""
    id: str
    name: str
    asset_type: AssetType
    serial_number: Optional[str] = None
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    location: Optional[str] = None
    assigned_to: Optional[str] = None  # User ID
    status: str = "active"  # active, inactive, maintenance, retired
    purchase_date: Optional[str] = None
    warranty_expiry: Optional[str] = None
    specifications: Dict[str, Any] = Field(default_factory=dict)

    def is_under_warranty(self) -> bool:
        """Check if asset is still under warranty"""
        if not self.warranty_expiry:
            return False

        from datetime import datetime
        try:
            expiry_date = datetime.fromisoformat(self.warranty_expiry)
            return expiry_date > datetime.now()
        except:
            return False
