"""Helper functions for the IT Technician Agent"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import hashlib
import random
import string

def generate_ticket_number(prefix: str = "IT") -> str:
    """Generate unique ticket number"""
    timestamp = datetime.now().strftime("%y%m%d")
    random_num = random.randint(1000, 9999)
    return f"{prefix}-{timestamp}-{random_num}"

def calculate_sla_deadline(priority: str, created_at: datetime) -> datetime:
    """Calculate SLA deadline based on priority"""
    from .constants import SLA_THRESHOLDS

    hours_to_add = SLA_THRESHOLDS.get(priority.lower(), 24)
    return created_at + timedelta(hours=hours_to_add)

def parse_date_range(date_range: str) -> Tuple[datetime, datetime]:
    """Parse date range string into start and end dates"""
    from .constants import DATE_RANGES

    now = datetime.now()
    days = DATE_RANGES.get(date_range, 30)

    end_date = now
    start_date = now - timedelta(days=days)

    return start_date, end_date

def generate_session_id() -> str:
    """Generate unique session ID"""
    return str(uuid.uuid4())

def hash_string(input_str: str) -> str:
    """Generate SHA256 hash of string"""
    return hashlib.sha256(input_str.encode()).hexdigest()

def generate_api_key(length: int = 32) -> str:
    """Generate random API key"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Split list into chunks of specified size"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def calculate_business_hours(start_time: datetime, end_time: datetime,
                           business_start: int = 9, business_end: int = 17,
                           weekend_days: List[int] = [5, 6]) -> float:
    """Calculate business hours between two timestamps"""
    total_hours = 0
    current = start_time.replace(hour=business_start, minute=0, second=0, microsecond=0)

    while current.date() <= end_time.date():
        # Skip weekends
        if current.weekday() in weekend_days:
            current += timedelta(days=1)
            continue

        day_start = current.replace(hour=business_start, minute=0, second=0, microsecond=0)
        day_end = current.replace(hour=business_end, minute=0, second=0, microsecond=0)

        # Calculate overlap with business hours for this day
        period_start = max(start_time, day_start)
        period_end = min(end_time, day_end)

        if period_start < period_end:
            total_hours += (period_end - period_start).total_seconds() / 3600

        current += timedelta(days=1)

    return total_hours

def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """Extract keywords from text"""
    import re

    # Remove special characters and convert to lowercase
    clean_text = re.sub(r'[^\w\s]', ' ', text.lower())
    words = clean_text.split()

    # Filter out short words and common stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}

    keywords = [word for word in words if len(word) >= min_length and word not in stop_words]

    # Remove duplicates while preserving order
    return list(dict.fromkeys(keywords))

def safe_get(dictionary: Dict, key: str, default=None, expected_type=None):
    """Safely get value from dictionary with type checking"""
    value = dictionary.get(key, default)

    if expected_type and value is not None and not isinstance(value, expected_type):
        try:
            value = expected_type(value)
        except (ValueError, TypeError):
            return default

    return value

def format_phone_number(phone: str) -> Optional[str]:
    """Format phone number to standard format"""
    import re

    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)

    # Check if valid US phone number
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"

    return None
