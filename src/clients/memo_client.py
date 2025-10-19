"""
memO Client for conversation memory management
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
import aiohttp
import requests
from ..utils.logger import get_logger

logger = get_logger("memo_client")


class MemoClient:
    """Client for interacting with memO API for conversation memory"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.memo.ai"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
    async def store_conversation(
        self,
        conversation_id: str,
        user_message: str,
        agent_response: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store a conversation exchange in memO
        
        Args:
            conversation_id: Unique identifier for the conversation
            user_message: The user's input message
            agent_response: The agent's response
            metadata: Additional metadata about the conversation
            
        Returns:
            Dictionary containing the storage result
        """
        try:
            timestamp = datetime.now().isoformat()
            
            # Prepare the conversation data
            conversation_data = {
                "conversation_id": conversation_id,
                "timestamp": timestamp,
                "user_message": user_message,
                "agent_response": agent_response,
                "metadata": metadata or {}
            }
            
            # Store in memO
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/conversations",
                    headers=self.headers,
                    json=conversation_data
                ) as response:
                    
                    if response.status == 200 or response.status == 201:
                        result = await response.json()
                        logger.info(f"Successfully stored conversation {conversation_id} in memO")
                        return {
                            "success": True,
                            "conversation_id": conversation_id,
                            "memo_id": result.get("id"),
                            "timestamp": timestamp
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to store conversation in memO: {response.status} - {error_text}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}",
                            "conversation_id": conversation_id
                        }
                        
        except Exception as e:
            logger.error(f"Error storing conversation in memO: {e}")
            return {
                "success": False,
                "error": str(e),
                "conversation_id": conversation_id
            }
    
    async def retrieve_conversation_history(
        self,
        conversation_id: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Retrieve conversation history from memO
        
        Args:
            conversation_id: Unique identifier for the conversation
            limit: Maximum number of messages to retrieve
            
        Returns:
            Dictionary containing the conversation history
        """
        try:
            params = {
                "conversation_id": conversation_id,
                "limit": limit
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/conversations",
                    headers=self.headers,
                    params=params
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Retrieved {len(result.get('conversations', []))} messages for conversation {conversation_id}")
                        return {
                            "success": True,
                            "conversation_id": conversation_id,
                            "conversations": result.get("conversations", []),
                            "total_count": result.get("total_count", 0)
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to retrieve conversation history: {response.status} - {error_text}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}",
                            "conversation_id": conversation_id
                        }
                        
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {e}")
            return {
                "success": False,
                "error": str(e),
                "conversation_id": conversation_id
            }
    
    async def search_conversations(
        self,
        query: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search conversations in memO
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            Dictionary containing search results
        """
        try:
            search_data = {
                "query": query,
                "limit": limit
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/search",
                    headers=self.headers,
                    json=search_data
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Found {len(result.get('results', []))} results for query: {query}")
                        return {
                            "success": True,
                            "query": query,
                            "results": result.get("results", []),
                            "total_count": result.get("total_count", 0)
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to search conversations: {response.status} - {error_text}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}",
                            "query": query
                        }
                        
        except Exception as e:
            logger.error(f"Error searching conversations: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    def store_conversation_sync(
        self,
        conversation_id: str,
        user_message: str,
        agent_response: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Synchronous version of store_conversation for non-async contexts
        """
        try:
            timestamp = datetime.now().isoformat()
            
            conversation_data = {
                "conversation_id": conversation_id,
                "timestamp": timestamp,
                "user_message": user_message,
                "agent_response": agent_response,
                "metadata": metadata or {}
            }
            
            response = requests.post(
                f"{self.base_url}/conversations",
                headers=self.headers,
                json=conversation_data,
                timeout=30
            )
            
            if response.status_code == 200 or response.status_code == 201:
                result = response.json()
                logger.info(f"Successfully stored conversation {conversation_id} in memO (sync)")
                return {
                    "success": True,
                    "conversation_id": conversation_id,
                    "memo_id": result.get("id"),
                    "timestamp": timestamp
                }
            else:
                logger.error(f"Failed to store conversation in memO (sync): {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "conversation_id": conversation_id
                }
                
        except Exception as e:
            logger.error(f"Error storing conversation in memO (sync): {e}")
            return {
                "success": False,
                "error": str(e),
                "conversation_id": conversation_id
            }
    
    async def create_memory_context(
        self,
        conversation_id: str,
        context_type: str = "support_session"
    ) -> Dict[str, Any]:
        """
        Create a memory context for a conversation session
        
        Args:
            conversation_id: Unique identifier for the conversation
            context_type: Type of context (e.g., 'support_session', 'onboarding', 'troubleshooting')
            
        Returns:
            Dictionary containing the context creation result
        """
        try:
            context_data = {
                "conversation_id": conversation_id,
                "context_type": context_type,
                "created_at": datetime.now().isoformat(),
                "metadata": {
                    "agent_type": "SuperOps IT Technician",
                    "session_start": datetime.now().isoformat()
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/contexts",
                    headers=self.headers,
                    json=context_data
                ) as response:
                    
                    if response.status == 200 or response.status == 201:
                        result = await response.json()
                        logger.info(f"Created memory context for conversation {conversation_id}")
                        return {
                            "success": True,
                            "conversation_id": conversation_id,
                            "context_id": result.get("id"),
                            "context_type": context_type
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to create memory context: {response.status} - {error_text}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}",
                            "conversation_id": conversation_id
                        }
                        
        except Exception as e:
            logger.error(f"Error creating memory context: {e}")
            return {
                "success": False,
                "error": str(e),
                "conversation_id": conversation_id
            }