"""Common base models and mixins"""

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel as PydanticBaseModel, Field
from enum import Enum

class BaseModel(PydanticBaseModel):
    """Base model with common configuration"""

    class Config:
        use_enum_values = True
        validate_assignment = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TimestampMixin(BaseModel):
    """Mixin for models that need timestamp fields"""
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    def touch(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.now()
