"""Mock SuperOps client for testing and development"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from ..utils.logger import get_logger

class MockSuperOpsClient:
    """Mock SuperOps client for testing tool functionality"""

    def __init__(self, config=None):
        self.config = config
        self.logger = get_logger(self.__class__.__name__)
        self.tickets = {}  # In-memory ticket storage
        self.work_logs = {}  # In-memory work log storage
        self.time_entries = {}  # In-memory time entry storage
        self.connected = False

    async def connect(self):
        """Mock connection to SuperOps API"""
        self.logger.info("Connecting to Mock SuperOps API")
        await asyncio.sleep(0.1)  # Simulate connection delay
        self.connected = True
        self.logger.info("Connected to Mock SuperOps API successfully")

    async def disconnect(self):
        """Mock disconnection from SuperOps API"""
        self.connected = False
        self.logger.info("Disconnected from Mock SuperOps API")

    def _generate_ticket_id(self) -> str:
        """Generate a mock ticket ID"""
        return f"MOCK-{uuid.uuid4().hex[:8].upper()}"

    def _generate_ticket_number(self) -> str:
        """Generate a mock ticket number"""
        return f"TKT-{len(self.tickets) + 1:06d}"

    async def create_ticket(self, ticket_data: Dict) -> Dict:
        """Mock ticket creation"""
        self.logger.info("Creating mock ticket")
        
        # Simulate API processing delay
        await asyncio.sleep(0.2)
        
        # Generate mock ticket
        ticket_id = self._generate_ticket_id()
        ticket_number = self._generate_ticket_number()
        
        mock_ticket = {
            "id": ticket_id,
            "number": ticket_number,
            "subject": ticket_data.get("subject", "No Subject"),
            "description": ticket_data.get("description", "No Description"),
            "priority": ticket_data.get("priority", "MEDIUM").upper(),
            "status": ticket_data.get("status", "NEW").upper(),
            "category": ticket_data.get("category", "GENERAL").upper(),
            "source": ticket_data.get("source", "API").upper(),
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat(),
            "requester": {
                "id": "mock-user-1",
                "name": "Mock User",
                "email": ticket_data.get("requesterEmail", "user@example.com")
            },
            "assignee": None
        }
        
        # Add assignee if provided
        if ticket_data.get("assigneeId"):
            mock_ticket["assignee"] = {
                "id": ticket_data["assigneeId"],
                "name": "Mock Technician",
                "email": ticket_data["assigneeId"]
            }
        
        # Store ticket
        self.tickets[ticket_id] = mock_ticket
        
        self.logger.info(f"Mock ticket created: {ticket_id}")
        return mock_ticket

    async def update_ticket(self, ticket_id: str, update_data: Dict) -> Dict:
        """Mock ticket update"""
        self.logger.info(f"Updating mock ticket: {ticket_id}")
        
        await asyncio.sleep(0.1)
        
        if ticket_id not in self.tickets:
            raise Exception(f"Ticket {ticket_id} not found")
        
        ticket = self.tickets[ticket_id]
        
        # Update fields from input data
        for key, value in update_data.items():
            if key in ["subject", "description", "priority", "status", "category"]:
                ticket[key] = value
        
        ticket["updatedAt"] = datetime.now().isoformat()
        
        self.logger.info(f"Mock ticket updated: {ticket_id}")
        return ticket

    async def assign_ticket(self, ticket_id: str, assignee: str, notes: str = "") -> Dict:
        """Mock ticket assignment"""
        self.logger.info(f"Assigning mock ticket {ticket_id} to {assignee}")
        
        await asyncio.sleep(0.1)
        
        if ticket_id not in self.tickets:
            raise Exception(f"Ticket {ticket_id} not found")
        
        ticket = self.tickets[ticket_id]
        ticket["assignee"] = {
            "id": assignee,
            "name": f"Technician {assignee}",
            "email": assignee if "@" in assignee else f"{assignee}@example.com"
        }
        ticket["updatedAt"] = datetime.now().isoformat()
        
        # Create assignment record
        assignment_result = {
            "id": ticket_id,
            "number": ticket["number"],
            "assignee": ticket["assignee"],
            "updatedAt": ticket["updatedAt"],
            "notes": notes
        }
        
        self.logger.info(f"Mock ticket assigned: {ticket_id} to {assignee}")
        return assignment_result

    async def get_ticket(self, ticket_id: str) -> Optional[Dict]:
        """Mock get ticket"""
        self.logger.info(f"Getting mock ticket: {ticket_id}")
        
        await asyncio.sleep(0.1)
        
        return self.tickets.get(ticket_id)

    async def resolve_ticket(self, ticket_id: str, resolution: str, time_spent: float = 0) -> Dict:
        """Mock ticket resolution"""
        self.logger.info(f"Resolving mock ticket: {ticket_id}")
        
        await asyncio.sleep(0.1)
        
        if ticket_id not in self.tickets:
            raise Exception(f"Ticket {ticket_id} not found")
        
        ticket = self.tickets[ticket_id]
        ticket["status"] = "RESOLVED"
        ticket["resolution"] = resolution
        ticket["resolvedAt"] = datetime.now().isoformat()
        ticket["updatedAt"] = datetime.now().isoformat()
        
        if time_spent > 0:
            ticket["timeSpent"] = time_spent
        
        result = {
            "id": ticket_id,
            "number": ticket["number"],
            "status": ticket["status"],
            "resolution": resolution,
            "resolvedAt": ticket["resolvedAt"],
            "updatedAt": ticket["updatedAt"]
        }
        
        self.logger.info(f"Mock ticket resolved: {ticket_id}")
        return result

    async def add_work_log(self, work_log: Dict) -> Dict:
        """Mock work log creation"""
        ticket_id = work_log.get("ticket_id")
        self.logger.info(f"Adding mock work log for ticket: {ticket_id}")
        
        await asyncio.sleep(0.1)
        
        work_log_id = f"WL-{uuid.uuid4().hex[:8].upper()}"
        
        mock_work_log = {
            "id": work_log_id,
            "ticketId": ticket_id,
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
        
        # Store work log
        self.work_logs[work_log_id] = mock_work_log
        
        self.logger.info(f"Mock work log created: {work_log_id}")
        return mock_work_log

    async def log_time_entry(self, time_entry: Dict) -> Dict:
        """Mock time entry logging"""
        ticket_id = time_entry.get("ticketId")
        self.logger.info(f"Logging mock time entry for ticket: {ticket_id}")
        
        await asyncio.sleep(0.1)
        
        time_entry_id = f"TE-{uuid.uuid4().hex[:8].upper()}"
        
        mock_time_entry = {
            "id": time_entry_id,
            "ticketId": ticket_id,
            "duration": time_entry.get("duration", 0),
            "description": time_entry.get("description", "Time entry"),
            "billable": time_entry.get("billable", True),
            "createdAt": datetime.now().isoformat(),
            "user": {
                "id": "mock-tech-1",
                "name": "Mock Technician"
            }
        }
        
        # Store time entry
        self.time_entries[time_entry_id] = mock_time_entry
        
        self.logger.info(f"Mock time entry created: {time_entry_id}")
        return mock_time_entry

    async def get_active_tickets(self) -> List[Dict]:
        """Mock get active tickets"""
        self.logger.info("Getting mock active tickets")
        
        await asyncio.sleep(0.1)
        
        # Return tickets that are not resolved or closed
        active_tickets = [
            ticket for ticket in self.tickets.values()
            if ticket.get("status") not in ["RESOLVED", "CLOSED"]
        ]
        
        self.logger.info(f"Found {len(active_tickets)} mock active tickets")
        return active_tickets

    async def get_tickets_by_date_range(self, date_range: str, filters: Dict = None) -> List[Dict]:
        """Mock get tickets by date range"""
        self.logger.info(f"Getting mock tickets by date range: {date_range}")
        
        await asyncio.sleep(0.1)
        
        # For mock, just return all tickets
        tickets = list(self.tickets.values())
        
        # Apply basic filters if provided
        if filters:
            if filters.get("status"):
                tickets = [t for t in tickets if t.get("status") == filters["status"].upper()]
            if filters.get("priority"):
                tickets = [t for t in tickets if t.get("priority") == filters["priority"].upper()]
        
        self.logger.info(f"Found {len(tickets)} mock tickets for date range")
        return tickets

    async def get_ticket_analytics(self, date_range: str, filters: Optional[Dict] = None) -> Dict:
        """Mock ticket analytics"""
        self.logger.info(f"Getting mock ticket analytics for: {date_range}")
        
        await asyncio.sleep(0.1)
        
        tickets = list(self.tickets.values())
        
        # Generate mock analytics
        analytics = {
            "totalTickets": len(tickets),
            "resolvedTickets": len([t for t in tickets if t.get("status") == "RESOLVED"]),
            "averageResolutionTime": 2.5,  # Mock average in hours
            "ticketsByStatus": [
                {"status": "NEW", "count": len([t for t in tickets if t.get("status") == "NEW"])},
                {"status": "IN_PROGRESS", "count": len([t for t in tickets if t.get("status") == "IN_PROGRESS"])},
                {"status": "RESOLVED", "count": len([t for t in tickets if t.get("status") == "RESOLVED"])}
            ],
            "ticketsByPriority": [
                {"priority": "LOW", "count": len([t for t in tickets if t.get("priority") == "LOW"])},
                {"priority": "MEDIUM", "count": len([t for t in tickets if t.get("priority") == "MEDIUM"])},
                {"priority": "HIGH", "count": len([t for t in tickets if t.get("priority") == "HIGH"])},
                {"priority": "CRITICAL", "count": len([t for t in tickets if t.get("priority") == "CRITICAL"])}
            ]
        }
        
        self.logger.info("Generated mock ticket analytics")
        return analytics

    def get_mock_data_summary(self) -> Dict:
        """Get summary of mock data for testing"""
        return {
            "tickets": len(self.tickets),
            "work_logs": len(self.work_logs),
            "time_entries": len(self.time_entries),
            "sample_tickets": list(self.tickets.keys())[:5]
        }