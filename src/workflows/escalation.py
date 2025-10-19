"""Escalation workflow implementation"""

from typing import Dict, Any
from datetime import datetime, timedelta
from .base_workflow import BaseWorkflow
from ..clients.superops_client import SuperOpsClient

class EscalationWorkflow(BaseWorkflow):
    """Handles ticket escalation based on various criteria"""

    def __init__(self, superops_client: SuperOpsClient):
        super().__init__("escalation")
        self.client = superops_client
        self._setup_workflow()

    def _setup_workflow(self):
        """Setup the workflow steps"""
        self.add_step("evaluate_criteria", self._evaluate_criteria)
        self.add_step("determine_level", self._determine_level)
        self.add_step("prepare_handover", self._prepare_handover)
        self.add_step("execute_escalation", self._execute_escalation)

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute escalation workflow"""
        ticket_id = context.get("ticket_id")
        self.logger.info(f"Evaluating escalation for ticket: {ticket_id}")

        for i, step in enumerate(self.steps):
            step_result = await self.execute_step(i, context)
            context.update(step_result)

            # Stop if no escalation needed
            if step_result.get("escalation_needed") is False:
                return {"escalation_needed": False, "reason": step_result.get("reason")}

        return {
            "escalation_needed": True,
            "escalation_level": context.get("escalation_level"),
            "target_team": context.get("target_team"),
            "handover_notes": context.get("handover_notes")
        }

    async def _evaluate_criteria(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate escalation criteria"""
        ticket_data = context.get("ticket_data", {})

        # Time-based criteria
        created_at = datetime.fromisoformat(ticket_data.get("created_at", datetime.now().isoformat()))
        time_elapsed = (datetime.now() - created_at).total_seconds() / 3600

        # Priority-based SLA thresholds
        sla_thresholds = {
            "critical": 1,
            "urgent": 4,
            "high": 8,
            "medium": 24,
            "low": 72
        }

        priority = ticket_data.get("priority", "medium")
        sla_threshold = sla_thresholds.get(priority, 24)

        escalation_reasons = []

        # Check time-based escalation
        if time_elapsed > sla_threshold:
            escalation_reasons.append(f"SLA breach: {time_elapsed:.1f}h > {sla_threshold}h")

        # Check complexity escalation
        if ticket_data.get("escalated_before"):
            escalation_reasons.append("Previously escalated")

        # Check business impact
        if ticket_data.get("business_critical"):
            escalation_reasons.append("Business critical system affected")

        # Check resolution attempts
        attempts = ticket_data.get("resolution_attempts", 0)
        if attempts >= 3:
            escalation_reasons.append(f"Multiple resolution attempts: {attempts}")

        escalation_needed = len(escalation_reasons) > 0

        return {
            "escalation_needed": escalation_needed,
            "escalation_reasons": escalation_reasons,
            "time_elapsed": time_elapsed,
            "sla_threshold": sla_threshold
        }

    async def _determine_level(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Determine escalation level and target"""
        if not context.get("escalation_needed"):
            return {}

        ticket_data = context.get("ticket_data", {})
        escalation_reasons = context.get("escalation_reasons", [])

        # Determine escalation level
        if any("business critical" in reason.lower() for reason in escalation_reasons):
            level = "L3"
            target_team = "senior_engineers"
        elif any("sla breach" in reason.lower() for reason in escalation_reasons):
            level = "L2"
            target_team = "senior_technicians"
        elif ticket_data.get("priority") in ["critical", "urgent"]:
            level = "L2"
            target_team = "senior_technicians"
        else:
            level = "L2"
            target_team = "team_lead"

        return {
            "escalation_level": level,
            "target_team": target_team
        }

    async def _prepare_handover(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare handover documentation"""
        ticket_data = context.get("ticket_data", {})
        escalation_reasons = context.get("escalation_reasons", [])

        handover_notes = {
            "escalation_reasons": escalation_reasons,
            "time_elapsed": f"{context.get('time_elapsed', 0):.1f} hours",
            "priority": ticket_data.get("priority"),
            "current_status": ticket_data.get("status"),
            "resolution_attempts": ticket_data.get("resolution_attempts", 0),
            "technical_summary": ticket_data.get("description", "")[:500],
            "next_steps_recommended": self._generate_next_steps(ticket_data),
            "escalation_timestamp": datetime.now().isoformat()
        }

        return {"handover_notes": handover_notes}

    async def _execute_escalation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the escalation"""
        ticket_id = context.get("ticket_id")
        escalation_level = context.get("escalation_level")
        target_team = context.get("target_team")

        # Would integrate with actual escalation system
        self.logger.info(f"Escalating ticket {ticket_id} to {escalation_level} ({target_team})")

        return {
            "escalation_executed": True,
            "escalation_id": f"ESC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        }

    def _generate_next_steps(self, ticket_data: Dict[str, Any]) -> list:
        """Generate recommended next steps"""
        category = ticket_data.get("category", "").lower()
        priority = ticket_data.get("priority", "medium")

        if "network" in category:
            return [
                "Perform network topology analysis",
                "Check switch/router configurations",
                "Review network monitoring alerts"
            ]
        elif "server" in category:
            return [
                "Check server resource utilization",
                "Review system logs for errors",
                "Verify service dependencies"
            ]
        elif priority in ["critical", "urgent"]:
            return [
                "Immediate impact assessment",
                "Engage vendor support if needed",
                "Consider temporary workaround"
            ]
        else:
            return [
                "Detailed technical analysis required",
                "Consult knowledge base and documentation",
                "Consider peer consultation"
            ]
