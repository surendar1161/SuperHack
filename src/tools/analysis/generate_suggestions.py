"""Generate suggestions tool for IT Technician Agent - Strands Compatible"""

from typing import Any, Dict, Optional, List
from strands import tool

from ...clients.superops_client import SuperOpsClient
from ...utils.logger import get_logger

logger = get_logger("generate_suggestions")

# Knowledge base of common solutions
solution_templates = {
    "hardware": {
        "printer": [
            "Check if printer is powered on and connected",
            "Verify printer drivers are installed and up to date",
            "Clear print queue and restart print spooler service",
            "Check for paper jams or low ink/toner",
            "Try printing a test page from printer settings"
        ],
        "computer": [
            "Restart the computer and check if issue persists",
            "Run Windows/Mac hardware diagnostics",
            "Check all cable connections",
            "Update device drivers",
            "Check for overheating issues"
        ],
        "monitor": [
            "Check monitor power and cable connections",
            "Try different video cable or port",
            "Adjust display settings and resolution",
            "Test monitor with different computer",
            "Check for loose connections"
        ]
    },
    "software": {
        "application": [
            "Close and restart the application",
            "Check for software updates",
            "Run application as administrator",
            "Clear application cache and temporary files",
            "Reinstall the application if necessary"
        ],
        "outlook": [
            "Restart Outlook and check connectivity",
            "Run Outlook in safe mode",
            "Repair Outlook data files (PST/OST)",
            "Check email account settings",
            "Clear Outlook cache and reset profile"
        ],
        "browser": [
            "Clear browser cache and cookies",
            "Disable browser extensions temporarily",
            "Try browsing in incognito/private mode",
            "Reset browser settings to default",
            "Update browser to latest version"
        ]
    },
    "network": {
        "connectivity": [
            "Check network cable connections",
            "Restart network adapter",
            "Run network troubleshooter",
            "Flush DNS cache (ipconfig /flushdns)",
            "Reset TCP/IP stack"
        ],
        "wifi": [
            "Restart WiFi adapter",
            "Forget and reconnect to WiFi network",
            "Check WiFi password and security settings",
            "Move closer to WiFi router",
            "Update WiFi driver"
        ],
        "vpn": [
            "Check VPN credentials and server settings",
            "Try different VPN server location",
            "Restart VPN client application",
            "Check firewall and antivirus settings",
            "Contact network administrator for VPN issues"
        ]
    },
    "email": {
        "sending": [
            "Check internet connectivity",
            "Verify email server settings (SMTP)",
            "Check email size and attachment limits",
            "Disable antivirus email scanning temporarily",
            "Try sending from webmail interface"
        ],
        "receiving": [
            "Check spam/junk folders",
            "Verify email server settings (POP3/IMAP)",
            "Check mailbox storage quota",
            "Test with different email client",
            "Contact email provider for server issues"
        ]
    },
    "security": {
        "password": [
            "Use password reset option if available",
            "Check caps lock and keyboard layout",
            "Try typing password in notepad first",
            "Contact administrator for password reset",
            "Check account lockout status"
        ],
        "access": [
            "Verify user permissions and group membership",
            "Check if account is active and not expired",
            "Try accessing from different location/device",
            "Clear cached credentials",
            "Contact administrator for access rights"
        ]
    }
}


def _identify_subcategory(description: str, category: str) -> str:
    """Identify subcategory based on description"""
    description_lower = description.lower()
    
    if category.lower() == "hardware":
        if any(word in description_lower for word in ["printer", "print", "printing"]):
            return "printer"
        elif any(word in description_lower for word in ["computer", "pc", "desktop", "laptop"]):
            return "computer"
        elif any(word in description_lower for word in ["monitor", "screen", "display"]):
            return "monitor"
    
    elif category.lower() == "software":
        if any(word in description_lower for word in ["outlook", "email client"]):
            return "outlook"
        elif any(word in description_lower for word in ["browser", "chrome", "firefox", "edge"]):
            return "browser"
        else:
            return "application"
    
    elif category.lower() == "network":
        if any(word in description_lower for word in ["wifi", "wireless"]):
            return "wifi"
        elif any(word in description_lower for word in ["vpn"]):
            return "vpn"
        else:
            return "connectivity"
    
    elif category.lower() == "email":
        if any(word in description_lower for word in ["send", "sending", "sent"]):
            return "sending"
        elif any(word in description_lower for word in ["receive", "receiving", "inbox"]):
            return "receiving"
    
    elif category.lower() == "security":
        if any(word in description_lower for word in ["password", "login", "sign in"]):
            return "password"
        else:
            return "access"
    
    return "general"


def _get_base_suggestions(category: str, subcategory: str) -> List[str]:
    """Get base suggestions from knowledge base"""
    category_lower = category.lower()
    
    if category_lower in solution_templates:
        if subcategory in solution_templates[category_lower]:
            return solution_templates[category_lower][subcategory].copy()
    
    # Fallback general suggestions
    return [
        "Restart the affected application or system",
        "Check for recent changes or updates",
        "Verify all connections and settings",
        "Try the operation from a different user account",
        "Contact IT support if issue persists"
    ]


def _customize_suggestions(suggestions: List[str], skill_level: str, priority: str) -> List[str]:
    """Customize suggestions based on user skill level and priority"""
    customized = suggestions.copy()
    
    if skill_level.lower() == "beginner":
        # Add more detailed explanations for beginners
        beginner_additions = [
            "If you're unsure about any step, please contact IT support",
            "Take note of any error messages you see",
            "Try restarting your computer if other steps don't work"
        ]
        customized.extend(beginner_additions)
    
    elif skill_level.lower() == "advanced":
        # Add more technical suggestions for advanced users
        advanced_additions = [
            "Check system logs for error details",
            "Use command line tools for deeper diagnostics",
            "Consider checking registry settings (Windows) or system preferences (Mac)"
        ]
        customized.extend(advanced_additions)
    
    if priority.upper() in ["HIGH", "URGENT", "CRITICAL"]:
        # Add escalation suggestions for high priority issues
        customized.insert(0, "Due to high priority, consider immediate escalation to senior technician")
    
    return customized


def _add_prevention_tips(category: str) -> List[str]:
    """Add prevention tips based on category"""
    prevention_tips = {
        "hardware": [
            "Keep hardware clean and dust-free",
            "Ensure proper ventilation for computers",
            "Use surge protectors for electrical equipment"
        ],
        "software": [
            "Keep software updated to latest versions",
            "Regularly clear cache and temporary files",
            "Avoid installing unknown or untrusted software"
        ],
        "network": [
            "Use strong WiFi passwords",
            "Keep network drivers updated",
            "Regularly restart network equipment"
        ],
        "email": [
            "Regularly clean up mailbox to avoid quota issues",
            "Be cautious with email attachments",
            "Keep email client updated"
        ],
        "security": [
            "Use strong, unique passwords",
            "Enable two-factor authentication where possible",
            "Regularly update passwords"
        ]
    }
    
    return prevention_tips.get(category.lower(), [])


@tool
async def generate_suggestions(
    problem_description: str = None,
    issue_description: str = None,  # Backward compatibility
    category: Optional[str] = None,
    priority: str = "MEDIUM",
    user_skill_level: str = "Beginner",
    previous_attempts: Optional[str] = None,
    system_info: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate troubleshooting suggestions and potential solutions for IT issues
    
    Args:
        problem_description: Detailed description of the IT problem or issue
        category: Category of the issue - Hardware, Software, Network, Email, Security, Account
        priority: Priority level - LOW, MEDIUM, HIGH, URGENT, CRITICAL
        user_skill_level: User's technical skill level - Beginner, Intermediate, Advanced
        previous_attempts: What troubleshooting steps have already been tried
        system_info: Information about the system (OS, software versions, hardware)
        
    Returns:
        Dictionary containing troubleshooting suggestions, prevention tips, and analysis
    """
    try:
        # Handle backward compatibility
        if issue_description and not problem_description:
            problem_description = issue_description
        elif not problem_description:
            problem_description = "General IT issue"
        
        logger.info(f"Generating suggestions for: {problem_description[:100]}...")
        
        # Default category if not provided
        if not category:
            category = "General"
        
        # Identify subcategory
        subcategory = _identify_subcategory(problem_description, category)
        
        # Get base suggestions
        base_suggestions = _get_base_suggestions(category, subcategory)
        
        # Customize suggestions
        customized_suggestions = _customize_suggestions(base_suggestions, user_skill_level, priority)
        
        # Filter out already attempted solutions
        if previous_attempts:
            previous_lower = previous_attempts.lower()
            filtered_suggestions = [
                s for s in customized_suggestions 
                if not any(word in previous_lower for word in s.lower().split()[:3])
            ]
            customized_suggestions = filtered_suggestions if filtered_suggestions else customized_suggestions
        
        # Add prevention tips
        prevention_tips = _add_prevention_tips(category)

        logger.info(f"Generated {len(customized_suggestions)} suggestions for {category}/{subcategory}")

        return {
            "success": True,
            "suggestions": customized_suggestions,
            "prevention_tips": prevention_tips,
            "category": category,
            "subcategory": subcategory,
            "priority": priority,
            "skill_level": user_skill_level,
            "message": f"Generated {len(customized_suggestions)} troubleshooting suggestions"
        }

    except Exception as e:
        logger.error(f"Failed to generate suggestions: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to generate suggestions"
        }


