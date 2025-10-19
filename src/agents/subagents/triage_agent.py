"""
Triage Agent - First line analysis and ticket categorization
Part of the multi-agent IT technician system
"""

from typing import Any, Dict, List, Optional
from strands import Agent, tool

from ..config import AgentConfig
from ...clients.superops_client import SuperOpsClient
from ...memory.memory_manager import MemoryManager
from ...utils.logger import get_logger

class TriageAgent(Agent):
    """
    Specialized agent for initial ticket triage and categorization.
    Performs first-line analysis to determine ticket priority, complexity, and routing.
    """
    
    def __init__(self, config: AgentConfig, superops_client: SuperOpsClient, memory_manager: MemoryManager):
        self.config = config
        self.superops_client = superops_client
        self.memory_manager = memory_manager
        self.logger = get_logger(self.__class__.__name__)
        
        super().__init__(
            name="TriageAgent",
            description="Analyzes incoming tickets for priority, complexity, and proper routing",
            tools=self._get_triage_tools()
        )
    
    def _get_triage_tools(self) -> List[Any]:
        """Get tools for ticket triage"""
        return [
            self._get_analyze_ticket_tool(),
            self._get_categorize_issue_tool(),
            self._get_assess_urgency_tool(),
            self._get_determine_routing_tool()
        ]
    
    def _get_analyze_ticket_tool(self) -> Any:
        """Tool for analyzing ticket content"""
        async def analyze_ticket(ticket_data: Dict[str, Any]) -> Dict[str, Any]:
            """Analyze ticket for key information and patterns"""
            try:
                # Extract key information
                subject = ticket_data.get('subject', '')
                description = ticket_data.get('description', '')
                priority = ticket_data.get('priority', 'Medium')
                
                # Keywords that indicate complexity
                complex_keywords = [
                    'server down', 'network outage', 'database', 'security breach',
                    'system crash', 'corruption', 'virus', 'malware', 'hack'
                ]
                
                simple_keywords = [
                    'password reset', 'email setup', 'printer', 'software install',
                    'user account', 'permission', 'access request'
                ]
                
                # Analyze content
                content = f"{subject} {description}".lower()
                
                complexity_score = 0
                if any(keyword in content for keyword in complex_keywords):
                    complexity_score += 3
                if any(keyword in content for keyword in simple_keywords):
                    complexity_score -= 1
                
                # Determine complexity level
                if complexity_score >= 3:
                    complexity = "high"
                elif complexity_score >= 1:
                    complexity = "medium"
                else:
                    complexity = "low"
                
                # Extract technical indicators
                technical_terms = []
                tech_patterns = ['error code', 'blue screen', 'timeout', 'connection', 'ssl', 'dns']
                for pattern in tech_patterns:
                    if pattern in content:
                        technical_terms.append(pattern)
                
                return {
                    "ticket_id": ticket_data.get('ticketId'),
                    "complexity": complexity,
                    "complexity_score": complexity_score,
                    "technical_indicators": technical_terms,
                    "requires_specialist": complexity == "high",
                    "estimated_effort": "high" if complexity == "high" else "medium" if complexity == "medium" else "low"
                }
                
            except Exception as e:
                self.logger.error(f"Error analyzing ticket: {e}")
                return {"error": str(e)}
        
        return Tool(
            name="analyze_ticket",
            description="Analyze ticket content for complexity and technical indicators",
            func=analyze_ticket
        )
    
    def _get_categorize_issue_tool(self) -> Any:
        """Tool for categorizing the type of issue"""
        async def categorize_issue(ticket_data: Dict[str, Any]) -> Dict[str, Any]:
            """Categorize the issue type"""
            try:
                content = f"{ticket_data.get('subject', '')} {ticket_data.get('description', '')}".lower()
                
                # Issue categories with keywords
                categories = {
                    "hardware": ["printer", "mouse", "keyboard", "monitor", "laptop", "desktop", "hardware"],
                    "software": ["application", "program", "software", "install", "update", "crash"],
                    "network": ["internet", "wifi", "network", "connection", "dns", "vpn"],
                    "security": ["password", "login", "access", "security", "virus", "malware", "breach"],
                    "email": ["email", "outlook", "mail", "exchange", "smtp"],
                    "system": ["server", "database", "system", "os", "windows", "linux", "mac"],
                    "user_account": ["account", "user", "permission", "active directory", "ldap"]
                }
                
                # Find matching categories
                matched_categories = []
                for category, keywords in categories.items():
                    if any(keyword in content for keyword in keywords):
                        matched_categories.append(category)
                
                # Determine primary category
                primary_category = matched_categories[0] if matched_categories else "general"
                
                return {
                    "primary_category": primary_category,
                    "all_categories": matched_categories,
                    "category_confidence": len(matched_categories) / len(categories)
                }
                
            except Exception as e:
                self.logger.error(f"Error categorizing issue: {e}")
                return {"error": str(e)}
        
        return Tool(
            name="categorize_issue",
            description="Categorize the type of IT issue",
            func=categorize_issue
        )
    
    def _get_assess_urgency_tool(self) -> Any:
        """Tool for assessing ticket urgency"""
        async def assess_urgency(ticket_data: Dict[str, Any]) -> Dict[str, Any]:
            """Assess the urgency of the ticket"""
            try:
                content = f"{ticket_data.get('subject', '')} {ticket_data.get('description', '')}".lower()
                priority = ticket_data.get('priority', 'Medium').lower()
                
                # Urgency indicators
                critical_indicators = [
                    "server down", "system down", "outage", "all users affected",
                    "production", "critical", "emergency", "urgent"
                ]
                
                high_indicators = [
                    "multiple users", "department", "business impact", "deadline"
                ]
                
                low_indicators = [
                    "single user", "training", "enhancement", "when convenient"
                ]
                
                # Calculate urgency score
                urgency_score = 0
                
                if any(indicator in content for indicator in critical_indicators):
                    urgency_score += 5
                if any(indicator in content for indicator in high_indicators):
                    urgency_score += 3
                if any(indicator in content for indicator in low_indicators):
                    urgency_score -= 2
                
                # Factor in stated priority
                priority_weights = {
                    "critical": 5,
                    "high": 3,
                    "medium": 1,
                    "low": -1
                }
                urgency_score += priority_weights.get(priority, 0)
                
                # Determine urgency level
                if urgency_score >= 5:
                    urgency = "critical"
                elif urgency_score >= 3:
                    urgency = "high"
                elif urgency_score >= 1:
                    urgency = "medium"
                else:
                    urgency = "low"
                
                return {
                    "urgency": urgency,
                    "urgency_score": urgency_score,
                    "business_impact": "high" if urgency_score >= 3 else "medium" if urgency_score >= 1 else "low",
                    "sla_target": self._get_sla_target(urgency)
                }
                
            except Exception as e:
                self.logger.error(f"Error assessing urgency: {e}")
                return {"error": str(e)}
        
        return Tool(
            name="assess_urgency",
            description="Assess the urgency and business impact of a ticket",
            func=assess_urgency
        )
    
    def _get_determine_routing_tool(self) -> Any:
        """Tool for determining where to route the ticket"""
        async def determine_routing(analysis_results: Dict[str, Any]) -> Dict[str, Any]:
            """Determine the best routing for the ticket"""
            try:
                complexity = analysis_results.get("complexity", "medium")
                category = analysis_results.get("primary_category", "general")
                urgency = analysis_results.get("urgency", "medium")
                
                # Routing logic
                if complexity == "high" or urgency == "critical":
                    next_agent = "diagnosis"
                    reason = "High complexity or critical urgency requires detailed analysis"
                elif category in ["security", "system", "network"] and complexity != "low":
                    next_agent = "diagnosis"
                    reason = "Technical category requires specialist diagnosis"
                elif complexity == "low" and category in ["user_account", "email", "software"]:
                    next_agent = "resolution"
                    reason = "Simple issue with known resolution path"
                else:
                    next_agent = "diagnosis"
                    reason = "Default routing for further analysis"
                
                # Check if escalation is immediately needed
                if urgency == "critical" and complexity == "high":
                    escalation_recommended = True
                    escalation_reason = "Critical urgency with high complexity"
                else:
                    escalation_recommended = False
                    escalation_reason = None
                
                return {
                    "next_agent": next_agent,
                    "routing_reason": reason,
                    "escalation_recommended": escalation_recommended,
                    "escalation_reason": escalation_reason,
                    "estimated_resolution_time": self._estimate_resolution_time(complexity, urgency),
                    "specialist_required": complexity == "high" or category in ["security", "network"]
                }
                
            except Exception as e:
                self.logger.error(f"Error determining routing: {e}")
                return {"error": str(e)}
        
        return Tool(
            name="determine_routing",
            description="Determine the best routing path for the ticket",
            func=determine_routing
        )
    
    def _get_sla_target(self, urgency: str) -> str:
        """Get SLA target based on urgency"""
        sla_targets = {
            "critical": "1 hour",
            "high": "4 hours",
            "medium": "1 day",
            "low": "3 days"
        }
        return sla_targets.get(urgency, "1 day")
    
    def _estimate_resolution_time(self, complexity: str, urgency: str) -> str:
        """Estimate resolution time based on complexity and urgency"""
        if complexity == "high":
            return "4-8 hours" if urgency in ["critical", "high"] else "1-2 days"
        elif complexity == "medium":
            return "2-4 hours" if urgency in ["critical", "high"] else "4-8 hours"
        else:
            return "30 minutes - 2 hours"
    
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main processing method for triage tasks"""
        try:
            ticket_data = task_data.get("ticket_data", {})
            
            self.logger.info(f"Triaging ticket: {ticket_data.get('ticketId')}")
            
            # Perform triage analysis
            analysis = await self.analyze_ticket(ticket_data)
            if "error" in analysis:
                return analysis
            
            categorization = await self.categorize_issue(ticket_data)
            if "error" in categorization:
                return categorization
            
            urgency_assessment = await self.assess_urgency(ticket_data)
            if "error" in urgency_assessment:
                return urgency_assessment
            
            # Combine all analysis results
            combined_analysis = {
                **analysis,
                **categorization,
                **urgency_assessment
            }
            
            routing = await self.determine_routing(combined_analysis)
            if "error" in routing:
                return routing
            
            # Final triage result
            triage_result = {
                "status": "complete",
                "ticket_id": ticket_data.get("ticketId"),
                "analysis": combined_analysis,
                "routing": routing,
                "triage_timestamp": task_data.get("timestamp"),
                "recommendations": self._generate_recommendations(combined_analysis, routing)
            }
            
            # Store triage result in memory
            await self.memory_manager.store_triage_result(
                ticket_id=ticket_data.get("ticketId"),
                result=triage_result
            )
            
            self.logger.info(f"Triage complete for ticket {ticket_data.get('ticketId')}: {routing['next_agent']}")
            
            return triage_result
            
        except Exception as e:
            self.logger.error(f"Error processing triage task: {e}")
            return {"error": str(e)}
    
    def _generate_recommendations(self, analysis: Dict[str, Any], routing: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on triage analysis"""
        recommendations = []
        
        if analysis.get("complexity") == "high":
            recommendations.append("Consider involving senior technician")
        
        if analysis.get("urgency") == "critical":
            recommendations.append("Prioritize immediate response")
        
        if routing.get("escalation_recommended"):
            recommendations.append("Prepare escalation path")
        
        if analysis.get("primary_category") == "security":
            recommendations.append("Follow security incident procedures")
        
        return recommendations
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current status of the triage agent"""
        return {
            "agent": "triage",
            "status": "ready",
            "capabilities": [
                "ticket_analysis",
                "issue_categorization", 
                "urgency_assessment",
                "routing_determination"
            ],
            "last_activity": None  # Could track last triage time
        }
