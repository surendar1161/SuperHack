"""
MetadataSyncAgent - Responsible for syncing metadata from SuperOps
Handles users, SLAs, tasks, and ticket information synchronization
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import sqlite3
from .base_subagent import BaseSubagent, AgentMessage
from ..config import AgentConfig
from ...clients.superops_client import SuperOpsClient

@dataclass
class SyncResult:
    """Result of a sync operation"""
    endpoint: str
    records_synced: int
    last_sync_timestamp: datetime
    success: bool
    error_message: Optional[str] = None

class MetadataSyncAgent(BaseSubagent):
    """
    Agent responsible for syncing metadata from SuperOps endpoints
    
    Responsibilities:
    - Sync user data from SuperOps /users endpoint
    - Sync SLA configurations from /slas endpoint  
    - Sync task metadata from /tasks endpoint
    - Sync ticket information from /tickets endpoint
    
    Scalability Features:
    - Parallel processing with worker pools
    - Incremental sync using timestamps
    - Rate limiting to prevent API throttling
    - Circuit breaker pattern for fault tolerance
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config, "MetadataSyncAgent")
        
        # Configuration
        self.sync_interval = getattr(config, 'metadata_sync_interval', 300)  # 5 minutes
        self.batch_size = getattr(config, 'metadata_batch_size', 1000)
        self.max_workers = getattr(config, 'metadata_max_workers', 4)
        
        # SuperOps client
        self.superops_client = SuperOpsClient(config)
        
        # Local storage
        self.db_path = "metadata_sync.db"
        self.last_sync_times = {}
        
        # Sync endpoints configuration
        self.sync_endpoints = {
            'users': {
                'query': 'query { users { id name email role department isActive } }',
                'table': 'users',
                'key_field': 'id'
            },
            'slas': {
                'query': 'query { slas { id name priority responseTime resolutionTime } }',
                'table': 'slas', 
                'key_field': 'id'
            },
            'tasks': {
                'query': 'query { tasks { id title status priority assignee createdAt } }',
                'table': 'tasks',
                'key_field': 'id'
            },
            'tickets': {
                'query': 'query { tickets { id subject status priority assignee createdAt updatedAt } }',
                'table': 'tickets',
                'key_field': 'id'
            }
        }
    
    def _get_worker_count(self) -> int:
        """Get optimal worker count based on configuration"""
        return self.max_workers
    
    async def _initialize_agent(self):
        """Initialize metadata sync agent"""
        # Initialize local database
        self._init_local_database()
        
        # Connect to SuperOps
        await self.superops_client.connect()
        
        # Subscribe to sync requests
        await self.subscribe_to_topic("sync-requests", self._handle_sync_request)
        
        # Register as publisher
        await self.publish_to_topic("metadata-updates")
        
        # Start periodic sync task
        asyncio.create_task(self._periodic_sync_loop())
        
        self.logger.info("MetadataSyncAgent initialized successfully")
    
    async def _cleanup_agent(self):
        """Cleanup metadata sync agent"""
        if self.superops_client:
            await self.superops_client.disconnect()
    
    def _init_local_database(self):
        """Initialize local SQLite database for metadata storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT,
                email TEXT,
                role TEXT,
                department TEXT,
                is_active BOOLEAN,
                synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # SLAs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS slas (
                id TEXT PRIMARY KEY,
                name TEXT,
                priority TEXT,
                response_time INTEGER,
                resolution_time INTEGER,
                synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT,
                status TEXT,
                priority TEXT,
                assignee TEXT,
                created_at TIMESTAMP,
                synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tickets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id TEXT PRIMARY KEY,
                subject TEXT,
                status TEXT,
                priority TEXT,
                assignee TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Sync tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_tracking (
                endpoint TEXT PRIMARY KEY,
                last_sync TIMESTAMP,
                records_count INTEGER DEFAULT 0,
                last_error TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        
        self.logger.info("Local metadata database initialized")
    
    async def _process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process incoming sync messages"""
        if message.message_type == "sync_request":
            return await self._handle_sync_request(message)
        elif message.message_type == "incremental_sync":
            return await self._handle_incremental_sync(message)
        else:
            self.logger.warning(f"Unknown message type: {message.message_type}")
            return None
    
    async def _handle_sync_request(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle sync request message"""
        endpoint = message.payload.get("endpoint", "all")
        force_full_sync = message.payload.get("force_full_sync", False)
        
        if endpoint == "all":
            results = await self._sync_all_endpoints(force_full_sync)
        else:
            results = [await self._sync_endpoint(endpoint, force_full_sync)]
        
        # Publish sync results
        response = AgentMessage(
            id=f"sync_result_{datetime.now().isoformat()}",
            timestamp=datetime.now(),
            source_agent=self.agent_name,
            target_topic="metadata-updates",
            message_type="sync_completed",
            payload={
                "results": [result.__dict__ for result in results],
                "total_records": sum(r.records_synced for r in results if r.success)
            }
        )
        
        return response
    
    async def _handle_incremental_sync(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle incremental sync request"""
        endpoint = message.payload.get("endpoint")
        since_timestamp = message.payload.get("since_timestamp")
        
        if not endpoint or not since_timestamp:
            self.logger.error("Incremental sync requires endpoint and since_timestamp")
            return None
        
        result = await self._sync_endpoint(endpoint, force_full_sync=False, since=since_timestamp)
        
        response = AgentMessage(
            id=f"incremental_sync_result_{datetime.now().isoformat()}",
            timestamp=datetime.now(),
            source_agent=self.agent_name,
            target_topic="metadata-updates",
            message_type="incremental_sync_completed",
            payload={"result": result.__dict__}
        )
        
        return response
    
    async def _periodic_sync_loop(self):
        """Periodic sync loop"""
        while self.is_running:
            try:
                self.logger.info("Starting periodic metadata sync")
                
                # Perform incremental sync for all endpoints
                results = await self._sync_all_endpoints(force_full_sync=False)
                
                # Log results
                total_synced = sum(r.records_synced for r in results if r.success)
                failed_endpoints = [r.endpoint for r in results if not r.success]
                
                self.logger.info(f"Periodic sync completed: {total_synced} records synced")
                if failed_endpoints:
                    self.logger.warning(f"Failed endpoints: {failed_endpoints}")
                
                # Publish sync completion
                await self._publish_message(AgentMessage(
                    id=f"periodic_sync_{datetime.now().isoformat()}",
                    timestamp=datetime.now(),
                    source_agent=self.agent_name,
                    target_topic="metadata-updates",
                    message_type="periodic_sync_completed",
                    payload={
                        "total_records": total_synced,
                        "failed_endpoints": failed_endpoints
                    }
                ))
                
            except Exception as e:
                self.logger.error(f"Error in periodic sync: {e}")
            
            # Wait for next sync interval
            await asyncio.sleep(self.sync_interval)
    
    async def _sync_all_endpoints(self, force_full_sync: bool = False) -> List[SyncResult]:
        """Sync all configured endpoints"""
        tasks = []
        
        for endpoint_name in self.sync_endpoints.keys():
            task = asyncio.create_task(
                self._sync_endpoint(endpoint_name, force_full_sync)
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        sync_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                endpoint_name = list(self.sync_endpoints.keys())[i]
                sync_results.append(SyncResult(
                    endpoint=endpoint_name,
                    records_synced=0,
                    last_sync_timestamp=datetime.now(),
                    success=False,
                    error_message=str(result)
                ))
            else:
                sync_results.append(result)
        
        return sync_results
    
    async def _sync_endpoint(self, endpoint_name: str, force_full_sync: bool = False, 
                           since: Optional[str] = None) -> SyncResult:
        """Sync a specific endpoint"""
        if endpoint_name not in self.sync_endpoints:
            return SyncResult(
                endpoint=endpoint_name,
                records_synced=0,
                last_sync_timestamp=datetime.now(),
                success=False,
                error_message=f"Unknown endpoint: {endpoint_name}"
            )
        
        endpoint_config = self.sync_endpoints[endpoint_name]
        
        try:
            # Get last sync time if not force full sync
            last_sync = None
            if not force_full_sync and not since:
                last_sync = self._get_last_sync_time(endpoint_name)
            elif since:
                last_sync = datetime.fromisoformat(since)
            
            # Build query with timestamp filter if incremental
            query = endpoint_config['query']
            if last_sync and not force_full_sync:
                # Modify query to include timestamp filter
                # This is a simplified approach - in reality, you'd need proper GraphQL query building
                query = query.replace('{ ', f'{{ (updatedAt: {{gt: "{last_sync.isoformat()}"}}) ')
            
            # Execute query with rate limiting and circuit breaker
            data = await self.execute_with_rate_limit(
                self._execute_superops_query, query
            )
            
            if not data:
                return SyncResult(
                    endpoint=endpoint_name,
                    records_synced=0,
                    last_sync_timestamp=datetime.now(),
                    success=False,
                    error_message="No data returned from SuperOps"
                )
            
            # Process data in batches
            records = data.get(endpoint_name, [])
            records_synced = await self._process_records_in_batches(
                endpoint_name, records, endpoint_config
            )
            
            # Update sync tracking
            self._update_sync_tracking(endpoint_name, len(records))
            
            return SyncResult(
                endpoint=endpoint_name,
                records_synced=records_synced,
                last_sync_timestamp=datetime.now(),
                success=True
            )
            
        except Exception as e:
            self.logger.error(f"Error syncing {endpoint_name}: {e}")
            return SyncResult(
                endpoint=endpoint_name,
                records_synced=0,
                last_sync_timestamp=datetime.now(),
                success=False,
                error_message=str(e)
            )
    
    async def _execute_superops_query(self, query: str) -> Optional[Dict]:
        """Execute GraphQL query against SuperOps"""
        try:
            # This is a mock implementation - replace with actual SuperOps GraphQL call
            # For now, return mock data
            return await self._get_mock_data(query)
            
        except Exception as e:
            self.logger.error(f"SuperOps query failed: {e}")
            return None
    
    async def _get_mock_data(self, query: str) -> Dict:
        """Generate mock data for testing"""
        if "users" in query:
            return {
                "users": [
                    {"id": "1", "name": "John Doe", "email": "john@example.com", "role": "technician", "department": "IT", "isActive": True},
                    {"id": "2", "name": "Jane Smith", "email": "jane@example.com", "role": "manager", "department": "IT", "isActive": True}
                ]
            }
        elif "slas" in query:
            return {
                "slas": [
                    {"id": "1", "name": "Critical SLA", "priority": "critical", "responseTime": 1, "resolutionTime": 4},
                    {"id": "2", "name": "High SLA", "priority": "high", "responseTime": 4, "resolutionTime": 24}
                ]
            }
        elif "tasks" in query:
            return {
                "tasks": [
                    {"id": "1", "title": "Server maintenance", "status": "in_progress", "priority": "high", "assignee": "1", "createdAt": datetime.now().isoformat()},
                    {"id": "2", "title": "Network check", "status": "pending", "priority": "medium", "assignee": "2", "createdAt": datetime.now().isoformat()}
                ]
            }
        elif "tickets" in query:
            return {
                "tickets": [
                    {"id": "1", "subject": "Email not working", "status": "open", "priority": "high", "assignee": "1", "createdAt": datetime.now().isoformat(), "updatedAt": datetime.now().isoformat()},
                    {"id": "2", "subject": "Printer issue", "status": "in_progress", "priority": "medium", "assignee": "2", "createdAt": datetime.now().isoformat(), "updatedAt": datetime.now().isoformat()}
                ]
            }
        
        return {}
    
    async def _process_records_in_batches(self, endpoint_name: str, records: List[Dict], 
                                        endpoint_config: Dict) -> int:
        """Process records in batches for better performance"""
        total_processed = 0
        
        for i in range(0, len(records), self.batch_size):
            batch = records[i:i + self.batch_size]
            
            # Process batch
            processed = await self._process_batch(endpoint_name, batch, endpoint_config)
            total_processed += processed
            
            # Small delay between batches to prevent overwhelming the system
            if i + self.batch_size < len(records):
                await asyncio.sleep(0.1)
        
        return total_processed
    
    async def _process_batch(self, endpoint_name: str, batch: List[Dict], 
                           endpoint_config: Dict) -> int:
        """Process a batch of records"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        table_name = endpoint_config['table']
        key_field = endpoint_config['key_field']
        
        processed = 0
        
        for record in batch:
            try:
                # Convert record to database format
                db_record = self._convert_record_for_db(endpoint_name, record)
                
                # Upsert record
                placeholders = ', '.join(['?' for _ in db_record.keys()])
                columns = ', '.join(db_record.keys())
                values = list(db_record.values())
                
                cursor.execute(f"""
                    INSERT OR REPLACE INTO {table_name} ({columns})
                    VALUES ({placeholders})
                """, values)
                
                processed += 1
                
            except Exception as e:
                self.logger.error(f"Error processing record {record.get(key_field)}: {e}")
        
        conn.commit()
        conn.close()
        
        return processed
    
    def _convert_record_for_db(self, endpoint_name: str, record: Dict) -> Dict:
        """Convert API record to database format"""
        db_record = record.copy()
        db_record['synced_at'] = datetime.now().isoformat()
        
        # Handle specific field conversions
        if endpoint_name == "users":
            db_record['is_active'] = record.get('isActive', True)
            if 'isActive' in db_record:
                del db_record['isActive']
        
        return db_record
    
    def _get_last_sync_time(self, endpoint: str) -> Optional[datetime]:
        """Get last sync time for endpoint"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT last_sync FROM sync_tracking WHERE endpoint = ?",
            (endpoint,)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            return datetime.fromisoformat(result[0])
        
        return None
    
    def _update_sync_tracking(self, endpoint: str, record_count: int):
        """Update sync tracking information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO sync_tracking (endpoint, last_sync, records_count)
            VALUES (?, ?, ?)
        """, (endpoint, datetime.now().isoformat(), record_count))
        
        conn.commit()
        conn.close()
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status for all endpoints"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM sync_tracking")
        results = cursor.fetchall()
        conn.close()
        
        status = {}
        for row in results:
            status[row[0]] = {
                "last_sync": row[1],
                "records_count": row[2],
                "last_error": row[3] if len(row) > 3 else None
            }
        
        return status