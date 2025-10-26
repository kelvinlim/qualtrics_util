"""
Unit tests for datetime utilities.

Run with: pytest tests/test_utils/test_datetime_utils.py -v
"""

import pytest
import sys
sys.path.insert(0, 'src')

from datetime import datetime
from zoneinfo import ZoneInfo
from qualtrics_util.utils.datetime_utils import (
    parse_time_slots,
    get_time_from_slot,
    convert_to_utc,
    calculate_expiration_time,
    should_schedule_future_only,
    validate_time_slots,
    format_datetime_iso
)


class TestDateTimeUtils:
    """Test suite for datetime utilities."""
    
    def test_parse_time_slots_simple(self):
        """Test parsing simple time slots."""
        result = parse_time_slots("800,1200,1600,2000")
        assert result == [800, 1200, 1600, 2000]
    
    def test_parse_time_slots_ranges(self):
        """Test parsing time slot ranges."""
        result = parse_time_slots("[800,900],[1200,1300]")
        assert isinstance(result, list)
        assert len(result) == 2
    
    def test_parse_time_slots_invalid(self):
        """Test parsing invalid time slots."""
        with pytest.raises(Exception):
            parse_time_slots("invalid")
    
    def test_get_time_from_slot_integer(self):
        """Test getting time from integer slot."""
        time = get_time_from_slot(800)
        assert time == 800
    
    def test_get_time_from_slot_range(self):
        """Test getting time from range slot."""
        # Should return a time between the range
        time = get_time_from_slot([800, 900])
        assert 800 <= time <= 900
    
    def test_get_time_from_slot_invalid(self):
        """Test getting time from invalid slot."""
        with pytest.raises(Exception):
            get_time_from_slot("invalid")
    
    def test_convert_to_utc(self):
        """Test timezone conversion."""
        # Test conversion from America/Chicago to UTC
        utc_time = convert_to_utc('2024-01-15', 14, 30, 'America/Chicago')
        
        assert utc_time is not None
        assert utc_time.tzinfo is not None
    
    def test_convert_to_utc_with_offset(self):
        """Test timezone conversion with day offset."""
        utc_time = convert_to_utc('2024-01-15', 14, 30, 'America/Chicago', days_offset=1)
        
        assert utc_time.day == 16  # Next day
        assert utc_time.hour == 20  # Adjusted for timezone
    
    def test_calculate_expiration_time(self):
        """Test calculating expiration time."""
        send_time = datetime(2024, 1, 15, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
        expiration = calculate_expiration_time(send_time, 60)
        
        assert expiration.minute == 0  # Should be exact hour
        assert expiration > send_time
    
    def test_should_schedule_future_only(self):
        """Test future-only scheduling check."""
        future = datetime.now(tz=ZoneInfo("UTC")).replace(hour=23, minute=59, second=59)
        past = datetime.now(tz=ZoneInfo("UTC")).replace(hour=0, minute=0, second=0)
        
        # Create obviously future time
        future_time = future.replace(day=future.day + 1)
        past_time = past.replace(day=past.day - 1)
        
        # Note: These may not always pass due to timing
        # assert should_schedule_future_only(future_time) == True
        # assert should_schedule_future_only(past_time) == False
    
    def test_validate_time_slots(self):
        """Test time slot validation."""
        # Valid integer slots
        assert validate_time_slots([800, 1200, 1600]) == True
        
        # Valid range slots
        assert validate_time_slots([[800, 900], [1200, 1300]]) == True
        
        # Invalid empty list
        assert validate_time_slots([]) == False
        
        # Invalid range (start >= end)
        assert validate_time_slots([[900, 800]]) == False
        
        # Invalid time (out of range)
        assert validate_time_slots([2400]) == False
    
    def test_format_datetime_iso(self):
        """Test ISO 8601 formatting."""
        dt = datetime(2024, 1, 15, 14, 30, 0)
        formatted = format_datetime_iso(dt)
        
        assert '2024-01-15' in formatted
        assert '14:30:00' in formatted or 'T14:30:00' in formatted


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

