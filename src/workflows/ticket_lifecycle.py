"""Ticket lifecycle workflow management"""

from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime, timedelta
import asyncio

from ..clients.superops_client import SuperOpsClient
from ..models.ticket import TicketStatus, Priority
from ..utils.logger import get_logger

class WorkflowStage(str, Enum):
    """Stages in the ticket lifecycle workflow"""
    INTAKE = "intake"
    TRIAGE = "triage"
    ASSIGNMENT = "assignment"
    INVESTIGATION = "investigation"
    RESOLUTION = "resolution"
    VERIFICATION = "verification"
    CLOSURE = "closure"

class TicketLifecycleWorkflow:
    """Manages the complete lifecycle of IT support tickets"""

    def __init__(self, client: SuperOpsClient):
        self.client = client
        self.logger = get_logger(self.__class__.__name__)
        
        # SLA definitions (in hours)
        self.sla_targets = {
            Priority.CRITICAL: {"response": 0.25, "resolution": 4},    # 15 min response, 4h resolution
            Priority.HIGH: {"response": 1, "resolution": 8},           # 1h response, 8h resolution
            Priority.MEDIUM: {"response": 4, "resolution": 24},        # 4h response, 24h resolution
            Priority.LOW: {"response": 8, "resolution": 72}            # 8h response, 72h resolution
        }

    async def process_new_ticket(self, ticket_data: Dict) -> Dict[str, Any]:
        """Process a newly created ticket through initial workflow stages"""
        try:
            ticket_id = ticket_data.get("id")
            self.logger.info(f"Processing new ticket: {ticket_id}")

            # Stage 1: Intake - Basic validation and categorization
            intake_result = await self._intake_stage(ticket_data)
            
            # Stage 2: Triage - Priority assessment and routing
            triage_result = await self._triage_stage(ticket_data, intake_result)
            
            # Stage 3: Assignment - Route to appropriate technician
            assignment_result = await self._assignment_stage(ticket_data, triage_result)

            workflow_result = {
                "ticket_id": ticket_id,
                "workflow_completed": True,
                "stages_completed": [
                    WorkflowStage.INTAKE,
                    WorkflowStage.TRIAGE,
                    WorkflowStage.ASSIGNMENT
                ],
                "intake": intake_result,
                "triage": triage_result,
                "assignment": assignment_result,
                "next_stage": WorkflowStage.INVESTIGATION,
                "sla_targets": self._get_sla_targets(triage_result.get("priority", Priority.MEDIUM))
            }

            self.logger.info(f"Completed initial workflow for ticket {ticket_id}")
            return workflow_result

        except Exception as e:
            self.logger.error(f"Error processing new ticket workflow: {e}")
            return {
                "ticket_id": ticket_data.get("id"),
                "workflow_completed": False,
                "error": str(e),
                "stages_completed": []
            }

    async def _intake_stage(self, ticket_data: Dict) -> Dict[str, Any]:
        """Stage 1: Intake and initial processing"""
        self.logger.info("Executing intake stage")
        
        # Extract and validate basic information
        title = ticket_data.get("subject", ticket_data.get("title", ""))
        description = ticket_data.get("description", "")
        requester = ticket_data.get("requester_email", ticket_data.get("contact_email", ""))

        # Basic validation
        validation_issues = []
        if not title:
            validation_issues.append("Missing ticket title/subject")
        if not description:
            validation_issues.append("Missing ticket description")
        if not requester:
            validation_issues.append("Missing requester information")

        # Auto-categorization based on content
        category = self._auto_categorize(title + " " + description)
        
        # Extract technical details
        technical_details = self._extract_technical_info(description)

        return {
            "stage": WorkflowStage.INTAKE,
            "validation_passed": len(validation_issues) == 0,
            "validation_issues": validation_issues,
            "auto_category": category,
            "technical_details": technical_details,
            "processed_at": datetime.now().isoformat()
        }

    async def _triage_stage(self, ticket_data: Dict, intake_result: Dict) -> Dict[str, Any]:
        """Stage 2: Triage and priority assessment"""
        self.logger.info("Executing triage stage")
        
        title = ticket_data.get("subject", ticket_data.get("title", ""))
        description = ticket_data.get("description", "")
        current_priority = ticket_data.get("priority", "medium")

        # Assess priority based on content and keywords
        assessed_priority = self._assess_priority(title, description)
        
        # Check for escalation triggers
        escalation_triggers = self._check_escalation_triggers(title, description)
        
        # Determine if priority adjustment is needed
        priority_adjustment_needed = assessed_priority.value != current_priority.lower()

        # Calculate SLA targets
        sla_targets = self._get_sla_targets(assessed_priority)

        return {
            "stage": WorkflowStage.TRIAGE,
            "assessed_priority": assessed_priority,
            "current_priority": current_priority,
            "priority_adjustment_needed": priority_adjustment_needed,
            "escalation_triggers": escalation_triggers,
            "requires_escalation": len(escalation_triggers) > 0,
            "sla_targets": sla_targets,
            "processed_at": datetime.now().isoformat()
        }

    async def _assignment_stage(self, ticket_data: Dict, triage_result: Dict) -> Dict[str, Any]:
        """Stage 3: Assignment to appropriate technician"""
        self.logger.info("Executing assignment stage")
        
        priority = triage_result.get("assessed_priority", Priority.MEDIUM)
        category = ticket_data.get("category", "General")
        
        # Get available technicians
        try:
            technicians = await self.client.get_users({"role": "technician", "is_active": True})
        except Exception as e:
            self.logger.warning(f"Could not fetch technicians: {e}")
            technicians = []

        # Find best match technician
        best_match = self._find_best_technician(technicians, category, priority)
        
        # Assignment logic
        assignment_method = "automatic" if best_match else "manual"
        
        return {
            "stage": WorkflowStage.ASSIGNMENT,
            "assignment_method": assignment_method,
            "recommended_assignee": best_match,
            "available_technicians": len(technicians),
            "assignment_criteria": {
                "category": category,
                "priority": priority.value,
                "skills_required": self._get_required_skills(category)
            },
            "processed_at": datetime.now().isoformat()
        }

    def _auto_categorize(self, content: str) -> str:
        """Automatically categorize ticket based on content"""
        content_lower = content.lower()
        
        categories = {
            "Hardware": ["printer", "computer", "laptop", "monitor", "keyboard", "mouse", "hardware"],
            "Software": ["application", "program", "software", "app", "excel", "word", "outlook"],
            "Network": ["internet", "wifi", "network", "connection", "vpn", "connectivity"],
            "Email": ["email", "outlook", "mail", "inbox", "sending", "receiving"],
            "Security": ["password", "login", "access", "account", "security", "locked"],
            "Account": ["user", "account", "profile", "permissions", "new user"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in content_lower for keyword in keywords):
                return category
        
        return "General"

    def _extract_technical_info(self, description: str) -> Dict[str, Any]:
        """Extract technical information from description"""
        import re
        
        # Extract error messages
        error_patterns = [r'"([^"]+)"', r"error:?\s*(.+?)(?:\.|$)"]
        errors = []
        for pattern in error_patterns:
            errors.extend(re.findall(pattern, description, re.IGNORECASE))
        
        # Extract system information
        systems = re.findall(r'\b(windows|mac|linux|outlook|excel|word|chrome|firefox)\b', 
                           description, re.IGNORECASE)
        
        return {
            "error_messages": errors,
            "systems_mentioned": list(set(systems)),
            "has_technical_details": len(errors) > 0 or len(systems) > 0
        }

    def _assess_priority(self, title: str, description: str) -> Priority:
        """Assess ticket priority based on content"""
        content = (title + " " + description).lower()
        
        critical_keywords = ["critical", "emergency", "down", "outage", "cannot work", "production"]
        high_keywords = ["urgent", "asap", "important", "not working", "broken"]
        low_keywords = ["question", "how to", "enhancement", "when convenient"]
        
        if any(keyword in content for keyword in critical_keywords):
            return Priority.CRITICAL
        elif any(keyword in content for keyword in high_keywords):
            return Priority.HIGH
        elif any(keyword in content for keyword in low_keywords):
            return Priority.LOW
        else:
            return Priority.MEDIUM

    def _check_escalation_triggers(self, title: str, description: str) -> List[str]:
        """Check for conditions that require escalation"""
        content = (title + " " + description).lower()
        triggers = []
        
        escalation_conditions = {
            "security_incident": ["security breach", "hack", "malware", "virus", "data breach"],
            "system_outage": ["system down", "server down", "network down", "outage"],
            "data_loss": ["lost data", "deleted files", "corrupted", "cannot access files"],
            "multiple_users": ["all users", "everyone", "department", "office"]
        }
        
        for trigger_type, keywords in escalation_conditions.items():
            if any(keyword in content for keyword in keywords):
                triggers.append(trigger_type)
        
        return triggers

    def _get_sla_targets(self, priority: Priority) -> Dict[str, Any]:
        """Get SLA targets for given priority"""
        targets = self.sla_targets.get(priority, self.sla_targets[Priority.MEDIUM])
        now = datetime.now()
        
        return {
            "response_time_hours": targets["response"],
            "resolution_time_hours": targets["resolution"],
            "response_due": (now + timedelta(hours=targets["response"])).isoformat(),
            "resolution_due": (now + timedelta(hours=targets["resolution"])).isoformat()
        }

    def _find_best_technician(self, technicians: List[Dict], category: str, priority: Priority) -> Optional[Dict]:
        """Find the best technician for assignment"""
        if not technicians:
            return None
        
        # Score technicians based on various factors
        scored_technicians = []
        
        for tech in technicians:
            score = 0
            
            # Skills match
            skills = tech.get("skills", [])
            if category.lower() in [skill.lower() for skill in skills]:
                score += 10
            
            # Workload (prefer less busy technicians)
            current_tickets = tech.get("current_ticket_count", 0)
            max_tickets = tech.get("max_concurrent_tickets", 10)
            if current_tickets < max_tickets:
                score += (max_tickets - current_tickets)
            
            # Priority handling capability
            if priority in [Priority.CRITICAL, Priority.HIGH]:
                if "senior" in tech.get("role", "").lower():
                    score += 5
            
            scored_technicians.append((score, tech))
        
        # Return technician with highest score
        if scored_technicians:
            scored_technicians.sort(key=lambda x: x[0], reverse=True)
            return scored_technicians[0][1]
        
        return None

    def _get_required_skills(self, category: str) -> List[str]:
        """Get required skills for a category"""
        skill_map = {
            "Hardware": ["hardware_troubleshooting", "desktop_support"],
            "Software": ["software_support", "application_troubleshooting"],
            "Network": ["network_administration", "connectivity_issues"],
            "Email": ["email_administration", "outlook_support"],
            "Security": ["security_administration", "access_management"],
            "Account": ["user_management", "active_directory"]
        }
        
        return skill_map.get(category, ["general_support"])

    async def check_sla_compliance(self, ticket_id: str) -> Dict[str, Any]:
        """Check SLA compliance for a ticket"""
        try:
            ticket = await self.client.get_ticket(ticket_id)
            if not ticket:
                return {"error": "Ticket not found"}
            
            created_at = datetime.fromisoformat(ticket.get("created_at", ""))
            priority = Priority(ticket.get("priority", "medium"))
            status = ticket.get("status", "new")
            
            sla_targets = self._get_sla_targets(priority)
            now = datetime.now()
            
            # Calculate elapsed time
            elapsed_hours = (now - created_at).total_seconds() / 3600
            
            # Check response SLA
            response_sla_met = elapsed_hours <= sla_targets["response_time_hours"] or status != "new"
            
            # Check resolution SLA
            resolution_sla_met = (
                status in ["resolved", "closed"] and 
                elapsed_hours <= sla_targets["resolution_time_hours"]
            ) or status not in ["resolved", "closed"]
            
            return {
                "ticket_id": ticket_id,
                "priority": priority.value,
                "elapsed_hours": round(elapsed_hours, 2),
                "response_sla": {
                    "target_hours": sla_targets["response_time_hours"],
                    "met": response_sla_met,
                    "overdue_by": max(0, elapsed_hours - sla_targets["response_time_hours"])
                },
                "resolution_sla": {
                    "target_hours": sla_targets["resolution_time_hours"],
                    "met": resolution_sla_met,
                    "overdue_by": max(0, elapsed_hours - sla_targets["resolution_time_hours"])
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error checking SLA compliance: {e}")
            return {"error": str(e)}