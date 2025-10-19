"""Analyze request tool for IT Technician Agent - Strands Compatible"""

from typing import Any, Dict, Optional, List
import re
from strands import tool

from ...clients.superops_client import SuperOpsClient
from ...utils.logger import get_logger

logger = get_logger("AnalyzeRequestTool")
# Keywords for different categories and priorities
priority_keywords = {
    "critical": ["critical", "emergency", "urgent", "down", "outage", "system failure", "cannot work", "production"],
    "high": ["urgent", "asap", "important", "blocking", "cannot access", "not working", "broken"],
    "medium": ["issue", "problem", "help", "support", "request", "need"],
    "low": ["question", "how to", "enhancement", "suggestion", "when convenient"]
}

category_keywords = {
    "hardware": ["printer", "computer", "laptop", "monitor", "keyboard", "mouse", "device", "hardware"],
    "software": ["application", "program", "software", "app", "excel", "word", "outlook", "browser"],
    "network": ["internet", "wifi", "network", "connection", "vpn", "slow", "connectivity"],
    "email": ["email", "outlook", "mail", "inbox", "sending", "receiving", "attachment"],
    "security": ["password", "login", "access", "account", "security", "locked", "reset", "permissions"],
    "account": ["user", "account", "profile", "permissions", "access rights", "new user"]
}

def _extract_priority(text: str) -> str:
    """Extract priority level from request text"""
    text_lower = text.lower()
    
    # Check for critical keywords first
    for keyword in priority_keywords["critical"]:
        if keyword in text_lower:
            return "CRITICAL"
    
    # Check for high priority keywords
    for keyword in priority_keywords["high"]:
        if keyword in text_lower:
            return "HIGH"
    
    # Check for low priority keywords
    for keyword in priority_keywords["low"]:
        if keyword in text_lower:
            return "LOW"
    
    # Default to medium
    return "MEDIUM"

def _extract_category(text: str) -> str:
    """Extract category from request text"""
    text_lower = text.lower()
    category_scores = {}
    
    for category, keywords in category_keywords.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        if score > 0:
            category_scores[category] = score
    
    if category_scores:
        return max(category_scores, key=category_scores.get).title()
    
    return "General"

def _extract_urgency_indicators(text: str) -> List[str]:
    """Extract urgency indicators from text"""
    urgency_patterns = [
        r"can'?t work",
        r"not working",
        r"broken",
        r"urgent",
        r"asap",
        r"emergency",
        r"critical",
        r"down",
        r"outage"
    ]
    
    indicators = []
    text_lower = text.lower()
    
    for pattern in urgency_patterns:
        if re.search(pattern, text_lower):
            indicators.append(pattern.replace(r"\b", "").replace("'?", "'"))
    
    return indicators

def _extract_technical_details(text: str) -> Dict[str, Any]:
    """Extract technical details from the request"""
    details = {
        "error_messages": [],
        "affected_systems": [],
        "user_actions": [],
        "symptoms": []
    }
    
    # Extract error messages (text in quotes or after "error:")
    error_patterns = [
        r'"([^"]+)"',
        r"'([^']+)'",
        r"error:?\s*(.+?)(?:\.|$)",
        r"message:?\s*(.+?)(?:\.|$)"
    ]
    
    for pattern in error_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        details["error_messages"].extend(matches)
    
    # Extract system/application names
    system_patterns = [
        r"\b(outlook|excel|word|powerpoint|teams|sharepoint|windows|mac|linux)\b",
        r"\b(printer|scanner|computer|laptop|server)\b",
        r"\b(wifi|internet|vpn|network)\b"
    ]
    
    for pattern in system_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        details["affected_systems"].extend(matches)
    
    return details

def _suggest_actions(analysis: Dict) -> List[str]:
    """Suggest actions based on analysis"""
    actions = []
    
    priority = analysis.get("priority", "MEDIUM")
    category = analysis.get("category", "General").lower()
    
    if priority in ["CRITICAL", "HIGH"]:
        actions.append("Escalate to senior technician")
        actions.append("Provide immediate response")
    
    if category == "hardware":
        actions.append("Check hardware diagnostics")
        actions.append("Verify physical connections")
    elif category == "software":
        actions.append("Check software version and updates")
        actions.append("Review application logs")
    elif category == "network":
        actions.append("Test network connectivity")
        actions.append("Check network configuration")
    elif category == "email":
        actions.append("Verify email server status")
        actions.append("Check email client configuration")
    elif category == "security":
        actions.append("Verify user credentials")
        actions.append("Check account permissions")
    
    if analysis.get("urgency_indicators"):
        actions.append("Schedule immediate intervention")
    
    return actions

def _calculate_confidence(analysis: Dict) -> float:
    """Calculate confidence score for the analysis"""
    score = 0.5  # Base score
    
    if analysis.get("urgency_indicators"):
        score += 0.2
    
    if analysis.get("technical_details", {}).get("error_messages"):
        score += 0.2
    
    if analysis.get("technical_details", {}).get("affected_systems"):
        score += 0.1
    
    return min(score, 1.0)

@tool
async def analyze_request(
    request_text: str,
    priority: Optional[str] = None,  # Backward compatibility
    requester_info: Optional[str] = None,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyze an IT support request to extract key information like priority, category, urgency indicators, and required actions
    
    Args:
        request_text: The full text of the IT support request to analyze
        requester_info: Information about the person making the request (name, email, department) - optional
        context: Additional context about the request or previous interactions - optional
        
    Returns:
        Dictionary containing analysis results with priority, category, urgency indicators, and suggested actions
    """
    try:
        logger.info(f"Analyzing request: {request_text[:100]}...")
        
        # Perform analysis
        priority = _extract_priority(request_text)
        category = _extract_category(request_text)
        urgency_indicators = _extract_urgency_indicators(request_text)
        technical_details = _extract_technical_details(request_text)
        
        analysis = {
            "priority": priority,
            "category": category,
            "urgency_indicators": urgency_indicators,
            "technical_details": technical_details,
            "requires_escalation": priority in ["CRITICAL", "HIGH"],
            "estimated_complexity": "High" if len(technical_details["error_messages"]) > 0 else "Medium"
        }
        
        suggested_actions = _suggest_actions(analysis)

        logger.info(f"Analyzed request - Priority: {priority}, Category: {category}")

        return {
            "success": True,
            "analysis": analysis,
            "suggested_actions": suggested_actions,
            "confidence_score": _calculate_confidence(analysis),
            "message": f"Request analyzed - Priority: {priority}, Category: {category}"
        }

    except Exception as e:
        logger.error(f"Failed to analyze request: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to analyze request"
        }