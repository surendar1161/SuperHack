"""Tests for ticket management tools"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.tools.ticket.create_ticket import CreateTicketTool
from src.tools.ticket.update_ticket import UpdateTicketTool
from src.tools.ticket.resolve_ticket import ResolveTicketTool
from src.tools.ticket.assign_ticket import AssignTicketTool
from src.models.ticket import Priority, Status


class TestCreateTicketTool:
    """Test suite for CreateTicketTool"""

    @pytest.fixture
    def mock_client(self):
        """Mock SuperOps client"""
        client = AsyncMock()
        client.create_ticket.return_value = {
            "id": "TKT-001",
            "number": "TKT-001",
            "title": "Test Ticket",
            "status": "OPEN"
        }
        return client

    @pytest.fixture
    def create_ticket_tool(self, mock_client):
        """Create ticket tool instance"""
        return CreateTicketTool(mock_client)

    @pytest.mark.asyncio
    async def test_create_ticket_success(self, create_ticket_tool, mock_client):
        """Test successful ticket creation"""
        result = await create_ticket_tool.execute(
            title="Password Reset Request",
            description="User cannot access their account",
            priority="HIGH",
            requester_email="user@example.com"
        )

        assert result["success"] is True
        assert result["ticket_id"] == "TKT-001"
        assert result["ticket_number"] == "TKT-001"
        assert "Password Reset Request" in result["message"]

        # Verify client was called with correct parameters
        mock_client.create_ticket.assert_called_once()
        call_args = mock_client.create_ticket.call_args[0][0]
        assert call_args.title == "Password Reset Request"
        assert call_args.priority == Priority.HIGH

    @pytest.mark.asyncio
    async def test_create_ticket_missing_required_fields(self, create_ticket_tool):
        """Test ticket creation with missing required fields"""
        result = await create_ticket_tool.execute(
            title="Test Ticket"
            # Missing description
        )

        assert result["success"] is False
        assert "Missing required parameter" in result["error"]

    @pytest.mark.asyncio
    async def test_create_ticket_invalid_priority(self, create_ticket_tool, mock_client):
        """Test ticket creation with invalid priority"""
        result = await create_ticket_tool.execute(
            title="Test Ticket",
            description="Test description",
            priority="INVALID_PRIORITY"
        )

        # Should default to MEDIUM priority
        assert result["success"] is True
        call_args = mock_client.create_ticket.call_args[0][0]
        assert call_args.priority == Priority.MEDIUM

    @pytest.mark.asyncio
    async def test_create_ticket_client_error(self, create_ticket_tool, mock_client):
        """Test ticket creation when client raises an error"""
        mock_client.create_ticket.side_effect = Exception("API Error")

        result = await create_ticket_tool.execute(
            title="Test Ticket",
            description="Test description"
        )

        assert result["success"] is False
        assert "API Error" in result["error"]

    def test_get_parameters(self, create_ticket_tool):
        """Test parameter schema"""
        params = create_ticket_tool.get_parameters()

        assert "title" in params
        assert params["title"]["required"] is True
        assert "description" in params
        assert params["description"]["required"] is True
        assert "priority" in params
        assert params["priority"]["required"] is False


class TestUpdateTicketTool:
    """Test suite for UpdateTicketTool"""

    @pytest.fixture
    def mock_client(self):
        """Mock SuperOps client"""
        client = AsyncMock()
        client.update_ticket.return_value = {
            "id": "TKT-001",
            "status": "IN_PROGRESS",
            "updated_at": datetime.now().isoformat()
        }
        return client

    @pytest.fixture
    def update_ticket_tool(self, mock_client):
        """Update ticket tool instance"""
        return UpdateTicketTool(mock_client)

    @pytest.mark.asyncio
    async def test_update_ticket_success(self, update_ticket_tool, mock_client):
        """Test successful ticket update"""
        result = await update_ticket_tool.execute(
            ticket_id="TKT-001",
            status="IN_PROGRESS",
            notes="Working on the issue"
        )

        assert result["success"] is True
        assert result["ticket_id"] == "TKT-001"
        assert "status" in result["updated_fields"]
        assert "notes" in result["updated_fields"]

        mock_client.update_ticket.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_ticket_missing_ticket_id(self, update_ticket_tool):
        """Test update without ticket ID"""
        result = await update_ticket_tool.execute(
            status="IN_PROGRESS"
        )

        assert result["success"] is False
        assert "Missing required parameter: ticket_id" in result["error"]

    @pytest.mark.asyncio
    async def test_update_ticket_invalid_status(self, update_ticket_tool, mock_client):
        """Test update with invalid status"""
        result = await update_ticket_tool.execute(
            ticket_id="TKT-001",
            status="INVALID_STATUS"
        )

        # Should still succeed but not include invalid status
        assert result["success"] is True
        call_args = mock_client.update_ticket.call_args[0][1]
        assert not hasattr(call_args, 'status')


class TestResolveTicketTool:
    """Test suite for ResolveTicketTool"""

    @pytest.fixture
    def mock_client(self):
        """Mock SuperOps client"""
        client = AsyncMock()
        client.update_ticket.return_value = {"id": "TKT-001", "status": "RESOLVED"}
        client.log_work.return_value = {"id": "WRK-001"}
        return client

    @pytest.fixture
    def resolve_ticket_tool(self, mock_client):
        """Resolve ticket tool instance"""
        return ResolveTicketTool(mock_client)

    @pytest.mark.asyncio
    async def test_resolve_ticket_success(self, resolve_ticket_tool, mock_client):
        """Test successful ticket resolution"""
        result = await resolve_ticket_tool.execute(
            ticket_id="TKT-001",
            resolution="Password has been reset successfully",
            time_spent=1.5
        )

        assert result["success"] is True
        assert result["ticket_id"] == "TKT-001"
        assert result["resolution"] == "Password has been reset successfully"
        assert result["status"] == Status.CLOSED.value

        # Should call both update_ticket and log_work
        mock_client.update_ticket.assert_called_once()
        mock_client.log_work.assert_called_once()

    @pytest.mark.asyncio
    async def test_resolve_ticket_without_closing(self, resolve_ticket_tool, mock_client):
        """Test resolving without closing ticket"""
        result = await resolve_ticket_tool.execute(
            ticket_id="TKT-001",
            resolution="Issue resolved",
            close_ticket=False
        )

        assert result["success"] is True
        assert result["status"] == Status.RESOLVED.value

        # Verify the status in the update call
        call_args = mock_client.update_ticket.call_args[0][1]
        assert call_args.status == Status.RESOLVED


class TestAssignTicketTool:
    """Test suite for AssignTicketTool"""

    @pytest.fixture
    def mock_client(self):
        """Mock SuperOps client"""
        client = AsyncMock()
        client.update_ticket.return_value = {"id": "TKT-001", "assigned_to": "tech001"}
        client.notify_assignee.return_value = {"success": True}
        return client

    @pytest.fixture
    def assign_ticket_tool(self, mock_client):
        """Assign ticket tool instance"""
        return AssignTicketTool(mock_client)

    @pytest.mark.asyncio
    async def test_assign_ticket_success(self, assign_ticket_tool, mock_client):
        """Test successful ticket assignment"""
        result = await assign_ticket_tool.execute(
            ticket_id="TKT-001",
            assigned_to="tech001",
            assignment_notes="Assigning to senior technician"
        )

        assert result["success"] is True
        assert result["ticket_id"] == "TKT-001"
        assert result["assigned_to"] == "tech001"

        mock_client.update_ticket.assert_called_once()
        mock_client.notify_assignee.assert_called_once_with("TKT-001", "tech001")

    @pytest.mark.asyncio
    async def test_assign_ticket_no_notification(self, assign_ticket_tool, mock_client):
        """Test assignment without notification"""
        result = await assign_ticket_tool.execute(
            ticket_id="TKT-001",
            assigned_to="tech001",
            notify_assignee=False
        )

        assert result["success"] is True
        mock_client.update_ticket.assert_called_once()
        mock_client.notify_assignee.assert_not_called()

    @pytest.mark.asyncio
    async def test_assign_ticket_notification_fails(self, assign_ticket_tool, mock_client):
        """Test assignment when notification fails"""
        mock_client.notify_assignee.side_effect = Exception("Notification failed")

        result = await assign_ticket_tool.execute(
            ticket_id="TKT-001",
            assigned_to="tech001"
        )

        # Assignment should still succeed even if notification fails
        assert result["success"] is True
        mock_client.update_ticket.assert_called_once()
