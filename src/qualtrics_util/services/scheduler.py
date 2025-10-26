"""
Scheduler service for distributing surveys via SMS or Email.

This module handles scheduling of survey distributions with time slots
and timezone management.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from zoneinfo import ZoneInfo
import dateutil.parser


def check_time_slots(parts: list) -> bool:
    """
    Validate time slot format.
    
    Args:
        parts (list): time slots examples [800,1200,1600,2000] or [[800, 900]]
    
    Returns:
        bool: True if all time slots are valid, False otherwise
    """
    count = len(parts)
    result = False  # init to False
    
    # check each part
    for part in parts:
        
        if type(part) is list:
            try:
                if len(part) == 2:
                    for number in part:
                        try:
                            if type(number) is not int:
                                raise Exception("Not an int")
                        except Exception as e:
                            return False
                        else:
                            result = True
                else:
                    return False
            except Exception as e:
                return False

            result = True
        else:
            # check is it a number
            try:
                if type(part) is not int:
                    raise Exception("Not an int")
                pass
            except Exception as e:
                return False
            else:
                result = True
        
    # everything OK!     
    return result


def get_time(slot) -> int:
    """
    Check the entry and return a time as a number.
    For the [800:900] entry, returns a time between the two
    numbers, e.g. 815

    Args:
        slot : time slot 800 or [800:900]

    Returns:
        int: time as a number in 24 hour notation
    """
    import random
    
    try:
        time = int(slot)
    except:
        # is a list [2050,2110]
        #  TODO  how to deal with [2350,0010]!!
        # convert hourm inute to hours.float
        time0 = slot[0]//100 + (slot[0] - slot[0]//100*100)/60.0
        time1 = slot[1]//100 + (slot[1] - slot[1]//100*100)/60.0
        
        time_raw = random.uniform(time0, time1)
        # convert time_raw such that 830 is 8 for hours and 30/60 for minutes
        # is 8.5
        hours = time_raw//1 
        minutes_percentage = (time_raw - hours)
        minutes = minutes_percentage * 60
        # convert back to hhmm
        time = int(hours*100 + minutes)
        
    return time


def calculate_send_times(params: Dict[str, Any]) -> List[Tuple[datetime, datetime]]:
    """
    Calculate send and expiration times for all scheduled surveys.
    
    Args:
        params: Dictionary containing:
            - startDate: Start date string (YYYY-MM-DD)
            - timeSlots: List of time slots (e.g., [800, 1200, 1600, 2000])
            - numDays: Number of days to send surveys
            - timeZone: IANA timezone name (e.g., 'America/Chicago')
            - ExpireMinutes: Minutes until survey expires (default: 60)
    
    Returns:
        List of tuples containing (send_time_utc, expiration_time_utc)
    """
    # Check time slots format
    if not check_time_slots(params['timeSlots']):
        raise ValueError(f"Error in format of timeSlots {params['timeSlots']}")
    
    total_count = params['numDays'] * len(params['timeSlots'])
    send_times = []
    
    for day in range(params['numDays']):
        for raw_time in params['timeSlots']:
            
            time = get_time(raw_time)
            
            # Parse start date
            dobj = dateutil.parser.parse(params['startDate'])
            hour = int(time) // 100
            min = int(time) % 100
            
            # Create datetime in recipient's timezone
            start_recipient_time = datetime(
                dobj.year, dobj.month, dobj.day, hour, min, 0,
                tzinfo=ZoneInfo(params['timeZone'])
            )
            
            # Add the day delta
            recipient_time = start_recipient_time + timedelta(days=day)
            
            # Convert to UTC
            recipient_time_utc = recipient_time.astimezone(ZoneInfo("UTC"))
            
            # Calculate expiration time
            expire_minutes = params.get('ExpireMinutes', 60)
            expiration_time_utc = recipient_time_utc + timedelta(minutes=expire_minutes)
            
            send_times.append((recipient_time_utc, expiration_time_utc))
    
    return send_times


def format_qualtrics_datetime(dt: datetime) -> str:
    """
    Format datetime for Qualtrics API.
    
    Args:
        dt: datetime object (preferably in UTC)
    
    Returns:
        str: Formatted datetime string for Qualtrics API
    """
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


def should_schedule_future_only(send_time: datetime) -> bool:
    """
    Check if send time is in the future.
    
    Args:
        send_time: UTC datetime to check
    
    Returns:
        bool: True if send time is in the future, False otherwise
    """
    from datetime import datetime
    from zoneinfo import ZoneInfo
    
    now = datetime.now(ZoneInfo("UTC"))
    return send_time > now
