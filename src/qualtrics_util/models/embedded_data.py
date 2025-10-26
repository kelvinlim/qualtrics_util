"""
Embedded data management utilities.

This module provides functions for working with embedded data in Qualtrics contacts,
including flattening nested structures and parsing field values.
"""

from typing import Dict, Any, List
import json


def embedded_flat2nested(emb_data: Dict[str, Any], sep: str = '__') -> Dict[str, Any]:
    """
    Convert embedded data from flat format to nested format.
    
    Converts keys like 'label__start': 0 into nested dict: {'label': {'start': 0}}
    
    Args:
        emb_data: Dictionary with flat embedded data
        sep: Separator used in flat keys (default: '__')
        
    Returns:
        Dictionary with nested structure
        
    Example:
        >>> data = {'label__start': 0, 'label__end': 1}
        >>> embedded_flat2nested(data)
        {'label': {'start': 0, 'end': 1}}
    """
    new_dict = {}
    
    for key, value in emb_data.items():
        if sep in key:
            # Split into nested structure
            key_parts = key.split(sep)
            key1 = key_parts[0]
            key2 = sep.join(key_parts[1:])  # Handle multiple separators
            
            # Create or update nested dict
            if key1 in new_dict:
                if isinstance(new_dict[key1], dict):
                    new_dict[key1][key2] = value
                else:
                    raise ValueError(f"Error in nested embedded data: {key}")
            else:
                new_dict[key1] = {key2: value}
        else:
            # Non-nested key
            new_dict[key] = value
    
    return new_dict


def embedded_nested2flat(emb_data: Dict[str, Any], sep: str = '__') -> Dict[str, Any]:
    """
    Convert embedded data from nested format to flat format.
    
    Converts {'label': {'start': 0}} into 'label__start': 0
    
    Args:
        emb_data: Dictionary with nested structure
        sep: Separator to use in flat keys (default: '__')
        
    Returns:
        Dictionary with flat structure
        
    Example:
        >>> data = {'label': {'start': 0, 'end': 1}}
        >>> embedded_nested2flat(data)
        {'label__start': 0, 'label__end': 1}
    """
    new_dict = {}
    
    for key, value in emb_data.items():
        if isinstance(value, dict):
            # Flatten nested dict
            for nested_key, nested_value in value.items():
                flat_key = f"{key}{sep}{nested_key}"
                new_dict[flat_key] = nested_value
        else:
            # Non-nested value
            new_dict[key] = value
    
    return new_dict


def update_log_data(log_data_json: str, new_action: Dict[str, Any]) -> str:
    """
    Append a new action to log data.
    
    Args:
        log_data_json: Existing log data as JSON string
        new_action: New action to append
        
    Returns:
        Updated log data as JSON string
        
    Example:
        >>> update_log_data('[{"action":"init"}]', {"action":"send"})
        '[{"action": "init"}, {"action": "send"}]'
    """
    try:
        # Parse existing log data
        log_list = json.loads(log_data_json)
        
        # Ensure it's a list
        if not isinstance(log_list, list):
            log_list = [log_list]
        
        # Append new action
        log_list.append(new_action)
        
        # Convert back to JSON
        return json.dumps(log_list)
        
    except (json.JSONDecodeError, TypeError):
        # If parsing fails, create new log with the action
        return json.dumps([{"action": "init"}, new_action])


def get_embedded_field(contact: Dict[str, Any], field_name: str, default: Any = None) -> Any:
    """
    Safely get an embedded data field from a contact.
    
    Args:
        contact: Contact dictionary
        field_name: Name of the embedded field
        default: Default value if field not found
        
    Returns:
        Field value or default
    """
    embedded_data = contact.get('embeddedData', {})
    return embedded_data.get(field_name, default)


def get_contact_method(contact: Dict[str, Any]) -> str:
    """
    Get the contact method (SMS, EMAIL, or unknown) from a contact.
    
    Args:
        contact: Contact dictionary
        
    Returns:
        Contact method string ('SMS', 'EMAIL', or 'unknown')
    """
    embedded_data = contact.get('embeddedData', {})
    
    # Check ContactMethod first
    contact_method = embedded_data.get('ContactMethod', '').upper()
    if contact_method in ['SMS', 'EMAIL']:
        return contact_method
    
    # Fallback to UseSMS
    use_sms = embedded_data.get('UseSMS', 0)
    if int(use_sms) == 1:
        return 'SMS'
    
    return 'unknown'


def should_send_survey(contact: Dict[str, Any]) -> bool:
    """
    Determine if a survey should be sent to this contact.
    
    Checks:
    - SurveysScheduled == 0
    - NumDays > 0
    - Valid contact method (SMS or EMAIL)
    
    Args:
        contact: Contact dictionary
        
    Returns:
        True if survey should be sent, False otherwise
    """
    embedded_data = contact.get('embeddedData', {})
    
    # Check if surveys already scheduled
    surveys_scheduled = int(embedded_data.get('SurveysScheduled', 0))
    if surveys_scheduled != 0:
        return False
    
    # Check if NumDays is valid
    num_days = int(embedded_data.get('NumDays', 0))
    if num_days <= 0:
        return False
    
    # Check if contact method is valid
    contact_method = get_contact_method(contact)
    if contact_method == 'unknown':
        return False
    
    return True


def get_time_slots(contact: Dict[str, Any]) -> List[Any]:
    """
    Extract time slots from a contact's embedded data.
    
    Supports two formats:
    1. TimeSlots field: "800,1200,1600,2000"
    2. TimeX fields: Time1, Time2, etc.
    
    Args:
        contact: Contact dictionary
        
    Returns:
        List of time slots (integers or lists)
    """
    embedded_data = contact.get('embeddedData', {})
    
    # Try TimeSlots first
    time_slots_str = embedded_data.get('TimeSlots')
    if time_slots_str:
        try:
            import eval
            return eval(f"[{time_slots_str}]")
        except:
            pass
    
    # Fallback to TimeX format
    time_slots = []
    time_keys = []
    
    for key in embedded_data.keys():
        if key.startswith('Time') and 'TimeZone' not in key:
            time_keys.append(key)
    
    time_keys.sort()
    
    for key in time_keys:
        value = embedded_data[key]
        if isinstance(value, int):
            time_slots.append(value)
    
    return time_slots
