"""Prompt manager for handling AI prompt templates"""

from typing import Dict, Any, Optional
from pathlib import Path

class PromptManager:
    """Manages AI prompt templates for different scenarios"""
    
    def __init__(self):
        self.templates = {}
        self._load_templates()
    
    def _load_templates(self):
        """Load prompt templates"""
        from .templates.ticket_analysis import TICKET_ANALYSIS_PROMPT
        from .templates.suggestions import SUGGESTIONS_PROMPT
        from .templates.escalation import ESCALATION_PROMPT
        
        self.templates = {
            "ticket_analysis": TICKET_ANALYSIS_PROMPT,
            "suggestions": SUGGESTIONS_PROMPT,
            "escalation": ESCALATION_PROMPT
        }
    
    def get_prompt(self, template_name: str, **kwargs) -> str:
        """Get formatted prompt template"""
        template = self.templates.get(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        
        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required parameter: {e}")
    
    def add_template(self, name: str, template: str):
        """Add custom template"""
        self.templates[name] = template
    
    def list_templates(self) -> list:
        """List available templates"""
        return list(self.templates.keys())
