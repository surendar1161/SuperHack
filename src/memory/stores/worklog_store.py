"""Worklog memory store"""

from typing import Dict, List
import asyncio
from datetime import datetime
from ...agents.config import AgentConfig
from ...utils.logger import get_logger

class WorklogStore:
    """Store for worklog entries and time tracking"""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.logger = get_logger(self.__class__.__name__)
        self._worklog_entries = {}
        self._lock = asyncio.Lock()

    async def store_entry(self, entry: Dict) -> str:
        """Store a worklog entry"""
        try:
            async with self._lock:
                entry_id = self._generate_entry_id()
                ticket_id = entry.get("ticket_id")

                if ticket_id not in self._worklog_entries:
                    self._worklog_entries[ticket_id] = []

                entry_data = {
                    "id": entry_id,
                    "ticket_id": ticket_id,
                    "activity_type": entry.get("activity_type"),
                    "description": entry.get("description"),
                    "time_spent": entry.get("time_spent", 0),
                    "timestamp": entry.get("timestamp", datetime.now().isoformat()),
                    "user_id": entry.get("user_id")
                }

                self._worklog_entries[ticket_id].append(entry_data)

                self.logger.debug(f"Stored worklog entry: {entry_id} for ticket: {ticket_id}")
                return entry_id

        except Exception as e:
            self.logger.error(f"Failed to store worklog entry: {e}")
            raise

    async def retrieve_entries(self, ticket_id: str) -> List[Dict]:
        """Retrieve all worklog entries for a ticket"""
        try:
            async with self._lock:
                return self._worklog_entries.get(ticket_id, [])

        except Exception as e:
            self.logger.error(f"Failed to retrieve worklog entries: {e}")
            return []

    async def get_total_time_spent(self, ticket_id: str) -> float:
        """Get total time spent on a ticket"""
        entries = await self.retrieve_entries(ticket_id)
        return sum(entry.get("time_spent", 0) for entry in entries)

    def _generate_entry_id(self) -> str:
        """Generate unique ID for worklog entries"""
        import uuid
        return str(uuid.uuid4())
