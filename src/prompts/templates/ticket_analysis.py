"""Ticket analysis prompt template"""

TICKET_ANALYSIS_PROMPT = """
You are an expert IT Technician analyzing a support ticket. Please analyze the following ticket information and provide a comprehensive assessment.

**Ticket Information:**
Title: {title}
Description: {description}
Priority: {priority}
Category: {category}
Requester: {requester_email}

**Analysis Required:**
1. Identify the primary issue or problem
2. Determine urgency and impact levels
3. Suggest initial troubleshooting steps
4. Recommend appropriate technician skills needed
5. Estimate resolution time
6. Identify any potential escalation needs

**Context:**
- Current workload: {current_workload}
- Available technicians: {available_technicians}
- Similar recent tickets: {similar_tickets}

Please provide your analysis in a structured format with clear recommendations for next steps.
"""
