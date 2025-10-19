"""
Memory Manager using mem0 for conversation tracking
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from ..clients.mem0_client import Mem0ClientWrapper
from ..utils.logger import get_logger

logger = get_logger("mem0_memory_manager")


class Mem0MemoryManager:
    """Memory manager that uses mem0 to track conversations and agent responses"""
    
    def __init__(self, mem0_api_key: str):
        self.mem0_client = Mem0ClientWrapper(mem0_api_key)
        self.current_user_id = None
        self.session_metadata = {}
        
    async def start_session(
        self,
        user_id: Optional[str] = None,
        session_type: str = "support_session",
        user_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Start a new conversation session
        
        Args:
            user_id: User identifier (if None, generates one)
            session_type: Type of session (support_session, onboarding, etc.)
            user_info: Information about the user
            
        Returns:
            User ID for the conversation
        """
        try:
            # Generate user ID if not provided
            if not user_id:
                user_id = f"superops_user_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"
            
            # Store session metadata
            self.current_user_id = user_id
            self.session_metadata = {
                "user_id": user_id,
                "session_type": session_type,
                "start_time": datetime.now().isoformat(),
                "user_info": user_info or {},
                "agent_type": "SuperOps IT Technician Agent"
            }
            
            # Store session start in mem0
            session_start_result = await self.mem0_client.store_conversation(
                user_id=user_id,
                user_message="[SESSION_START]",
                agent_response=f"Started {session_type} session for SuperOps IT Technician Agent",
                metadata=self.session_metadata
            )
            
            if session_start_result["success"]:
                logger.info(f"Started new mem0 session: {user_id}")
            else:
                logger.warning(f"Failed to store session start in mem0, but session started: {user_id}")
            
            return user_id
                
        except Exception as e:
            logger.error(f"Error starting mem0 session: {e}")
            # Still return a user ID even if mem0 fails
            user_id = f"fallback_user_{int(datetime.now().timestamp())}"
            self.current_user_id = user_id
            return user_id
    
    async def record_interaction(
        self,
        user_input: str,
        agent_response: str,
        interaction_type: str = "general",
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Record a user-agent interaction
        
        Args:
            user_input: The user's input/request
            agent_response: The agent's response
            interaction_type: Type of interaction (ticket_creation, user_query, etc.)
            metadata: Additional metadata about the interaction
            user_id: User ID (uses current session if not provided)
            
        Returns:
            Dictionary containing the recording result
        """
        try:
            # Use provided user_id or current session
            target_user_id = user_id or self.current_user_id
            
            if not target_user_id:
                await self.start_session()
                target_user_id = self.current_user_id
            
            # Prepare interaction metadata
            interaction_metadata = {
                "interaction_type": interaction_type,
                "timestamp": datetime.now().isoformat(),
                "session_metadata": self.session_metadata,
                **(metadata or {})
            }
            
            # Store in mem0
            result = await self.mem0_client.store_conversation(
                user_id=target_user_id,
                user_message=user_input,
                agent_response=agent_response,
                metadata=interaction_metadata
            )
            
            if result["success"]:
                logger.info(f"Recorded interaction for user {target_user_id} in mem0")
            else:
                logger.warning(f"Failed to record interaction in mem0: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error recording interaction in mem0: {e}")
            return {
                "success": False,
                "error": str(e),
                "user_id": target_user_id
            }
    
    async def get_conversation_memories(
        self,
        user_id: Optional[str] = None,
        limit: Optional[int] = 10
    ) -> Dict[str, Any]:
        """
        Get conversation memories for a user
        
        Args:
            user_id: User ID (uses current session if not provided)
            limit: Maximum number of memories to retrieve
            
        Returns:
            Dictionary containing conversation memories
        """
        try:
            target_user_id = user_id or self.current_user_id
            
            if not target_user_id:
                return {
                    "success": False,
                    "error": "No user ID provided and no current session",
                    "memories": []
                }
            
            result = await self.mem0_client.get_memories(
                user_id=target_user_id,
                limit=limit
            )
            
            if result["success"]:
                logger.info(f"Retrieved {len(result.get('memories', []))} memories for user {target_user_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving memories from mem0: {e}")
            return {
                "success": False,
                "error": str(e),
                "memories": []
            }
    
    async def search_past_interactions(
        self,
        query: str,
        user_id: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search past interactions for a user
        
        Args:
            query: Search query
            user_id: User ID (uses current session if not provided)
            limit: Maximum number of results
            
        Returns:
            Dictionary containing search results
        """
        try:
            target_user_id = user_id or self.current_user_id
            
            if not target_user_id:
                return {
                    "success": False,
                    "error": "No user ID provided and no current session",
                    "results": []
                }
            
            result = await self.mem0_client.search_memories(
                query=query,
                user_id=target_user_id,
                limit=limit
            )
            
            if result["success"]:
                logger.info(f"Found {len(result.get('results', []))} results for query: {query}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error searching memories in mem0: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": []
            }
    
    async def end_session(
        self,
        session_summary: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        End the current session
        
        Args:
            session_summary: Optional summary of the session
            user_id: User ID (uses current session if not provided)
            
        Returns:
            Dictionary containing session end result
        """
        try:
            target_user_id = user_id or self.current_user_id
            
            if not target_user_id:
                return {
                    "success": False,
                    "error": "No active session to end"
                }
            
            # Record session end
            end_metadata = {
                "session_end": datetime.now().isoformat(),
                "session_summary": session_summary,
                "session_type": "session_end"
            }
            
            # Store session end record
            result = await self.mem0_client.store_conversation(
                user_id=target_user_id,
                user_message="[SESSION_END]",
                agent_response=f"Session ended. Summary: {session_summary or 'No summary provided'}",
                metadata=end_metadata
            )
            
            # Clear current session if it matches
            if target_user_id == self.current_user_id:
                self.current_user_id = None
                self.session_metadata = {}
            
            logger.info(f"Ended mem0 session: {target_user_id}")
            
            return {
                "success": True,
                "user_id": target_user_id,
                "message": "Session ended successfully"
            }
            
        except Exception as e:
            logger.error(f"Error ending mem0 session: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def record_interaction_sync(
        self,
        user_input: str,
        agent_response: str,
        interaction_type: str = "general",
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Synchronous version of record_interaction for non-async contexts
        """
        try:
            # Use provided user_id or current session
            target_user_id = user_id or self.current_user_id
            
            if not target_user_id:
                target_user_id = f"sync_user_{int(datetime.now().timestamp())}"
                self.current_user_id = target_user_id
            
            # Prepare interaction metadata
            interaction_metadata = {
                "interaction_type": interaction_type,
                "timestamp": datetime.now().isoformat(),
                "sync_mode": True,
                **(metadata or {})
            }
            
            # Store in mem0 synchronously
            result = self.mem0_client.store_conversation_sync(
                user_id=target_user_id,
                user_message=user_input,
                agent_response=agent_response,
                metadata=interaction_metadata
            )
            
            if result["success"]:
                logger.info(f"Recorded interaction for user {target_user_id} in mem0 (sync)")
            else:
                logger.warning(f"Failed to record interaction in mem0 (sync): {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error recording interaction in mem0 (sync): {e}")
            return {
                "success": False,
                "error": str(e),
                "user_id": target_user_id
            }
    
    def get_current_user_id(self) -> Optional[str]:
        """Get the current user ID"""
        return self.current_user_id
    
    def get_session_metadata(self) -> Dict[str, Any]:
        """Get metadata for the current session"""
        return self.session_metadata.copy()
    
    async def get_user_context(
        self,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get contextual information about a user based on their memory
        
        Args:
            user_id: User ID (uses current session if not provided)
            
        Returns:
            Dictionary containing user context
        """
        try:
            target_user_id = user_id or self.current_user_id
            
            if not target_user_id:
                return {
                    "success": False,
                    "error": "No user ID provided and no current session",
                    "context": {}
                }
            
            # Get recent memories to build context
            memories_result = await self.mem0_client.get_memories(
                user_id=target_user_id,
                limit=20
            )
            
            if not memories_result["success"]:
                return {
                    "success": False,
                    "error": memories_result.get("error"),
                    "context": {}
                }
            
            memories = memories_result.get("memories", [])
            
            # Analyze memories to build context
            context = {
                "user_id": target_user_id,
                "total_memories": len(memories),
                "recent_topics": [],
                "interaction_patterns": {},
                "preferences": {},
                "history_summary": ""
            }
            
            # Extract topics and patterns from memories
            for memory in memories:
                memory_text = memory.get("memory", "")
                
                # Simple keyword extraction for topics
                if "ticket" in memory_text.lower():
                    context["recent_topics"].append("ticket_management")
                if "technician" in memory_text.lower():
                    context["recent_topics"].append("user_management")
                if "contract" in memory_text.lower():
                    context["recent_topics"].append("contract_management")
                if "alert" in memory_text.lower():
                    context["recent_topics"].append("system_monitoring")
            
            # Remove duplicates and limit topics
            context["recent_topics"] = list(set(context["recent_topics"]))[:5]
            
            # Build history summary
            if memories:
                context["history_summary"] = f"User has {len(memories)} interactions focusing on: {', '.join(context['recent_topics'])}"
            
            return {
                "success": True,
                "user_id": target_user_id,
                "context": context
            }
            
        except Exception as e:
            logger.error(f"Error getting user context from mem0: {e}")
            return {
                "success": False,
                "error": str(e),
                "context": {}
            }