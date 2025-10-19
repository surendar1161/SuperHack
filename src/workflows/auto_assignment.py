"""Auto-assignment workflow implementation"""

from typing import Dict, Any, List
from .base_workflow import BaseWorkflow
from ..clients.superops_client import SuperOpsClient

class AutoAssignmentWorkflow(BaseWorkflow):
    """Automatically assigns tickets to appropriate technicians"""

    def __init__(self, superops_client: SuperOpsClient):
        super().__init__("auto_assignment")
        self.client = superops_client
        self._setup_workflow()

    def _setup_workflow(self):
        """Setup the workflow steps"""
        self.add_step("analyze_requirements", self._analyze_requirements)
        self.add_step("find_candidates", self._find_candidates)
        self.add_step("score_candidates", self._score_candidates)
        self.add_step("assign_ticket", self._assign_ticket)

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute auto-assignment workflow"""
        ticket_data = context.get("ticket_data", {})
        self.logger.info(f"Auto-assigning ticket: {ticket_data.get('id')}")

        results = {"workflow": "auto_assignment"}

        for i, step in enumerate(self.steps):
            step_result = await self.execute_step(i, context)
            context.update(step_result)

        return {
            "assigned_to": context.get("selected_technician"),
            "assignment_score": context.get("assignment_score"),
            "assignment_reason": context.get("assignment_reason")
        }

    async def _analyze_requirements(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze ticket requirements for assignment"""
        ticket_data = context.get("ticket_data", {})

        requirements = {
            "skills_needed": self._extract_required_skills(ticket_data),
            "priority": ticket_data.get("priority", "medium"),
            "category": ticket_data.get("category", "general"),
            "estimated_effort": self._estimate_effort(ticket_data)
        }

        return {"requirements": requirements}

    async def _find_candidates(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Find candidate technicians"""
        requirements = context.get("requirements", {})

        # Get available technicians (would integrate with real API)
        candidates = await self._get_available_technicians()

        # Filter by skills
        qualified_candidates = [
            tech for tech in candidates
            if self._has_required_skills(tech, requirements["skills_needed"])
        ]

        return {"candidates": qualified_candidates}

    async def _score_candidates(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Score candidates for assignment"""
        candidates = context.get("candidates", [])
        requirements = context.get("requirements", {})

        scored_candidates = []
        for candidate in candidates:
            score = self._calculate_assignment_score(candidate, requirements)
            scored_candidates.append({
                "technician": candidate,
                "score": score
            })

        # Sort by score (highest first)
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)

        return {"scored_candidates": scored_candidates}

    async def _assign_ticket(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Assign ticket to best candidate"""
        scored_candidates = context.get("scored_candidates", [])

        if not scored_candidates:
            return {"assignment_error": "No qualified technicians available"}

        best_candidate = scored_candidates[0]

        return {
            "selected_technician": best_candidate["technician"]["id"],
            "assignment_score": best_candidate["score"],
            "assignment_reason": f"Best match with score {best_candidate['score']}"
        }

    def _extract_required_skills(self, ticket_data: Dict) -> List[str]:
        """Extract required skills from ticket"""
        # Simple keyword-based skill extraction
        description = ticket_data.get("description", "").lower()
        category = ticket_data.get("category", "").lower()

        skills = []
        if "network" in description or "network" in category:
            skills.append("networking")
        if "server" in description or "server" in category:
            skills.append("server_administration")
        if "software" in description or "application" in description:
            skills.append("software_support")

        return skills or ["general_support"]

    def _estimate_effort(self, ticket_data: Dict) -> str:
        """Estimate effort required"""
        priority = ticket_data.get("priority", "medium")
        description_length = len(ticket_data.get("description", ""))

        if priority in ["urgent", "critical"] or description_length > 500:
            return "high"
        elif priority == "high" or description_length > 200:
            return "medium"
        else:
            return "low"

    async def _get_available_technicians(self) -> List[Dict]:
        """Get list of available technicians"""
        # Mock data - would integrate with real API
        return [
            {
                "id": "tech1",
                "name": "John Doe",
                "skills": ["networking", "general_support"],
                "current_workload": 5,
                "max_workload": 10
            },
            {
                "id": "tech2",
                "name": "Jane Smith",
                "skills": ["server_administration", "software_support"],
                "current_workload": 3,
                "max_workload": 8
            }
        ]

    def _has_required_skills(self, technician: Dict, required_skills: List[str]) -> bool:
        """Check if technician has required skills"""
        tech_skills = technician.get("skills", [])
        return any(skill in tech_skills for skill in required_skills)

    def _calculate_assignment_score(self, technician: Dict, requirements: Dict) -> float:
        """Calculate assignment score for technician"""
        score = 0.0

        # Skill match score (0-40 points)
        tech_skills = set(technician.get("skills", []))
        required_skills = set(requirements.get("skills_needed", []))
        skill_match = len(tech_skills.intersection(required_skills)) / max(len(required_skills), 1)
        score += skill_match * 40

        # Workload score (0-30 points)
        current_load = technician.get("current_workload", 0)
        max_load = technician.get("max_workload", 10)
        availability = (max_load - current_load) / max_load
        score += availability * 30

        # Experience score (0-30 points) - simplified
        score += min(len(tech_skills) * 5, 30)

        return round(score, 2)
