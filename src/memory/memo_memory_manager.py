"""
Memory Manager using memO for conversation tracking
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from ..clients.memo_client import MemoClient
from ..utils.logger import get_logger

logger = get_logger("memo_memory_manager")


class MemoMemoryManager:
    """Memory manager that uses memO to track conversations and agent responses"""
    
    def __init__(self, memo_api_key: str, memo_base_url: str = "https://api.memo.ai"):
        self.memo_client = MemoClient(memo_api_key, memo_base_url)
        self.current_session_id = None
        self.session_metadata = {}
        
    async def start_session(
        self,
        session_type: str = "support_session",
        user_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Start a new conversation session
        
        Args:
            session_type: Type of session (support_session, onboarding, etc.)
            user_info: Information about the user
            
        Returns:
            Session ID for the conversation
        """
        try:
            # Generate unique session ID
            session_id = f"session_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"
            
            # Store session metadata
            self.current_session_id = session_id
            self.session_metadata = {
                "session_id": session_id,
                "session_type": session_type,
                "start_time": datetime.now().isoformat(),
                "user_info": user_info or {},
                "agent_type": "SuperOps IT Technician Agent"
            }
            
            # Create memory context in memO
            context_result = await self.memo_client.create_memory_context(
                conversation_id=session_id,
                context_type=session_type
            )
            
            if context_result["success"]:
                logger.info(f"Started new session: {session_id}")
                return session_id
            else:
                logger.warning(f"Failed to create memO context, but session started: {session_id}")
                return session_id
                
        except Exception as e:
            logger.error(f"Error starting session: {e}")
            # Still return a session ID even if memO fails
            session_id = f"session_{int(datetime.now().timestamp())}_fallback"
            self.current_session_id = session_id
            return session_id
    
    async def record_interaction(
        self,
        user_input: str,
        agent_response: str,
        interaction_type: str = "general",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Record a user-agent interaction
        
        Args:
            user_input: The user's input/request
            agent_response: The agent's response
            interaction_type: Type of interaction (ticket_creation, user_query, etc.)
            metadata: Additional metadata about the interaction
            
        Returns:
            Dictionary containing the recording result
        """
        try:
            # Use current session or create a new one
            if not self.current_session_id:
                await self.start_session()
            
            # Prepare interaction metadata
            interaction_metadata = {
                "interaction_type": interaction_type,
                "timestamp": datetime.now().isoformat(),
                "session_metadata": self.session_metadata,
                **(metadata or {})
            }
            
            # Store in memO
            result = await self.memo_client.store_conversation(
                conversation_id=self.current_session_id,
                user_message=user_input,
                agent_response=agent_response,
                metadata=interaction_metadata
            )
            
            if result["success"]:
                logger.info(f"Recorded interaction in session {self.current_session_id}")
            else:
                logger.warning(f"Failed to record interaction in memO: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error recording interaction: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": self.current_session_id
            }
    
    async def get_conversation_history(
        self,
        session_id: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get conversation history for a session
        
        Args:
            session_id: Session ID (uses current session if not provided)
            limit: Maximum number of interactions to retrieve
            
        Returns:
            Dictionary containing conversation history
        """
        try:
            target_session = session_id or self.current_session_id
            
            if not target_session:
                return {
                    "success": False,
                    "error": "No session ID provided and no current session",
                    "history": []
                }
            
            result = await self.memo_client.retrieve_conversation_history(
                conversation_id=target_session,
                limit=limit
            )
            
            if result["success"]:
                logger.info(f"Retrieved {len(result.get('conversations', []))} interactions for session {target_session}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {e}")
            return {
                "success": False,
                "error": str(e),
                "history": []
            }
    
    async def search_past_interactions(
        self,
        query: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search past interactions across all sessions
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            Dictionary containing search results
        """
        try:
            result = await self.memo_client.search_conversations(
                query=query,
                limit=limit
            )
            
            if result["success"]:
                logger.info(f"Found {len(result.get('results', []))} results for query: {query}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error searching interactions: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": []
            }
    
    async def end_session(self, session_summary: Optional[str] = None) -> Dict[str, Any]:
        """
        End the current session
        
        Args:
            session_summary: Optional summary of the session
            
        Returns:
            Dictionary containing session end result
        """
        try:
            if not self.current_session_id:
                return {
                    "success": False,
                    "error": "No active session to end"
                }
            
            # Record session end
            end_metadata = {
                "session_end": datetime.now().isoformat(),
                "session_summary": session_summary,
                "session_duration": "calculated_duration"
            }
            
            # Store session end record
            result = await self.memo_client.store_conversation(
                conversation_id=self.current_session_id,
                user_message="[SESSION_END]",
                agent_response=f"Session ended. Summary: {session_summary or 'No summary provided'}",
                metadata=end_metadata
            )
            
            session_id = self.current_session_id
            
            # Clear current session
            self.current_session_id = None
            self.session_metadata = {}
            
            logger.info(f"Ended session: {session_id}")
            
            return {
                "success": True,
                "session_id": session_id,
                "message": "Session ended successfully"
            }
            
        except Exception as e:
            logger.error(f"Error ending session: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def record_interaction_sync(
        self,
        user_input: str,
        agent_response: str,
        interaction_type: str = "general",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Synchronous version of record_interaction for non-async contexts
        """
        try:
            # Use current session or create a simple one
            if not self.current_session_id:
                self.current_session_id = f"sync_session_{int(datetime.now().timestamp())}"
            
            # Prepare interaction metadata
            interaction_metadata = {
                "interaction_type": interaction_type,
                "timestamp": datetime.now().isoformat(),
                "sync_mode": True,
                **(metadata or {})
            }
            
            # Store in memO synchronously
            result = self.memo_client.store_conversation_sync(
                conversation_id=self.current_session_id,
                user_message=user_input,
                agent_response=agent_response,
                metadata=interaction_metadata
            )
            
            if result["success"]:
                logger.info(f"Recorded interaction in session {self.current_session_id} (sync)")
            else:
                logger.warning(f"Failed to record interaction in memO (sync): {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error recording interaction (sync): {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": self.current_session_id
            }
    
    def get_current_session_id(self) -> Optional[str]:
        """Get the current session ID"""
        return self.current_session_id
    
    def get_session_metadata(self) -> Dict[str, Any]:
        """Get metadata for the current session"""
        return self.session_metadata.copy()