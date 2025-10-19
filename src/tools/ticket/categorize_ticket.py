"""
Ticket Categorization Tool

Strands-compatible tool for analyzing and categorizing support requests
with urgency assessment, SLA determination, and assignment logic.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from strands import tool

from ...utils.logger import get_logger
from ...clients.superops_client import SuperOpsClient
from ...models.ticket import Priority, TicketStatus


logger = get_logger("TicketCategorizationTool")


@tool
async def categorize_support_request(
    ticket_data: Dict[str, Any],
    customer_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Analyze and categorize a support request with AI-powered classification
    
    Args:
        ticket_data: Ticket information including subject, description, etc.
        customer_data: Optional customer information for context
        
    Returns:
        Dictionary containing categorization results, urgency, SLA requirements
    """
    try:
        logger.info(f"Categorizing ticket {ticket_data.get('id', 'unknown')}")
        
        # Extract key information
        subject = ticket_data.get('subject', '').lower()
        description = ticket_data.get('description', '').lower()
        current_priority = ticket_data.get('priority', 'medium').lower()
        
        # Analyze content for keywords and patterns
        category_analysis = await _analyze_ticket_content(subject, description)
        urgency_analysis = await _assess_urgency(ticket_data, customer_data)
        sla_requirements = await _determine_sla_requirements(category_analysis, urgency_analysis, customer_data)
        
        # Determine final categorization
        final_category = category_analysis['primary_category']
        final_priority = _calculate_final_priority(current_priority, urgency_analysis, customer_data)
        
        return {
            "success": True,
            "ticket_id": ticket_data.get('id'),
            "categorization": {
                "primary_category": final_category,
                "subcategory": category_analysis.get('subcategory'),
                "keywords": category_analysis.get('keywords', []),
                "confidence": category_analysis.get('confidence', 0.0)
            },
            "urgency_assessment": {
                "urgency_level": urgency_analysis['urgency_level'],
                "urgency_score": urgency_analysis['urgency_score'],
                "urgency_factors": urgency_analysis['factors']
            },
            "priority_recommendation": {
                "original_priority": current_priority,
                "recommended_priority": final_priority,
                "priority_changed": final_priority != current_priority,
                "reasoning": urgency_analysis.get('reasoning', [])
            },
            "sla_requirements": sla_requirements,
            "assignment_hints": {
                "required_skills": category_analysis.get('required_skills', []),
                "complexity_level": category_analysis.get('complexity', 'medium'),
                "estimated_effort_hours": category_analysis.get('estimated_hours', 2)
            }
        }
        
    except Exception as e:
        logger.error(f"Error categorizing ticket: {e}")
        return {
            "success": False,
            "error": str(e),
            "ticket_id": ticket_data.get('id', 'unknown')
        }


async def _analyze_ticket_content(subject: str, description: str) -> Dict[str, Any]:
    """Analyze ticket content to determine category and requirements"""
    
    # Category keywords mapping
    category_keywords = {
        'hardware': ['server', 'computer', 'laptop', 'printer', 'hardware', 'device', 'equipment'],
        'software': ['application', 'software', 'program', 'app', 'install', 'update', 'bug'],
        'network': ['network', 'internet', 'wifi', 'connection', 'vpn', 'firewall', 'router'],
        'security': ['security', 'virus', 'malware', 'password', 'access', 'breach', 'hack'],
        'email': ['email', 'outlook', 'mail', 'exchange', 'smtp', 'imap'],
        'database': ['database', 'sql', 'mysql', 'postgres', 'oracle', 'db'],
        'infrastructure': ['infrastructure', 'cloud', 'aws', 'azure', 'deployment', 'server'],
        'user_access': ['access', 'permission', 'user', 'account', 'login', 'authentication']
    }
    
    # Urgency keywords
    urgency_keywords = {
        'critical': ['down', 'outage', 'critical', 'emergency', 'urgent', 'broken', 'failed'],
        'high': ['slow', 'performance', 'issue', 'problem', 'error', 'not working'],
        'medium': ['question', 'help', 'how to', 'request', 'need'],
        'low': ['enhancement', 'feature', 'improvement', 'suggestion']
    }
    
    # Skill requirements mapping
    skill_requirements = {
        'hardware': ['hardware_support', 'troubleshooting'],
        'software': ['software_support', 'application_management'],
        'network': ['network_administration', 'troubleshooting'],
        'security': ['security_specialist', 'incident_response'],
        'email': ['email_administration', 'exchange_management'],
        'database': ['database_administration', 'sql'],
        'infrastructure': ['cloud_administration', 'devops'],
        'user_access': ['identity_management', 'active_directory']
    }
    
    content = f"{subject} {description}"
    
    # Score each category
    category_scores = {}
    for category, keywords in category_keywords.items():
        score = sum(1 for keyword in keywords if keyword in content)
        if score > 0:
            category_scores[category] = score
    
    # Determine primary category
    if category_scores:
        primary_category = max(category_scores, key=category_scores.get)
        confidence = category_scores[primary_category] / len(category_keywords[primary_category])
    else:
        primary_category = 'general'
        confidence = 0.5
    
    # Estimate complexity and effort
    complexity_indicators = ['integration', 'custom', 'complex', 'multiple', 'advanced']
    complexity_score = sum(1 for indicator in complexity_indicators if indicator in content)
    
    if complexity_score >= 3:
        complexity = 'high'
        estimated_hours = 8
    elif complexity_score >= 1:
        complexity = 'medium'
        estimated_hours = 4
    else:
        complexity = 'low'
        estimated_hours = 2
    
    return {
        'primary_category': primary_category,
        'subcategory': _determine_subcategory(primary_category, content),
        'keywords': [kw for kw in category_keywords.get(primary_category, []) if kw in content],
        'confidence': min(confidence, 1.0),
        'required_skills': skill_requirements.get(primary_category, ['general_support']),
        'complexity': complexity,
        'estimated_hours': estimated_hours,
        'category_scores': category_scores
    }


async def _assess_urgency(ticket_data: Dict[str, Any], customer_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Assess ticket urgency based on multiple factors"""
    
    subject = ticket_data.get('subject', '').lower()
    description = ticket_data.get('description', '').lower()
    content = f"{subject} {description}"
    
    urgency_score = 0
    factors = []
    reasoning = []
    
    # Content-based urgency indicators
    critical_keywords = ['down', 'outage', 'critical', 'emergency', 'production', 'all users']
    high_keywords = ['slow', 'performance', 'error', 'not working', 'urgent']
    
    critical_matches = sum(1 for kw in critical_keywords if kw in content)
    high_matches = sum(1 for kw in high_keywords if kw in content)
    
    if critical_matches > 0:
        urgency_score += 40
        factors.append('critical_keywords')
        reasoning.append(f"Contains critical keywords: {[kw for kw in critical_keywords if kw in content]}")
    
    if high_matches > 0:
        urgency_score += 20
        factors.append('high_priority_keywords')
        reasoning.append(f"Contains high priority keywords: {[kw for kw in high_keywords if kw in content]}")
    
    # Customer tier impact
    if customer_data:
        customer_tier = customer_data.get('tier', 'standard').lower()
        if customer_tier in ['premium', 'enterprise']:
            urgency_score += 15
            factors.append('premium_customer')
            reasoning.append(f"Premium customer tier: {customer_tier}")
        elif customer_tier == 'business':
            urgency_score += 10
            factors.append('business_customer')
            reasoning.append(f"Business customer tier: {customer_tier}")
    
    # Time-based factors
    current_hour = datetime.now().hour
    if current_hour < 9 or current_hour > 17:  # Outside business hours
        urgency_score += 5
        factors.append('outside_business_hours')
        reasoning.append("Reported outside business hours")
    
    # Determine urgency level
    if urgency_score >= 50:
        urgency_level = 'critical'
    elif urgency_score >= 30:
        urgency_level = 'high'
    elif urgency_score >= 15:
        urgency_level = 'medium'
    else:
        urgency_level = 'low'
    
    return {
        'urgency_level': urgency_level,
        'urgency_score': urgency_score,
        'factors': factors,
        'reasoning': reasoning
    }


async def _determine_sla_requirements(
    category_analysis: Dict[str, Any], 
    urgency_analysis: Dict[str, Any],
    customer_data: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """Determine SLA requirements based on categorization and urgency"""
    
    # Base SLA times by urgency
    base_sla_times = {
        'critical': {'response_minutes': 15, 'resolution_hours': 4},
        'high': {'response_minutes': 60, 'resolution_hours': 8},
        'medium': {'response_minutes': 240, 'resolution_hours': 24},
        'low': {'response_minutes': 480, 'resolution_hours': 72}
    }
    
    urgency_level = urgency_analysis['urgency_level']
    sla_times = base_sla_times[urgency_level].copy()
    
    # Adjust for customer tier
    if customer_data:
        customer_tier = customer_data.get('tier', 'standard').lower()
        if customer_tier in ['premium', 'enterprise']:
            # Reduce SLA times by 25% for premium customers
            sla_times['response_minutes'] = int(sla_times['response_minutes'] * 0.75)
            sla_times['resolution_hours'] = int(sla_times['resolution_hours'] * 0.75)
    
    # Adjust for complexity
    complexity = category_analysis.get('complexity', 'medium')
    if complexity == 'high':
        # Increase resolution time for complex issues
        sla_times['resolution_hours'] = int(sla_times['resolution_hours'] * 1.5)
    
    return {
        'response_time_minutes': sla_times['response_minutes'],
        'resolution_time_hours': sla_times['resolution_hours'],
        'business_hours_only': urgency_level in ['medium', 'low'],
        'escalation_required': urgency_level in ['critical', 'high'],
        'sla_policy_id': f"sla_{urgency_level}_{customer_data.get('tier', 'standard') if customer_data else 'standard'}"
    }


def _calculate_final_priority(
    current_priority: str, 
    urgency_analysis: Dict[str, Any], 
    customer_data: Optional[Dict[str, Any]]
) -> str:
    """Calculate final priority based on analysis"""
    
    urgency_level = urgency_analysis['urgency_level']
    
    # Priority mapping based on urgency
    urgency_to_priority = {
        'critical': 'critical',
        'high': 'high',
        'medium': 'medium',
        'low': 'low'
    }
    
    recommended_priority = urgency_to_priority[urgency_level]
    
    # Don't downgrade existing high priorities
    priority_levels = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
    current_level = priority_levels.get(current_priority, 2)
    recommended_level = priority_levels.get(recommended_priority, 2)
    
    if current_level > recommended_level:
        return current_priority
    
    return recommended_priority


def _determine_subcategory(primary_category: str, content: str) -> Optional[str]:
    """Determine subcategory based on primary category and content"""
    
    subcategory_mapping = {
        'hardware': {
            'server': ['server', 'rack', 'datacenter'],
            'desktop': ['computer', 'desktop', 'workstation'],
            'laptop': ['laptop', 'notebook', 'mobile'],
            'printer': ['printer', 'print', 'scanning'],
            'peripheral': ['mouse', 'keyboard', 'monitor', 'display']
        },
        'software': {
            'application': ['application', 'app', 'program'],
            'operating_system': ['windows', 'linux', 'macos', 'os'],
            'browser': ['browser', 'chrome', 'firefox', 'edge'],
            'office': ['office', 'word', 'excel', 'powerpoint']
        },
        'network': {
            'connectivity': ['connection', 'internet', 'wifi'],
            'vpn': ['vpn', 'remote', 'tunnel'],
            'firewall': ['firewall', 'security', 'blocked'],
            'dns': ['dns', 'domain', 'resolution']
        }
    }
    
    if primary_category in subcategory_mapping:
        for subcategory, keywords in subcategory_mapping[primary_category].items():
            if any(keyword in content for keyword in keywords):
                return subcategory
    
    return None


@tool
async def determine_assignment_logic(
    categorization_result: Dict[str, Any],
    available_technicians: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Determine the best technician assignment based on categorization results
    
    Args:
        categorization_result: Result from categorize_support_request
        available_technicians: List of available technicians with skills
        
    Returns:
        Dictionary containing assignment recommendations
    """
    try:
        if not available_technicians:
            # Get available technicians from SuperOps API
            available_technicians = await _get_available_technicians()
        
        required_skills = categorization_result.get('assignment_hints', {}).get('required_skills', [])
        complexity_level = categorization_result.get('assignment_hints', {}).get('complexity_level', 'medium')
        urgency_level = categorization_result.get('urgency_assessment', {}).get('urgency_level', 'medium')
        
        # Score technicians based on skills and availability
        technician_scores = []
        
        for tech in available_technicians:
            score = _calculate_technician_score(tech, required_skills, complexity_level, urgency_level)
            if score > 0:
                technician_scores.append({
                    'technician': tech,
                    'score': score,
                    'match_reasons': score.get('reasons', [])
                })
        
        # Sort by score
        technician_scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Get top 3 recommendations
        recommendations = technician_scores[:3] if technician_scores else []
        
        return {
            "success": True,
            "assignment_recommendations": [
                {
                    "technician_id": rec['technician']['id'],
                    "technician_name": rec['technician']['name'],
                    "score": rec['score'],
                    "match_reasons": rec.get('match_reasons', []),
                    "current_workload": rec['technician'].get('currentTicketCount', 0),
                    "availability": rec['technician'].get('availability', 'available')
                }
                for rec in recommendations
            ],
            "assignment_criteria": {
                "required_skills": required_skills,
                "complexity_level": complexity_level,
                "urgency_level": urgency_level
            },
            "total_candidates": len(available_technicians),
            "qualified_candidates": len(recommendations)
        }
        
    except Exception as e:
        logger.error(f"Error determining assignment logic: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def _get_available_technicians() -> List[Dict[str, Any]]:
    """Get available technicians from SuperOps API"""
    # This would integrate with SuperOps API
    # For now, return mock data
    return [
        {
            "id": "tech-001",
            "name": "John Doe",
            "email": "john.doe@company.com",
            "skills": ["hardware_support", "network_administration"],
            "experience_level": "senior",
            "currentTicketCount": 3,
            "maxConcurrentTickets": 8,
            "availability": "available"
        },
        {
            "id": "tech-002", 
            "name": "Jane Smith",
            "email": "jane.smith@company.com",
            "skills": ["software_support", "database_administration"],
            "experience_level": "intermediate",
            "currentTicketCount": 5,
            "maxConcurrentTickets": 6,
            "availability": "busy"
        }
    ]


def _calculate_technician_score(
    technician: Dict[str, Any], 
    required_skills: List[str], 
    complexity_level: str,
    urgency_level: str
) -> float:
    """Calculate technician suitability score"""
    
    score = 0.0
    reasons = []
    
    # Skill matching (40% of score)
    tech_skills = technician.get('skills', [])
    skill_matches = len(set(required_skills) & set(tech_skills))
    if skill_matches > 0:
        skill_score = (skill_matches / len(required_skills)) * 40
        score += skill_score
        reasons.append(f"Matches {skill_matches}/{len(required_skills)} required skills")
    
    # Experience level matching (25% of score)
    experience_level = technician.get('experience_level', 'intermediate')
    experience_scores = {
        'junior': {'low': 25, 'medium': 15, 'high': 5},
        'intermediate': {'low': 20, 'medium': 25, 'high': 15},
        'senior': {'low': 15, 'medium': 20, 'high': 25}
    }
    
    if experience_level in experience_scores and complexity_level in experience_scores[experience_level]:
        exp_score = experience_scores[experience_level][complexity_level]
        score += exp_score
        reasons.append(f"{experience_level} level matches {complexity_level} complexity")
    
    # Availability (20% of score)
    current_tickets = technician.get('currentTicketCount', 0)
    max_tickets = technician.get('maxConcurrentTickets', 10)
    availability_ratio = 1 - (current_tickets / max_tickets)
    availability_score = availability_ratio * 20
    score += availability_score
    reasons.append(f"Availability: {current_tickets}/{max_tickets} tickets")
    
    # Urgency handling (15% of score)
    if urgency_level in ['critical', 'high'] and technician.get('availability') == 'available':
        score += 15
        reasons.append("Available for urgent tickets")
    elif urgency_level in ['medium', 'low']:
        score += 10
        reasons.append("Suitable for standard priority")
    
    return {
        'score': score,
        'reasons': reasons
    }