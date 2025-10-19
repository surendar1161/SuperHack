"""
Memory-enhanced agent that integrates memO for conversation tracking
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from .config import AgentConfig
from ..memory.memo_memory_manager import MemoMemoryManager
from ..utils.logger import get_logger

logger = get_logger("memory_enhanced_agent")


class MemoryEnhancedAgent:
    """
    Agent wrapper that adds memO memory capabilities to any agent
    """
    
    def __init__(self, config: AgentConfig, agent_name: str = "SuperOps IT Technician"):
        self.config = config
        self.agent_name = agent_name
        
        # Initialize memory manager if memO is enabled
        self.memory_manager = None
        if config.memo_enabled and config.memo_api_key:
            try:
                self.memory_manager = MemoMemoryManager(
                    memo_api_key=config.memo_api_key,
                    memo_base_url=config.memo_base_url
                )
                logger.info("memO memory manager initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize memO memory manager: {e}")
                self.memory_manager = None
        else:
            logger.info("memO memory manager disabled or not configured")
    
    async def start_conversation_session(
        self,
        session_type: str = "support_session",
        user_info: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Start a new conversation session with memory tracking
        
        Args:
            session_type: Type of session (support_session, onboarding, etc.)
            user_info: Information about the user
            
        Returns:
            Session ID if memory is enabled, None otherwise
        """
        if not self.memory_manager:
            return None
        
        try:
            session_id = await self.memory_manager.start_session(
                session_type=session_type,
                user_info=user_info
            )
            
            logger.info(f"Started conversation session: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error starting conversation session: {e}")
            return None
    
    async def process_user_request(
        self,
        user_input: str,
        request_type: str = "general",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a user request and record the interaction in memory
        
        Args:
            user_input: The user's input/request
            request_type: Type of request (ticket_creation, user_query, etc.)
            context: Additional context about the request
            
        Returns:
            Dictionary containing the agent's response and metadata
        """
        try:
            # Get conversation history for context (if memory is enabled)
            conversation_context = []
            if self.memory_manager:
                history_result = await self.memory_manager.get_conversation_history(limit=5)
                if history_result["success"]:
                    conversation_context = history_result.get("conversations", [])
            
            # Process the request (this would integrate with your actual agent logic)
            agent_response = await self._generate_agent_response(
                user_input=user_input,
                request_type=request_type,
                context=context,
                conversation_history=conversation_context
            )
            
            # Record the interaction in memory
            if self.memory_manager:
                memory_metadata = {
                    "request_type": request_type,
                    "context": context or {},
                    "agent_name": self.agent_name,
                    "processing_time": "calculated_time"
                }
                
                await self.memory_manager.record_interaction(
                    user_input=user_input,
                    agent_response=agent_response["response"],
                    interaction_type=request_type,
                    metadata=memory_metadata
                )
            
            return {
                "success": True,
                "response": agent_response["response"],
                "metadata": agent_response.get("metadata", {}),
                "session_id": self.memory_manager.get_current_session_id() if self.memory_manager else None
            }
            
        except Exception as e:
            logger.error(f"Error processing user request: {e}")
            
            error_response = f"I apologize, but I encountered an error while processing your request: {str(e)}"
            
            # Still try to record the error interaction
            if self.memory_manager:
                try:
                    await self.memory_manager.record_interaction(
                        user_input=user_input,
                        agent_response=error_response,
                        interaction_type="error",
                        metadata={"error": str(e), "request_type": request_type}
                    )
                except:
                    pass  # Don't let memory errors compound the original error
            
            return {
                "success": False,
                "response": error_response,
                "error": str(e),
                "session_id": self.memory_manager.get_current_session_id() if self.memory_manager else None
            }
    
    async def _generate_agent_response(
        self,
        user_input: str,
        request_type: str,
        context: Optional[Dict[str, Any]],
        conversation_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate agent response (this would integrate with your actual agent logic)
        
        This is a placeholder that demonstrates how to integrate with existing agent systems
        """
        
        # Example response generation based on request type
        if request_type == "ticket_creation":
            response = await self._handle_ticket_creation(user_input, context, conversation_history)
        elif request_type == "user_query":
            response = await self._handle_user_query(user_input, context, conversation_history)
        elif request_type == "contract_management":
            response = await self._handle_contract_management(user_input, context, conversation_history)
        else:
            response = await self._handle_general_request(user_input, context, conversation_history)
        
        return response
    
    async def _handle_ticket_creation(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]],
        conversation_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle ticket creation requests"""
        
        # This would integrate with your existing ticket creation tools
        response = f"I'll help you create a ticket for: {user_input}\n\n"
        
        # Add context from conversation history
        if conversation_history:
            response += "Based on our previous conversation, I have the following context:\n"
            for msg in conversation_history[-2:]:  # Last 2 interactions
                if msg.get("metadata", {}).get("interaction_type") == "ticket_creation":
                    response += f"- Previous ticket discussion: {msg.get('user_message', '')[:100]}...\n"
        
        response += "\nPlease provide more details about the issue you're experiencing."
        
        return {
            "response": response,
            "metadata": {
                "action": "ticket_creation_initiated",
                "requires_followup": True
            }
        }
    
    async def _handle_user_query(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]],
        conversation_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle general user queries"""
        
        response = f"I understand you're asking about: {user_input}\n\n"
        
        # Check if we've discussed similar topics before
        if conversation_history:
            similar_topics = []
            for msg in conversation_history:
                if any(word in msg.get("user_message", "").lower() for word in user_input.lower().split()):
                    similar_topics.append(msg)
            
            if similar_topics:
                response += "I notice we've discussed similar topics before. "
        
        response += "Let me help you with that. Could you provide more specific details about what you need?"
        
        return {
            "response": response,
            "metadata": {
                "action": "information_request",
                "similar_topics_found": len(similar_topics) if 'similar_topics' in locals() else 0
            }
        }
    
    async def _handle_contract_management(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]],
        conversation_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle contract management requests"""
        
        response = f"I'll assist you with contract management: {user_input}\n\n"
        response += "I can help you with:\n"
        response += "- Creating new client contracts\n"
        response += "- Viewing existing contracts\n"
        response += "- Managing contract details\n\n"
        response += "What specific contract operation would you like to perform?"
        
        return {
            "response": response,
            "metadata": {
                "action": "contract_management",
                "available_operations": ["create", "view", "manage"]
            }
        }
    
    async def _handle_general_request(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]],
        conversation_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle general requests"""
        
        response = f"Thank you for your message: {user_input}\n\n"
        response += "As your SuperOps IT Technician Agent, I can help you with:\n"
        response += "- Creating and managing support tickets\n"
        response += "- User and technician management\n"
        response += "- Contract management\n"
        response += "- System alerts and monitoring\n"
        response += "- Knowledge base articles\n\n"
        response += "How can I assist you today?"
        
        return {
            "response": response,
            "metadata": {
                "action": "general_assistance",
                "capabilities_shown": True
            }
        }
    
    async def search_conversation_history(
        self,
        query: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search conversation history using memO
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            Dictionary containing search results
        """
        if not self.memory_manager:
            return {
                "success": False,
                "error": "Memory manager not available",
                "results": []
            }
        
        try:
            result = await self.memory_manager.search_past_interactions(
                query=query,
                limit=limit
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error searching conversation history: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": []
            }
    
    async def get_session_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current session
        
        Returns:
            Dictionary containing session summary
        """
        if not self.memory_manager:
            return {
                "success": False,
                "error": "Memory manager not available"
            }
        
        try:
            session_id = self.memory_manager.get_current_session_id()
            if not session_id:
                return {
                    "success": False,
                    "error": "No active session"
                }
            
            history_result = await self.memory_manager.get_conversation_history(limit=50)
            
            if history_result["success"]:
                conversations = history_result.get("conversations", [])
                
                summary = {
                    "session_id": session_id,
                    "total_interactions": len(conversations),
                    "session_metadata": self.memory_manager.get_session_metadata(),
                    "interaction_types": {},
                    "recent_topics": []
                }
                
                # Analyze interactions
                for conv in conversations:
                    interaction_type = conv.get("metadata", {}).get("interaction_type", "general")
                    summary["interaction_types"][interaction_type] = summary["interaction_types"].get(interaction_type, 0) + 1
                    
                    # Extract recent topics (simplified)
                    user_msg = conv.get("user_message", "")
                    if user_msg and len(user_msg) > 10:
                        summary["recent_topics"].append(user_msg[:100])
                
                return {
                    "success": True,
                    "summary": summary
                }
            else:
                return history_result
                
        except Exception as e:
            logger.error(f"Error getting session summary: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def end_conversation_session(self, session_summary: Optional[str] = None) -> Dict[str, Any]:
        """
        End the current conversation session
        
        Args:
            session_summary: Optional summary of the session
            
        Returns:
            Dictionary containing session end result
        """
        if not self.memory_manager:
            return {
                "success": False,
                "error": "Memory manager not available"
            }
        
        try:
            result = await self.memory_manager.end_session(session_summary)
            
            if result["success"]:
                logger.info(f"Ended conversation session: {result.get('session_id')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error ending conversation session: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def is_memory_enabled(self) -> bool:
        """Check if memory management is enabled and available"""
        return self.memory_manager is not None