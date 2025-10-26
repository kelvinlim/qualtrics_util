"""
Date and time utility functions.

This module provides helpers for timezone conversion, time slot parsing,
and date/time formatting for survey scheduling.
"""

from datetime import datetime, timedelta
from typing import List, Union, Optional
from zoneinfo import ZoneInfo
import dateutil.parser
import random


def parse_time_slots(time_slots_str: str) -> List[Union[int, List[int]]]:
    """
    Parse time slots string into a list.
    
    Supports multiple formats:
    - "800,1200,1600,2000" -> [800, 1200, 1600, 2000]
    - "[800,900],[1200,1300]" -> [[800, 900], [1200, 1300]]
    
    Args:
        time_slots_str: String representation of time slots
        
    Returns:
        List of time slots (integers or lists of integers)
        
    Example:
        >>> parse_time_slots("800,1200")
        [800, 1200]
        
        >>> parse_time_slots("[800,900],[1200,1300]")
        [[800, 900], [1200, 1300]]
    """
    try:
        # Use eval to parse the string safely (assuming input is trusted)
        return eval(f"[{time_slots_str}]")
    except Exception as e:
        raise ValueError(f"Invalid time slots format: {time_slots_str}") from e


def get_time_from_slot(slot: Union[int, List[int]]) -> int:
    """
    Convert a time slot to a specific time.
    
    For single integers (e.g., 800), returns the time as-is.
    For lists (e.g., [800, 900]), returns a random time within the range.
    
    Args:
        slot: Time slot as integer or list of two integers
        
    Returns:
        Time as an integer (e.g., 815 for 8:15 AM)
        
    Example:
        >>> get_time_from_slot(800)
        800
        
        >>> get_time_from_slot([800, 900])  # Random time between 8:00 and 9:00
        845  # Example output
    """
    if isinstance(slot, int):
        return slot
    
    # Handle range [start, end]
    if isinstance(slot, list) and len(slot) == 2:
        time0_hours = slot[0] // 100 + (slot[0] - (slot[0] // 100 * 100)) / 60.0
        time1_hours = slot[1] // 100 + (slot[1] - (slot[1] // 100 * 100)) / 60.0
        
        time_raw = random.uniform(time0_hours, time1_hours)
        hours = int(time_raw // 1)
        minutes_percentage = time_raw - hours
        minutes = minutes_percentage * 60
        
        return int(hours * 100 + minutes)
    
    raise ValueError(f"Invalid slot format: {slot}")


def convert_to_utc(
    date_str: str,
    hour: int,
    minute: int,
    timezone: str,
    days_offset: int = 0
) -> datetime:
    """
    Convert a date and time to UTC.
    
    Args:
        date_str: Date string in format 'YYYY-MM-DD'
        hour: Hour (0-23)
        minute: Minute (0-59)
        timezone: Timezone string (e.g., 'America/Chicago')
        days_offset: Number of days to add to the date (default: 0)
        
    Returns:
        Datetime object in UTC
        
    Example:
        >>> convert_to_utc('2024-01-15', 14, 30, 'America/Chicago')
        datetime.datetime(2024, 1, 15, 20, 30, tzinfo=ZoneInfo('UTC'))
    """
    # Parse the date
    date_obj = dateutil.parser.parse(date_str)
    
    # Create datetime in specified timezone
    local_time = datetime(
        date_obj.year,
        date_obj.month,
        date_obj.day,
        hour,
        minute,
        0,
        tzinfo=ZoneInfo(timezone)
    )
    
    # Add day offset
    if days_offset:
        local_time = local_time + timedelta(days=days_offset)
    
    # Convert to UTC
    return local_time.astimezone(ZoneInfo("UTC"))


def calculate_expiration_time(
    send_time: datetime,
    expiration_minutes: int
) -> datetime:
    """
    Calculate expiration time from send time.
    
    Args:
        send_time: When to send the survey (datetime in UTC)
        expiration_minutes: Minutes until expiration
        
    Returns:
        Expiration datetime in UTC
        
    Example:
        >>> send_time = datetime(2024, 1, 15, 12, 0, 0, tzinfo=ZoneInfo('UTC'))
        >>> calculate_expiration_time(send_time, 60)
        datetime.datetime(2024, 1, 15, 13, 0, tzinfo=ZoneInfo('UTC'))
    """
    return send_time + timedelta(minutes=expiration_minutes)


def should_schedule_future_only(send_time: datetime) -> bool:
    """
    Check if the send time is in the future.
    
    Args:
        send_time: Time to send the survey
        
    Returns:
        True if send time is in the future, False otherwise
    """
    now = datetime.now(tz=ZoneInfo("UTC"))
    return send_time > now


def validate_time_slots(time_slots: List[Union[int, List[int]]]) -> bool:
    """
    Validate time slot format.
    
    Args:
        time_slots: List of time slots
        
    Returns:
        True if valid, False otherwise
        
    Example:
        >>> validate_time_slots([800, 1200, 1600])
        True
        
        >>> validate_time_slots([[800, 900], [1200, 1300]])
        True
    """
    if not time_slots:
        return False
    
    for slot in time_slots:
        if isinstance(slot, int):
            # Simple integer time slot
            if not (0 <= slot <= 2359):
                return False
        elif isinstance(slot, list):
            # Range time slot [start, end]
            if len(slot) != 2:
                return False
            if not all(isinstance(t, int) and 0 <= t <= 2359 for t in slot):
                return False
            if slot[0] >= slot[1]:
                return False
        else:
            return False
    
    return True


def format_datetime_iso(dt: datetime) -> str:
    """
    Format datetime in ISO 8601 format for Qualtrics API.
    
    Args:
        dt: Datetime object
        
    Returns:
        ISO 8601 formatted string (e.g., '2024-01-15T12:00:00Z')
    """
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
