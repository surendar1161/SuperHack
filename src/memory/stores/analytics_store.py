"""Analytics data store"""

from typing import Dict, List
import asyncio
from datetime import datetime
from ...agents.config import AgentConfig
from ...utils.logger import get_logger

class AnalyticsStore:
    """Store for analytics data and metrics"""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.logger = get_logger(self.__class__.__name__)
        self._analytics_data = {}
        self._lock = asyncio.Lock()

    async def store_data(self, data: Dict) -> None:
        """Store analytics data"""
        try:
            async with self._lock:
                data_type = data.get("type", "general")
                timestamp = datetime.now().isoformat()

                if data_type not in self._analytics_data:
                    self._analytics_data[data_type] = []

                entry = {
                    "data": data,
                    "timestamp": timestamp,
                    "id": self._generate_data_id()
                }

                self._analytics_data[data_type].append(entry)

                # Keep only recent entries (last 1000 per type)
                if len(self._analytics_data[data_type]) > 1000:
                    self._analytics_data[data_type] = self._analytics_data[data_type][-1000:]

                self.logger.debug(f"Stored analytics data: {data_type}")

        except Exception as e:
            self.logger.error(f"Failed to store analytics data: {e}")
            raise

    async def retrieve_data(self, data_type: str, limit: int = 100) -> List[Dict]:
        """Retrieve analytics data by type"""
        try:
            async with self._lock:
                entries = self._analytics_data.get(data_type, [])
                return entries[-limit:] if entries else []

        except Exception as e:
            self.logger.error(f"Failed to retrieve analytics data: {e}")
            return []

    def _generate_data_id(self) -> str:
        """Generate unique ID for analytics entries"""
        import uuid
        return str(uuid.uuid4())
