"""
Robust SuperOps API Client
Handles all SuperOps API communication with fallback to mock data
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from enum import Enum

from ..agents.config import AgentConfig
from ..utils.logger import get_logger
from .exceptions import SuperOpsAPIError, AuthenticationError, RateLimitError

class APIMode(Enum):
    """API operation modes"""
    REAL = "real"
    MOCK = "mock"
    HYBRID = "hybrid"  # Try real, fallback to mock

class RobustSuperOpsClient:
    """
    Robust SuperOps API client with intelligent fallback
    Automatically handles API failures and provides consistent interface
    """

    def __init__(self, config: AgentConfig, mode: APIMode = APIMode.HYBRID):
        self.config = config
        self.mode = mode
        self.logger = get_logger(self.__class__.__name__)
        self.session = None
        self.connected = False
        
        # Mock data storage
        self.mock_tickets = {}
        self.mock_tasks = {}
        self.mock_work_logs = {}
        self.mock_time_entries = {}
        self.mock_users = {}
        
        # API configuration
        self.api_url = self._determine_api_url()
        self.headers = self._build_headers()
        
        # Track API health
        self.api_healthy = None
        self.last_health_check = None

    def _determine_api_url(self) -> str:
        """Determine the correct API URL (WORKING FORMAT)"""
        # Use the working IT endpoint from successful curl command
        return "https://api.superops.ai/it"

    def _build_headers(self) -> Dict[str, str]:
        """Build request headers (WORKING FORMAT)"""
        headers = {
            "Authorization": f"Bearer {self.config.superops_api_key}",
            "Content-Type": "application/json",
            "CustomerSubDomain": "hackathon",  # Required for working API
            "Cookie": "JSESSIONID=4F5551506BB79B608294EB25E62B5C52; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
        }
        
        return headers

    async def connect(self):
        """Initialize connection and determine API health"""
        self.logger.info("Initializing SuperOps API connection...")
        
        # Initialize HTTP session
        self.session = aiohttp.ClientSession(headers=self.headers)
        
        # Check API health
        if self.mode in [APIMode.REAL, APIMode.HYBRID]:
            await self._check_api_health()
        
        self.connected = True
        
        if self.api_healthy:
            self.logger.info("Connected to SuperOps API successfully")
        elif self.mode == APIMode.HYBRID:
            self.logger.warning("SuperOps API unavailable, using mock mode")
        else:
            self.logger.info("Using mock SuperOps client")

    async def _check_api_health(self) -> bool:
        """Check if the SuperOps API is accessible and healthy"""
        try:
            # Try a simple health check
            health_endpoints = [
                f"{self.api_url.replace('/it', '/health')}",
                f"{self.api_url.replace('/it', '')}/health",
                "https://api.superops.ai/health",
                "https://euapi.superops.ai/health"
            ]
            
            for endpoint in health_endpoints:
                try:
                    async with self.session.get(endpoint, timeout=5) as response:
                        if response.status == 200:
                            self.api_healthy = True
                            self.last_health_check = datetime.now()
                            self.logger.info(f"API health check passed: {endpoint}")
                            return True
                except:
                    continue
            
            # Try a simple GraphQL query
            test_query = {
                "query": "query { __typename }",
                "variables": {}
            }
            
            async with self.session.post(self.api_url, json=test_query, timeout=5) as response:
                if response.status in [200, 400]:  # 400 might be schema issue, but API is responding
                    self.api_healthy = True
                    self.last_health_check = datetime.now()
                    self.logger.info("API responding to GraphQL queries")
                    return True
                    
        except Exception as e:
            self.logger.warning(f"API health check failed: {e}")
        
        self.api_healthy = False
        self.last_health_check = datetime.now()
        return False

    async def _execute_real_api_call(self, operation: str, payload: Dict) -> Optional[Dict]:
        """Execute real API call with error handling"""
        try:
            self.logger.debug(f"Executing real API call: {operation}")
            
            async with self.session.post(self.api_url, json=payload, timeout=30) as response:
                if response.status == 200:
                    result = await response.json()
                    self.logger.debug(f"Real API call successful: {operation}")
                    return result
                else:
                    error_text = await response.text()
                    self.logger.warning(f"Real API call failed ({response.status}): {error_text[:200]}")
                    return None
                    
        except Exception as e:
            self.logger.warning(f"Real API call exception: {e}")
            return None

    def _generate_mock_id(self, prefix: str = "MOCK") -> str:
        """Generate mock ID"""
        return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"

    def _generate_mock_number(self, prefix: str = "TKT") -> str:
        """Generate mock ticket number"""
        return f"{prefix}-{len(self.mock_tickets) + 1:06d}"

    async def create_ticket(self, ticket_data: Dict) -> Dict:
        """Create a new ticket with intelligent fallback"""
        self.logger.info("Creating ticket...")
        
        # Try real API first if in real or hybrid mode
        if self.mode in [APIMode.REAL, APIMode.HYBRID] and self.api_healthy:
            real_result = await self._create_ticket_real(ticket_data)
            if real_result:
                return real_result
        
        # Fallback to mock or if in mock mode
        if self.mode in [APIMode.MOCK, APIMode.HYBRID]:
            return await self._create_ticket_mock(ticket_data)
        
        raise SuperOpsAPIError("Unable to create ticket - API unavailable and mock disabled")

    async def _create_ticket_real(self, ticket_data: Dict) -> Optional[Dict]:
        """Create ticket using real SuperOps API (WORKING FORMAT)"""
        # Build the createTicket mutation payload using WORKING format
        payload = {
            "query": """
                mutation createTicket($input: CreateTicketInput!) {
                    createTicket(input: $input) {
                        ticketId
                        status
                        subject
                        requester
                        technician
                        site
                        requestType
                        source
                        department
                    }
                }
            """,
            "variables": {
                "input": {
                    "source": "FORM",
                    "subject": ticket_data.get("subject", "API Created Ticket"),
                    "requestType": ticket_data.get("requestType", "Incident"),
                    "technician": {
                        "userId": ticket_data.get("assigneeId", "5066433879474626560")
                    },
                    "site": {
                        "id": ticket_data.get("siteId", "6027178066613911552")
                    },
                    "description": ticket_data.get("description", "Ticket created via API")
                }
            }
        }
        
        result = await self._execute_real_api_call("create_ticket", payload)
        
        if result and "data" in result and "createTicket" in result["data"]:
            ticket = result["data"]["createTicket"]
            return {
                "id": ticket.get("ticketId"),
                "ticketId": ticket.get("ticketId"),
                "subject": ticket.get("subject"),
                "status": ticket.get("status"),
                "requestType": ticket.get("requestType"),
                "source": ticket.get("source"),
                "technician": ticket.get("technician"),
                "site": ticket.get("site"),
                "department": ticket.get("department")
            }
        
        return None

    async def create_task(self, task_data: Dict) -> Dict:
        """Create a new task with intelligent fallback"""
        self.logger.info("Creating task...")
        
        # Try real API first if in real or hybrid mode
        if self.mode in [APIMode.REAL, APIMode.HYBRID] and self.api_healthy:
            real_result = await self._create_task_real(task_data)
            if real_result:
                return real_result
        
        # Fallback to mock or if in mock mode
        if self.mode in [APIMode.MOCK, APIMode.HYBRID]:
            return await self._create_task_mock(task_data)
        
        raise SuperOpsAPIError("Unable to create task - API unavailable and mock disabled")

    async def _create_task_real(self, task_data: Dict) -> Optional[Dict]:
        """Create task using real SuperOps API (WORKING FORMAT)"""
        # Build the createTask mutation payload using WORKING format
        payload = {
            "query": """
                mutation createTask($input: CreateTaskInput!) {
                    createTask(input: $input) {
                        taskId
                        title
                        description
                        status
                    }
                }
            """,
            "variables": {
                "input": {
                    "title": task_data.get("title", "API Created Task"),
                    "description": task_data.get("description", "<p>Task created via API</p>"),
                    "estimatedTime": task_data.get("estimatedTime", 180),
                    "status": task_data.get("status", "In Progress"),
                    "scheduledStartDate": task_data.get("scheduledStartDate", "2025-10-01T00:00"),
                    "techGroup": {
                        "groupId": task_data.get("techGroupId", "6410137295585656832")
                    },
                    "technician": {
                        "userId": task_data.get("technicianId", "5066433879474626560")
                    },
                    "workItem": {
                        "workId": task_data.get("workId", "6028540472074190848"),
                        "module": task_data.get("module", "TICKET")
                    }
                }
            }
        }
        
        result = await self._execute_real_api_call("create_task", payload)
        
        if result and "data" in result and "createTask" in result["data"]:
            task = result["data"]["createTask"]
            return {
                "id": task.get("taskId"),
                "taskId": task.get("taskId"),
                "title": task.get("title"),
                "description": task.get("description"),
                "status": task.get("status")
            }
        
        return None

    async def _create_task_mock(self, task_data: Dict) -> Dict:
        """Create task using mock data"""
        await asyncio.sleep(0.1)  # Simulate API delay
        
        task_id = self._generate_mock_id("TASK")
        
        mock_task = {
            "id": task_id,
            "taskId": task_id,
            "title": task_data.get("title", "Mock Task"),
            "description": task_data.get("description", "Mock task description"),
            "status": task_data.get("status", "In Progress"),
            "estimatedTime": task_data.get("estimatedTime", 180),
            "scheduledStartDate": task_data.get("scheduledStartDate", "2025-10-01T00:00"),
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat(),
            "technician": {
                "userId": task_data.get("technicianId", "5066433879474626560"),
                "name": "Mock Technician"
            },
            "workItem": {
                "workId": task_data.get("workId", "6028540472074190848"),
                "module": task_data.get("module", "TICKET")
            }
        }
        
        self.mock_tasks[task_id] = mock_task
        self.logger.info(f"Mock task created: {task_id}")
        
        return mock_task

    async def _create_ticket_mock(self, ticket_data: Dict) -> Dict:
        """Create ticket using mock data"""
        await asyncio.sleep(0.1)  # Simulate API delay
        
        ticket_id = self._generate_mock_id()
        ticket_number = self._generate_mock_number()
        
        mock_ticket = {
            "id": ticket_id,
            "number": ticket_number,
            "subject": ticket_data.get("subject", "No Subject"),
            "description": ticket_data.get("description", "No Description"),
            "priority": ticket_data.get("priority", "Medium"),
            "status": ticket_data.get("status", "Open"),
            "ticketType": ticket_data.get("ticketType", "Incident"),
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat(),
            "requester": {
                "id": "mock-user-1",
                "name": "Mock User",
                "email": ticket_data.get("requesterEmail", "user@example.com")
            },
            "technician": None
        }
        
        # Add technician if provided
        if ticket_data.get("assigneeId"):
            mock_ticket["technician"] = {
                "id": ticket_data["assigneeId"],
                "name": "Mock Technician",
                "email": ticket_data["assigneeId"]
            }
        
        self.mock_tickets[ticket_id] = mock_ticket
        self.logger.info(f"Mock ticket created: {ticket_id}")
        
        return mock_ticket

    async def update_ticket(self, ticket_id: str, update_data: Dict) -> Dict:
        """Update an existing ticket"""
        self.logger.info(f"Updating ticket: {ticket_id}")
        
        # Try real API first
        if self.mode in [APIMode.REAL, APIMode.HYBRID] and self.api_healthy:
            real_result = await self._update_ticket_real(ticket_id, update_data)
            if real_result:
                return real_result
        
        # Fallback to mock
        if self.mode in [APIMode.MOCK, APIMode.HYBRID]:
            return await self._update_ticket_mock(ticket_id, update_data)
        
        raise SuperOpsAPIError("Unable to update ticket")

    async def _update_ticket_real(self, ticket_id: str, update_data: Dict) -> Optional[Dict]:
        """Update ticket using real API"""
        # Implementation would go here
        return None

    async def _update_ticket_mock(self, ticket_id: str, update_data: Dict) -> Dict:
        """Update ticket using mock data"""
        await asyncio.sleep(0.1)
        
        if ticket_id not in self.mock_tickets:
            raise SuperOpsAPIError(f"Ticket {ticket_id} not found")
        
        ticket = self.mock_tickets[ticket_id]
        
        # Update fields
        for key, value in update_data.items():
            if key in ["subject", "description", "priority", "status", "ticketType"]:
                ticket[key] = value
        
        ticket["updatedAt"] = datetime.now().isoformat()
        
        self.logger.info(f"Mock ticket updated: {ticket_id}")
        return ticket

    async def assign_ticket(self, ticket_id: str, assignee: str, notes: str = "") -> Dict:
        """Assign ticket to a technician"""
        self.logger.info(f"Assigning ticket {ticket_id} to {assignee}")
        
        # Try real API first
        if self.mode in [APIMode.REAL, APIMode.HYBRID] and self.api_healthy:
            real_result = await self._assign_ticket_real(ticket_id, assignee, notes)
            if real_result:
                return real_result
        
        # Fallback to mock
        if self.mode in [APIMode.MOCK, APIMode.HYBRID]:
            return await self._assign_ticket_mock(ticket_id, assignee, notes)
        
        raise SuperOpsAPIError("Unable to assign ticket")

    async def _assign_ticket_real(self, ticket_id: str, assignee: str, notes: str) -> Optional[Dict]:
        """Assign ticket using real API"""
        # Implementation would go here
        return None

    async def _assign_ticket_mock(self, ticket_id: str, assignee: str, notes: str) -> Dict:
        """Assign ticket using mock data"""
        await asyncio.sleep(0.1)
        
        if ticket_id not in self.mock_tickets:
            raise SuperOpsAPIError(f"Ticket {ticket_id} not found")
        
        ticket = self.mock_tickets[ticket_id]
        ticket["technician"] = {
            "id": assignee,
            "name": f"Technician {assignee}",
            "email": assignee if "@" in assignee else f"{assignee}@example.com"
        }
        ticket["updatedAt"] = datetime.now().isoformat()
        
        result = {
            "id": ticket_id,
            "number": ticket["number"],
            "assignee": ticket["technician"],
            "updatedAt": ticket["updatedAt"],
            "notes": notes
        }
        
        self.logger.info(f"Mock ticket assigned: {ticket_id} to {assignee}")
        return result

    async def add_work_log(self, work_log: Dict) -> Dict:
        """Add work log entry"""
        ticket_id = work_log.get("ticket_id")
        self.logger.info(f"Adding work log for ticket: {ticket_id}")
        
        # Try real API first
        if self.mode in [APIMode.REAL, APIMode.HYBRID] and self.api_healthy:
            real_result = await self._add_work_log_real(work_log)
            if real_result:
                return real_result
        
        # Fallback to mock
        if self.mode in [APIMode.MOCK, APIMode.HYBRID]:
            return await self._add_work_log_mock(work_log)
        
        raise SuperOpsAPIError("Unable to add work log")

    async def _add_work_log_real(self, work_log: Dict) -> Optional[Dict]:
        """Add work log using real API"""
        # Implementation would go here
        return None

    async def _add_work_log_mock(self, work_log: Dict) -> Dict:
        """Add work log using mock data"""
        await asyncio.sleep(0.1)
        
        work_log_id = self._generate_mock_id("WL")
        
        mock_work_log = {
            "id": work_log_id,
            "ticketId": work_log.get("ticket_id"),
            "description": work_log.get("description", "No description"),
            "timeSpent": work_log.get("time_spent", 0),
            "visibility": work_log.get("visibility", "internal"),
            "workType": work_log.get("work_type", "Investigation"),
            "createdAt": datetime.now().isoformat(),
            "user": {
                "id": "mock-tech-1",
                "name": "Mock Technician"
            }
        }
        
        self.mock_work_logs[work_log_id] = mock_work_log
        
        self.logger.info(f"Mock work log created: {work_log_id}")
        return mock_work_log

    async def get_active_tickets(self) -> List[Dict]:
        """Get all active tickets"""
        self.logger.info("Getting active tickets")
        
        # Try real API first
        if self.mode in [APIMode.REAL, APIMode.HYBRID] and self.api_healthy:
            real_result = await self._get_active_tickets_real()
            if real_result is not None:
                return real_result
        
        # Fallback to mock
        if self.mode in [APIMode.MOCK, APIMode.HYBRID]:
            return await self._get_active_tickets_mock()
        
        return []

    async def _get_active_tickets_real(self) -> Optional[List[Dict]]:
        """Get active tickets using real API"""
        # Implementation would go here
        return None

    async def _get_active_tickets_mock(self) -> List[Dict]:
        """Get active tickets using mock data"""
        await asyncio.sleep(0.1)
        
        active_tickets = [
            ticket for ticket in self.mock_tickets.values()
            if ticket.get("status") not in ["Resolved", "Closed"]
        ]
        
        self.logger.info(f"Found {len(active_tickets)} mock active tickets")
        return active_tickets

    async def get_ticket(self, ticket_id: str) -> Optional[Dict]:
        """Get ticket by ID"""
        self.logger.info(f"Getting ticket: {ticket_id}")
        
        # Try real API first
        if self.mode in [APIMode.REAL, APIMode.HYBRID] and self.api_healthy:
            real_result = await self._get_ticket_real(ticket_id)
            if real_result:
                return real_result
        
        # Fallback to mock
        if self.mode in [APIMode.MOCK, APIMode.HYBRID]:
            return self.mock_tickets.get(ticket_id)
        
        return None

    async def _get_ticket_real(self, ticket_id: str) -> Optional[Dict]:
        """Get ticket using real API"""
        # Implementation would go here
        return None

    def get_api_status(self) -> Dict[str, Any]:
        """Get current API status and statistics"""
        return {
            "mode": self.mode.value,
            "api_healthy": self.api_healthy,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "connected": self.connected,
            "api_url": self.api_url,
            "mock_data": {
                "tickets": len(self.mock_tickets),
                "tasks": len(self.mock_tasks),
                "work_logs": len(self.mock_work_logs),
                "time_entries": len(self.mock_time_entries)
            }
        }

    def get_mock_data_summary(self) -> Dict:
        """Get summary of mock data for testing"""
        return {
            "tickets": len(self.mock_tickets),
            "tasks": len(self.mock_tasks),
            "work_logs": len(self.mock_work_logs),
            "time_entries": len(self.mock_time_entries),
            "sample_tickets": list(self.mock_tickets.keys())[:5],
            "sample_tasks": list(self.mock_tasks.keys())[:5]
        }

    async def disconnect(self):
        """Close connection"""
        if self.session:
            await self.session.close()
        self.connected = False
        self.logger.info("Disconnected from SuperOps API")

    def __str__(self) -> str:
        return f"RobustSuperOpsClient(mode={self.mode.value}, healthy={self.api_healthy})"

