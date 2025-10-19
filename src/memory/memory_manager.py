"""Memory manager for storing and retrieving agent interactions and context"""

from typing import Any, Dict, List, Optional
import asyncio
from datetime import datetime, timedelta
from .stores.ticket_store import TicketStore
from .stores.worklog_store import WorklogStore
from .stores.analytics_store import AnalyticsStore
from .models import MemoryEntry, InteractionContext
from ..agents.config import AgentConfig
from ..utils.logger import get_logger

class MemoryManager:
    """Manages memory storage and retrieval for the IT Technician Agent"""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.logger = get_logger(self.__class__.__name__)

        # Initialize memory stores
        self.ticket_store = TicketStore(config)
        self.worklog_store = WorklogStore(config)
        self.analytics_store = AnalyticsStore(config)

        # Memory configuration
        self.max_memory_size = config.memory_max_size
        self.memory_ttl = config.memory_ttl

        # In-memory cache for recent interactions
        self._interaction_cache = []
        self._cache_lock = asyncio.Lock()

    async def store_interaction(self, content: str, context: Optional[Dict] = None) -> str:
        """Store an interaction in memory"""
        try:
            async with self._cache_lock:
                entry = MemoryEntry(
                    id=self._generate_id(),
                    content=content,
                    context=InteractionContext(**context) if context else InteractionContext(),
                    timestamp=datetime.now(),
                    ttl=datetime.now() + timedelta(seconds=self.memory_ttl)
                )

                self._interaction_cache.append(entry)

                # Maintain cache size
                if len(self._interaction_cache) > self.max_memory_size:
                    self._interaction_cache.pop(0)

                self.logger.debug(f"Stored interaction: {entry.id}")
                return entry.id

        except Exception as e:
            self.logger.error(f"Failed to store interaction: {e}")
            raise

    async def retrieve_recent_interactions(self, limit: int = 10) -> List[MemoryEntry]:
        """Retrieve recent interactions from memory"""
        try:
            async with self._cache_lock:
                # Clean expired entries
                current_time = datetime.now()
                self._interaction_cache = [
                    entry for entry in self._interaction_cache
                    if entry.ttl > current_time
                ]

                # Return most recent entries
                return self._interaction_cache[-limit:] if self._interaction_cache else []

        except Exception as e:
            self.logger.error(f"Failed to retrieve interactions: {e}")
            return []

    async def search_interactions(self, query: str, limit: int = 5) -> List[MemoryEntry]:
        """Search interactions by content"""
        try:
            async with self._cache_lock:
                matches = []
                query_lower = query.lower()

                for entry in reversed(self._interaction_cache):
                    if query_lower in entry.content.lower():
                        matches.append(entry)
                        if len(matches) >= limit:
                            break

                return matches

        except Exception as e:
            self.logger.error(f"Failed to search interactions: {e}")
            return []

    async def store_ticket_context(self, ticket_id: str, context: Dict) -> None:
        """Store ticket-specific context"""
        await self.ticket_store.store_context(ticket_id, context)

    async def retrieve_ticket_context(self, ticket_id: str) -> Optional[Dict]:
        """Retrieve ticket-specific context"""
        return await self.ticket_store.retrieve_context(ticket_id)

    async def store_worklog_entry(self, entry: Dict) -> str:
        """Store worklog entry"""
        return await self.worklog_store.store_entry(entry)

    async def retrieve_worklog_entries(self, ticket_id: str) -> List[Dict]:
        """Retrieve worklog entries for a ticket"""
        return await self.worklog_store.retrieve_entries(ticket_id)

    async def store_analytics_data(self, data: Dict) -> None:
        """Store analytics data"""
        await self.analytics_store.store_data(data)

    async def get_memory_stats(self) -> Dict:
        """Get memory usage statistics"""
        async with self._cache_lock:
            active_entries = len([
                entry for entry in self._interaction_cache
                if entry.ttl > datetime.now()
            ])

            return {
                "total_entries": len(self._interaction_cache),
                "active_entries": active_entries,
                "memory_utilization": (len(self._interaction_cache) / self.max_memory_size) * 100,
                "oldest_entry": min([e.timestamp for e in self._interaction_cache]) if self._interaction_cache else None,
                "newest_entry": max([e.timestamp for e in self._interaction_cache]) if self._interaction_cache else None
            }

    async def cleanup_expired_entries(self) -> int:
        """Clean up expired memory entries"""
        async with self._cache_lock:
            initial_count = len(self._interaction_cache)
            current_time = datetime.now()

            self._interaction_cache = [
                entry for entry in self._interaction_cache
                if entry.ttl > current_time
            ]

            cleaned_count = initial_count - len(self._interaction_cache)
            self.logger.info(f"Cleaned up {cleaned_count} expired memory entries")
            return cleaned_count

    def _generate_id(self) -> str:
        """Generate unique ID for memory entries"""
        import uuid
        return str(uuid.uuid4())
