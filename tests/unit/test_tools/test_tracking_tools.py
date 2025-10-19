"""Tests for tracking tools"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, date

from src.tools.tracking.log_work import LogWorkTool
from src.tools.tracking.track_time import TrackTimeTool
from src.tools.tracking.monitor_progress import MonitorProgressTool


class TestLogWorkTool:
    """Test suite for LogWorkTool"""

    @pytest.fixture
    def mock_client(self):
        """Mock SuperOps client"""
        client = AsyncMock()
        client.log_work.return_value = {
            "id": "WRK-001",
            "ticket_id": "TKT-001",
            "time_spent": 2.0,
            "logged_at": datetime.now().isoformat()
        }
        return client

    @pytest.fixture
    def log_work_tool(self, mock_client):
        """Log work tool instance"""
        return LogWorkTool(mock_client)

    @pytest.mark.asyncio
    async def test_log_work_success(self, log_work_tool, mock_client):
        """Test successful work logging"""
        result = await log_work_tool.execute(
            ticket_id="TKT-001",
            description="Troubleshooting network connectivity issues",
            time_spent=2.0,
            work_type="Troubleshooting"
        )

        assert result["success"] is True
        assert result["ticket_id"] == "TKT-001"
        assert result["time_spent"] == 2.0
        assert result["work_type"] == "Troubleshooting"

        mock_client.log_work.assert_called_once()
        call_args = mock_client.log_work.call_args
        assert call_args.kwargs["ticket_id"] == "TKT-001"
        assert call_args.kwargs["time_spent"] == 2.0

    @pytest.mark.asyncio
    async def test_log_work_with_custom_date(self, log_work_tool, mock_client):
        """Test work logging with custom date"""
        custom_date = "2024-01-15"
        result = await log_work_tool.execute(
            ticket_id="TKT-001",
            description="System maintenance",
            time_spent=1.5,
            date=custom_date
        )

        assert result["success"] is True
        assert result["date"] == custom_date

        call_args = mock_client.log_work.call_args
        assert call_args.kwargs["date"] == date(2024, 1, 15)

    @pytest.mark.asyncio
    async def test_log_work_invalid_date(self, log_work_tool):
        """Test work logging with invalid date format"""
        result = await log_work_tool.execute(
            ticket_id="TKT-001",
            description="Test work",
            time_spent=1.0,
            date="invalid-date"
        )

        assert result["success"] is False
        assert "Date must be in YYYY-MM-DD format" in result["error"]

    @pytest.mark.asyncio
    async def test_log_work_missing_required_fields(self, log_work_tool):
        """Test work logging with missing required fields"""
        result = await log_work_tool.execute(
            ticket_id="TKT-001",
            description="Test work"
            # Missing time_spent
        )

        assert result["success"] is False
        assert "Missing required parameter" in result["error"]

    @pytest.mark.asyncio
    async def test_log_work_default_values(self, log_work_tool, mock_client):
        """Test work logging with default values"""
        with patch('src.tools.tracking.log_work.datetime') as mock_datetime:
            mock_datetime.now.return_value.date.return_value = date(2024, 1, 1)

            result = await log_work_tool.execute(
                ticket_id="TKT-001",
                description="Test work",
                time_spent=1.0
                # No work_type or date specified
            )

        assert result["success"] is True
        assert result["work_type"] == "General"

        call_args = mock_client.log_work.call_args
        assert call_args.kwargs["work_type"] == "General"


class TestTrackTimeTool:
    """Test suite for TrackTimeTool"""

    @pytest.fixture
    def mock_client(self):
        """Mock SuperOps client"""
        client = AsyncMock()
        client.start_timer.return_value = {"timer_id": "TMR-001", "started_at": datetime.now().isoformat()}
        client.stop_timer.return_value = {"timer_id": "TMR-001", "time_spent": 2.5}
        client.get_time_report.return_value = {
            "entries": [{"ticket_id": "TKT-001", "time_spent": 2.5}],
            "total_time": 2.5
        }
        client.get_time_summary.return_value = {
            "total_time": 40.0,
            "tickets_worked": 10,
            "average_time_per_ticket": 4.0
        }
        return client

    @pytest.fixture
    def track_time_tool(self, mock_client):
        """Track time tool instance"""
        return TrackTimeTool(mock_client)

    @pytest.mark.asyncio
    async def test_start_timer_success(self, track_time_tool, mock_client):
        """Test successful timer start"""
        result = await track_time_tool.execute(
            action="start_timer",
            ticket_id="TKT-001"
        )

        assert result["success"] is True
        assert result["action"] == "start_timer"
        assert result["ticket_id"] == "TKT-001"
        assert "start_time" in result

        mock_client.start_timer.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_timer_success(self, track_time_tool, mock_client):
        """Test successful timer stop"""
        result = await track_time_tool.execute(
            action="stop_timer",
            ticket_id="TKT-001"
        )

        assert result["success"] is True
        assert result["action"] == "stop_timer"
        assert result["ticket_id"] == "TKT-001"
        assert result["time_spent"] == 2.5

        mock_client.stop_timer.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_time_report(self, track_time_tool, mock_client):
        """Test time report generation"""
        result = await track_time_tool.execute(
            action="get_report",
            technician_id="TECH-001",
            start_date="2024-01-01",
            end_date="2024-01-31"
        )

        assert result["success"] is True
        assert result["action"] == "get_report"
        assert result["total_entries"] == 1
        assert result["total_time"] == 2.5

        mock_client.get_time_report.assert_called_once()
        call_args = mock_client.get_time_report.call_args[0][0]
        assert call_args["technician_id"] == "TECH-001"
        assert call_args["start_date"] == "2024-01-01"

    @pytest.mark.asyncio
    async def test_get_time_summary(self, track_time_tool, mock_client):
        """Test time summary generation"""
        result = await track_time_tool.execute(
            action="get_summary",
            technician_id="TECH-001"
        )

        assert result["success"] is True
        assert result["action"] == "get_summary"
        assert "summary" in result

        mock_client.get_time_summary.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_timer_missing_ticket_id(self, track_time_tool):
        """Test start timer without ticket ID"""
        result = await track_time_tool.execute(action="start_timer")

        assert result["success"] is False
        assert "ticket_id is required" in result["error"]

    @pytest.mark.asyncio
    async def test_unknown_action(self, track_time_tool):
        """Test unknown action"""
        result = await track_time_tool.execute(action="unknown_action")

        assert result["success"] is False
        assert "Unknown action" in result["error"]


class TestMonitorProgressTool:
    """Test suite for MonitorProgressTool"""

    @pytest.fixture
    def mock_client(self):
        """Mock SuperOps client"""
        client = AsyncMock()
        client.check_sla_compliance.return_value = {
            "compliant": 85,
            "breached": 10,
            "at_risk": 5,
            "compliance_rate": 0.85
        }
        client.get_ticket_progress.return_value = {
            "progress_percentage": 75,
            "estimated_completion": "2024-01-20T10:00:00Z",
            "time_spent": 5.5,
            "milestones": ["Analysis Complete", "Solution Identified"]
        }
        client.get_overdue_tickets.return_value = {
            "tickets": [
                {"id": "TKT-001", "priority": "CRITICAL"},
                {"id": "TKT-002", "priority": "HIGH"}
            ],
            "average_overdue_hours": 12
        }
        client.get_progress_metrics.return_value = {
            "tickets_resolved": 45,
            "average_resolution_time": 24.5,
            "first_response_time": 2.3,
            "sla_compliance_rate": 0.92,
            "productivity_score": 87
        }
        return client

    @pytest.fixture
    def monitor_progress_tool(self, mock_client):
        """Monitor progress tool instance"""
        return MonitorProgressTool(mock_client)

    @pytest.mark.asyncio
    async def test_check_sla_compliance(self, monitor_progress_tool, mock_client):
        """Test SLA compliance checking"""
        result = await monitor_progress_tool.execute(
            action="check_sla",
            technician_id="TECH-001"
        )

        assert result["success"] is True
        assert result["action"] == "check_sla"
        assert result["compliant_tickets"] == 85
        assert result["breached_tickets"] == 10
        assert result["compliance_rate"] == 0.85

        mock_client.check_sla_compliance.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_ticket_progress(self, monitor_progress_tool, mock_client):
        """Test individual ticket progress"""
        result = await monitor_progress_tool.execute(
            action="get_progress",
            ticket_id="TKT-001"
        )

        assert result["success"] is True
        assert result["action"] == "get_progress"
        assert result["ticket_id"] == "TKT-001"
        assert result["progress_percentage"] == 75
        assert len(result["milestones"]) == 2

        mock_client.get_ticket_progress.assert_called_once_with("TKT-001")

    @pytest.mark.asyncio
    async def test_get_overdue_tickets(self, monitor_progress_tool, mock_client):
        """Test overdue tickets retrieval"""
        result = await monitor_progress_tool.execute(
            action="get_overdue",
            priority="HIGH"
        )

        assert result["success"] is True
        assert result["action"] == "get_overdue"
        assert result["overdue_count"] == 2
        assert result["critical_overdue"] == 1
        assert result["high_overdue"] == 1

        mock_client.get_overdue_tickets.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_progress_metrics(self, monitor_progress_tool, mock_client):
        """Test progress metrics calculation"""
        result = await monitor_progress_tool.execute(
            action="get_metrics",
            days_back=30,
            technician_id="TECH-001"
        )

        assert result["success"] is True
        assert result["action"] == "get_metrics"
        assert result["period_days"] == 30
        assert result["tickets_resolved"] == 45
        assert result["sla_compliance_rate"] == 0.92

        mock_client.get_progress_metrics.assert_called_once()
        call_args = mock_client.get_progress_metrics.call_args[0][0]
        assert call_args["technician_id"] == "TECH-001"

    @pytest.mark.asyncio
    async def test_unknown_action(self, monitor_progress_tool):
        """Test unknown action"""
        result = await monitor_progress_tool.execute(action="unknown_action")

        assert result["success"] is False
        assert "Unknown action" in result["error"]

    @pytest.mark.asyncio
    async def test_default_days_back(self, monitor_progress_tool, mock_client):
        """Test default days back parameter"""
        result = await monitor_progress_tool.execute(action="get_metrics")

        assert result["success"] is True
        assert result["period_days"] == 30  # Default value
