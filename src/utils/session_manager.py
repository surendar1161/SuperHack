"""
Session Manager Utility for proper aiohttp session cleanup
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from ..agents.config import AgentConfig
from ..clients.superops_client import SuperOpsClient
from ..utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def get_superops_client() -> AsyncGenerator[SuperOpsClient, None]:
    """
    Async context manager for SuperOps client with proper session cleanup
    
    Usage:
        async with get_superops_client() as client:
            result = await client.some_operation()
    """
    config = AgentConfig()
    client = SuperOpsClient(config)
    
    try:
        await client.connect()
        yield client
    finally:
        try:
            if hasattr(client, 'close'):
                await client.close()
            elif hasattr(client, 'session') and client.session and not client.session.closed:
                await client.session.close()
                logger.debug("SuperOps client session closed properly")
        except Exception as e:
            logger.warning(f"Error during client cleanup: {e}")


async def with_superops_client(func, *args, **kwargs):
    """
    Helper function to execute a function with a properly managed SuperOps client
    
    Args:
        func: Async function that takes a client as first parameter
        *args: Additional arguments to pass to the function
        **kwargs: Additional keyword arguments to pass to the function
    
    Returns:
        Result of the function execution
    """
    async with get_superops_client() as client:
        return await func(client, *args, **kwargs)


class SessionManager:
    """
    Session manager for tracking and cleaning up multiple client sessions
    """
    
    def __init__(self):
        self.active_sessions = []
        self.logger = get_logger(self.__class__.__name__)
    
    def register_session(self, session):
        """Register a session for cleanup"""
        self.active_sessions.append(session)
    
    async def cleanup_all(self):
        """Clean up all registered sessions"""
        cleanup_tasks = []
        
        for session in self.active_sessions:
            if session and not session.closed:
                cleanup_tasks.append(session.close())
        
        if cleanup_tasks:
            try:
                await asyncio.gather(*cleanup_tasks, return_exceptions=True)
                self.logger.info(f"Cleaned up {len(cleanup_tasks)} sessions")
            except Exception as e:
                self.logger.warning(f"Error during session cleanup: {e}")
        
        self.active_sessions.clear()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup_all()


# Global session manager instance
_global_session_manager = SessionManager()


def get_session_manager() -> SessionManager:
    """Get the global session manager instance"""
    return _global_session_manager