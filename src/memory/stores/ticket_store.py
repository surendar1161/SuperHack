"""Ticket-specific memory store"""

from typing import Dict, Optional
import json
import asyncio
from datetime import datetime
from ...agents.config import AgentConfig
from ...utils.logger import get_logger

class TicketStore:
    """Store for ticket-specific context and information"""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.logger = get_logger(self.__class__.__name__)
        self._ticket_contexts = {}
        self._lock = asyncio.Lock()

    async def store_context(self, ticket_id: str, context: Dict) -> None:
        """Store context for a specific ticket"""
        try:
            async with self._lock:
                self._ticket_contexts[ticket_id] = {
                    "context": context,
                    "updated_at": datetime.now().isoformat(),
                    "version": self._ticket_contexts.get(ticket_id, {}).get("version", 0) + 1
                }

                self.logger.debug(f"Stored context for ticket: {ticket_id}")

        except Exception as e:
            self.logger.error(f"Failed to store ticket context: {e}")
            raise

    async def retrieve_context(self, ticket_id: str) -> Optional[Dict]:
        """Retrieve context for a specific ticket"""
        try:
            async with self._lock:
                ticket_data = self._ticket_contexts.get(ticket_id)
                return ticket_data.get("context") if ticket_data else None

        except Exception as e:
            self.logger.error(f"Failed to retrieve ticket context: {e}")
            return None

    async def update_context(self, ticket_id: str, updates: Dict) -> None:
        """Update existing ticket context"""
        try:
            async with self._lock:
                if ticket_id in self._ticket_contexts:
                    current_context = self._ticket_contexts[ticket_id]["context"]
                    current_context.update(updates)
                    await self.store_context(ticket_id, current_context)
                else:
                    await self.store_context(ticket_id, updates)

        except Exception as e:
            self.logger.error(f"Failed to update ticket context: {e}")
            raise

    async def remove_context(self, ticket_id: str) -> bool:
        """Remove context for a specific ticket"""
        try:
            async with self._lock:
                if ticket_id in self._ticket_contexts:
                    del self._ticket_contexts[ticket_id]
                    self.logger.debug(f"Removed context for ticket: {ticket_id}")
                    return True
                return False

        except Exception as e:
            self.logger.error(f"Failed to remove ticket context: {e}")
            return False

    async def get_all_ticket_ids(self) -> list:
        """Get all stored ticket IDs"""
        async with self._lock:
            return list(self._ticket_contexts.keys())
