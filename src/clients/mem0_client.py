"""
mem0 Client for conversation memory management
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from mem0 import MemoryClient
from ..utils.logger import get_logger

logger = get_logger("mem0_client")


class Mem0ClientWrapper:
    """Wrapper for mem0 MemoryClient with SuperOps-specific functionality"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = MemoryClient(api_key=api_key)
        
    async def store_conversation(
        self,
        user_id: str,
        user_message: str,
        agent_response: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store a conversation exchange in mem0
        
        Args:
            user_id: Unique identifier for the user/session
            user_message: The user's input message
            agent_response: The agent's response
            metadata: Additional metadata about the conversation
            
        Returns:
            Dictionary containing the storage result
        """
        try:
            # Prepare messages in mem0 format
            messages = [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": agent_response}
            ]
            
            # Add metadata to the messages if provided
            if metadata:
                # Include metadata in the assistant message for context
                enhanced_response = f"{agent_response}\n\n[Metadata: {json.dumps(metadata)}]"
                messages[1]["content"] = enhanced_response
            
            # Store in mem0
            result = self.client.add(messages, user_id=user_id)
            
            logger.info(f"Successfully stored conversation for user {user_id} in mem0")
            
            return {
                "success": True,
                "user_id": user_id,
                "mem0_result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error storing conversation in mem0: {e}")
            return {
                "success": False,
                "error": str(e),
                "user_id": user_id
            }
    
    async def get_memories(
        self,
        user_id: str,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get memories for a user from mem0 using API v2 format
        
        Args:
            user_id: Unique identifier for the user/session
            limit: Maximum number of memories to retrieve
            
        Returns:
            Dictionary containing the memories
        """
        try:
            # Use API v2 format with proper filters
            filters = {"OR": [{"user_id": user_id}]}
            memories = self.client.get_all(version="v2", filters=filters)
            
            # Apply limit if specified
            if limit and len(memories) > limit:
                memories = memories[:limit]
            
            logger.info(f"Retrieved {len(memories)} memories for user {user_id}")
            
            return {
                "success": True,
                "user_id": user_id,
                "memories": memories,
                "total_count": len(memories)
            }
            
        except Exception as e:
            logger.error(f"Error retrieving memories from mem0: {e}")
            return {
                "success": False,
                "error": str(e),
                "user_id": user_id,
                "memories": []
            }
    
    async def search_memories(
        self,
        query: str,
        user_id: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search memories for a user using API v2 format
        
        Args:
            query: Search query
            user_id: Unique identifier for the user/session
            limit: Maximum number of results to return
            
        Returns:
            Dictionary containing search results
        """
        try:
            # Use API v2 format with proper filters
            filters = {"OR": [{"user_id": user_id}]}
            results = self.client.search(query, version="v2", filters=filters, limit=limit)
            
            logger.info(f"Found {len(results)} results for query '{query}' for user {user_id}")
            
            return {
                "success": True,
                "query": query,
                "user_id": user_id,
                "results": results,
                "total_count": len(results)
            }
            
        except Exception as e:
            logger.error(f"Error searching memories in mem0: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "user_id": user_id,
                "results": []
            }
    
    async def update_memory(
        self,
        memory_id: str,
        data: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Update a specific memory
        
        Args:
            memory_id: ID of the memory to update
            data: New data for the memory
            user_id: User ID associated with the memory
            
        Returns:
            Dictionary containing update result
        """
        try:
            result = self.client.update(memory_id=memory_id, data=data, user_id=user_id)
            
            logger.info(f"Updated memory {memory_id} for user {user_id}")
            
            return {
                "success": True,
                "memory_id": memory_id,
                "user_id": user_id,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error updating memory in mem0: {e}")
            return {
                "success": False,
                "error": str(e),
                "memory_id": memory_id,
                "user_id": user_id
            }
    
    async def delete_memory(
        self,
        memory_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Delete a specific memory
        
        Args:
            memory_id: ID of the memory to delete
            user_id: User ID associated with the memory
            
        Returns:
            Dictionary containing deletion result
        """
        try:
            result = self.client.delete(memory_id=memory_id, user_id=user_id)
            
            logger.info(f"Deleted memory {memory_id} for user {user_id}")
            
            return {
                "success": True,
                "memory_id": memory_id,
                "user_id": user_id,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error deleting memory in mem0: {e}")
            return {
                "success": False,
                "error": str(e),
                "memory_id": memory_id,
                "user_id": user_id
            }
    
    async def get_memory_history(
        self,
        user_id: str,
        memory_id: str
    ) -> Dict[str, Any]:
        """
        Get history of a specific memory
        
        Args:
            user_id: User ID
            memory_id: Memory ID
            
        Returns:
            Dictionary containing memory history
        """
        try:
            history = self.client.history(memory_id=memory_id, user_id=user_id)
            
            logger.info(f"Retrieved history for memory {memory_id} for user {user_id}")
            
            return {
                "success": True,
                "memory_id": memory_id,
                "user_id": user_id,
                "history": history
            }
            
        except Exception as e:
            logger.error(f"Error retrieving memory history from mem0: {e}")
            return {
                "success": False,
                "error": str(e),
                "memory_id": memory_id,
                "user_id": user_id,
                "history": []
            }
    
    def store_conversation_sync(
        self,
        user_id: str,
        user_message: str,
        agent_response: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Synchronous version of store_conversation for non-async contexts
        """
        try:
            # Prepare messages in mem0 format
            messages = [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": agent_response}
            ]
            
            # Add metadata if provided
            if metadata:
                enhanced_response = f"{agent_response}\n\n[Metadata: {json.dumps(metadata)}]"
                messages[1]["content"] = enhanced_response
            
            # Store in mem0 synchronously
            result = self.client.add(messages, user_id=user_id)
            
            logger.info(f"Successfully stored conversation for user {user_id} in mem0 (sync)")
            
            return {
                "success": True,
                "user_id": user_id,
                "mem0_result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error storing conversation in mem0 (sync): {e}")
            return {
                "success": False,
                "error": str(e),
                "user_id": user_id
            }