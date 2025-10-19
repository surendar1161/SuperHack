"""Escalation prompt template"""

ESCALATION_PROMPT = """
You are an expert IT Technician determining if a ticket requires escalation. Analyze the situation and provide escalation recommendations.

**Ticket Information:**
ID: {ticket_id}
Title: {title}
Current Status: {status}
Priority: {priority}
Time Since Creation: {time_elapsed}
Assigned Technician: {assigned_to}
Escalation History: {escalation_history}

**Issue Analysis:**
Problem Complexity: {complexity}
Impact Scope: {impact_scope}
Business Critical: {business_critical}
Resolution Attempts: {resolution_attempts}

**SLA Status:**
SLA Deadline: {sla_deadline}
Time Remaining: {time_remaining}
Breach Risk: {breach_risk}

**Escalation Criteria to Evaluate:**
1. Technical complexity beyond current skill level
2. SLA breach imminent or occurred
3. Business critical system affected
4. Multiple failed resolution attempts
5. Customer VIP status or high visibility
6. Security implications
7. Resource constraints

**Please determine:**
1. Should this ticket be escalated? (Yes/No with reasoning)
2. Escalation level (L2, L3, Management, Vendor)
3. Urgency of escalation (Immediate, Within 2 hours, Next business day)
4. Required handover information
5. Recommended next steps
6. Communication plan for stakeholders

Provide clear justification for your escalation decision.
"""
