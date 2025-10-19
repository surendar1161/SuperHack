"""
Local Memory Manager using SQLite as fallback for memO
"""

import asyncio
import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from ..utils.logger import get_logger

logger = get_logger("local_memory_manager")


class LocalMemoryManager:
    """Local memory manager using SQLite as fallback for memO"""
    
    def __init__(self, db_path: str = "conversations.db"):
        self.db_path = db_path
        self.current_session_id = None
        self.session_metadata = {}
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database for conversation storage"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    agent_response TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    session_type TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    user_info TEXT,
                    session_summary TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversation_id 
                ON conversations(conversation_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON conversations(timestamp)
            """)
            
            conn.commit()
            conn.close()
            
            logger.info(f"Local memory database initialized: {self.db_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize local memory database: {e}")
            raise
    
    async def start_session(
        self,
        session_type: str = "support_session",
        user_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """Start a new conversation session"""
        try:
            # Generate unique session ID
            session_id = f"local_session_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"
            
            # Store session metadata
            self.current_session_id = session_id
            self.session_metadata = {
                "session_id": session_id,
                "session_type": session_type,
                "start_time": datetime.now().isoformat(),
                "user_info": user_info or {},
                "agent_type": "SuperOps IT Technician Agent (Local Memory)"
            }
            
            # Store session in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO sessions (session_id, session_type, start_time, user_info)
                VALUES (?, ?, ?, ?)
            """, (
                session_id,
                session_type,
                datetime.now().isoformat(),
                json.dumps(user_info or {})
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Started local session: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error starting local session: {e}")
            # Still return a session ID even if database fails
            session_id = f"fallback_session_{int(datetime.now().timestamp())}"
            self.current_session_id = session_id
            return session_id
    
    async def record_interaction(
        self,
        user_input: str,
        agent_response: str,
        interaction_type: str = "general",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Record a user-agent interaction"""
        try:
            # Use current session or create a new one
            if not self.current_session_id:
                await self.start_session()
            
            # Generate unique interaction ID
            interaction_id = f"interaction_{uuid.uuid4().hex}"
            timestamp = datetime.now().isoformat()
            
            # Prepare interaction metadata
            interaction_metadata = {
                "interaction_type": interaction_type,
                "timestamp": timestamp,
                "session_metadata": self.session_metadata,
                **(metadata or {})
            }
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO conversations (id, conversation_id, timestamp, user_message, agent_response, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                interaction_id,
                self.current_session_id,
                timestamp,
                user_input,
                agent_response,
                json.dumps(interaction_metadata)
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Recorded interaction in local session {self.current_session_id}")
            
            return {
                "success": True,
                "interaction_id": interaction_id,
                "conversation_id": self.current_session_id,
                "timestamp": timestamp
            }
            
        except Exception as e:
            logger.error(f"Error recording local interaction: {e}")
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
        """Get conversation history for a session"""
        try:
            target_session = session_id or self.current_session_id
            
            if not target_session:
                return {
                    "success": False,
                    "error": "No session ID provided and no current session",
                    "conversations": []
                }
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, timestamp, user_message, agent_response, metadata
                FROM conversations
                WHERE conversation_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (target_session, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            conversations = []
            for row in rows:
                conversations.append({
                    "id": row[0],
                    "timestamp": row[1],
                    "user_message": row[2],
                    "agent_response": row[3],
                    "metadata": json.loads(row[4]) if row[4] else {}
                })
            
            logger.info(f"Retrieved {len(conversations)} interactions for local session {target_session}")
            
            return {
                "success": True,
                "conversation_id": target_session,
                "conversations": conversations,
                "total_count": len(conversations)
            }
            
        except Exception as e:
            logger.error(f"Error retrieving local conversation history: {e}")
            return {
                "success": False,
                "error": str(e),
                "conversations": []
            }
    
    async def search_past_interactions(
        self,
        query: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Search past interactions across all sessions"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Simple text search in user messages and agent responses
            search_query = f"%{query}%"
            
            cursor.execute("""
                SELECT id, conversation_id, timestamp, user_message, agent_response, metadata
                FROM conversations
                WHERE user_message LIKE ? OR agent_response LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (search_query, search_query, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            results = []
            for row in rows:
                results.append({
                    "id": row[0],
                    "conversation_id": row[1],
                    "timestamp": row[2],
                    "user_message": row[3],
                    "agent_response": row[4],
                    "metadata": json.loads(row[5]) if row[5] else {}
                })
            
            logger.info(f"Found {len(results)} local results for query: {query}")
            
            return {
                "success": True,
                "query": query,
                "results": results,
                "total_count": len(results)
            }
            
        except Exception as e:
            logger.error(f"Error searching local interactions: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": []
            }
    
    async def end_session(self, session_summary: Optional[str] = None) -> Dict[str, Any]:
        """End the current session"""
        try:
            if not self.current_session_id:
                return {
                    "success": False,
                    "error": "No active session to end"
                }
            
            # Update session in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE sessions
                SET end_time = ?, session_summary = ?
                WHERE session_id = ?
            """, (
                datetime.now().isoformat(),
                session_summary,
                self.current_session_id
            ))
            
            conn.commit()
            conn.close()
            
            # Record session end
            await self.record_interaction(
                user_input="[SESSION_END]",
                agent_response=f"Session ended. Summary: {session_summary or 'No summary provided'}",
                interaction_type="session_end",
                metadata={
                    "session_end": datetime.now().isoformat(),
                    "session_summary": session_summary
                }
            )
            
            session_id = self.current_session_id
            
            # Clear current session
            self.current_session_id = None
            self.session_metadata = {}
            
            logger.info(f"Ended local session: {session_id}")
            
            return {
                "success": True,
                "session_id": session_id,
                "message": "Local session ended successfully"
            }
            
        except Exception as e:
            logger.error(f"Error ending local session: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_current_session_id(self) -> Optional[str]:
        """Get the current session ID"""
        return self.current_session_id
    
    def get_session_metadata(self) -> Dict[str, Any]:
        """Get metadata for the current session"""
        return self.session_metadata.copy()
    
    async def get_session_statistics(self) -> Dict[str, Any]:
        """Get statistics about all sessions"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get session count
            cursor.execute("SELECT COUNT(*) FROM sessions")
            total_sessions = cursor.fetchone()[0]
            
            # Get conversation count
            cursor.execute("SELECT COUNT(*) FROM conversations")
            total_conversations = cursor.fetchone()[0]
            
            # Get recent activity
            cursor.execute("""
                SELECT COUNT(*) FROM conversations
                WHERE datetime(timestamp) > datetime('now', '-24 hours')
            """)
            recent_conversations = cursor.fetchone()[0]
            
            # Get interaction types
            cursor.execute("""
                SELECT json_extract(metadata, '$.interaction_type') as interaction_type, COUNT(*)
                FROM conversations
                WHERE json_extract(metadata, '$.interaction_type') IS NOT NULL
                GROUP BY interaction_type
            """)
            
            interaction_types = {}
            for row in cursor.fetchall():
                interaction_types[row[0]] = row[1]
            
            conn.close()
            
            return {
                "success": True,
                "statistics": {
                    "total_sessions": total_sessions,
                    "total_conversations": total_conversations,
                    "recent_conversations_24h": recent_conversations,
                    "interaction_types": interaction_types,
                    "database_path": self.db_path
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting local session statistics: {e}")
            return {
                "success": False,
                "error": str(e),
                "statistics": {}
            }
    
    def record_interaction_sync(
        self,
        user_input: str,
        agent_response: str,
        interaction_type: str = "general",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Synchronous version of record_interaction"""
        try:
            # Use current session or create a simple one
            if not self.current_session_id:
                self.current_session_id = f"sync_session_{int(datetime.now().timestamp())}"
            
            # Generate unique interaction ID
            interaction_id = f"sync_interaction_{uuid.uuid4().hex}"
            timestamp = datetime.now().isoformat()
            
            # Prepare interaction metadata
            interaction_metadata = {
                "interaction_type": interaction_type,
                "timestamp": timestamp,
                "sync_mode": True,
                **(metadata or {})
            }
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO conversations (id, conversation_id, timestamp, user_message, agent_response, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                interaction_id,
                self.current_session_id,
                timestamp,
                user_input,
                agent_response,
                json.dumps(interaction_metadata)
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Recorded sync interaction in local session {self.current_session_id}")
            
            return {
                "success": True,
                "interaction_id": interaction_id,
                "conversation_id": self.current_session_id,
                "timestamp": timestamp
            }
            
        except Exception as e:
            logger.error(f"Error recording sync local interaction: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": self.current_session_id
            }