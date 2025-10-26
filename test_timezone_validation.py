#!/usr/bin/env python3
"""
Tests for timezone validation in qualtrics_util.

Run: python test_timezone_validation.py
"""

import sys
import os
import tempfile
import yaml
from zoneinfo import ZoneInfo
from qualtrics_util import QualtricsDist


def test_valid_timezone():
    """Test that valid IANA timezones pass validation."""
    print("Test 1: Valid timezone (America/Chicago)")
    qd = QualtricsDist()
    
    try:
        qd.read_config('config_qualtrics.yaml')
        print("✅ PASS: Valid timezone accepted")
        return True
    except Exception as e:
        print(f"❌ FAIL: Valid timezone rejected: {e}")
        return False


def test_invalid_project_timezone():
    """Test that invalid project timezone raises an error."""
    print("\nTest 2: Invalid project timezone")
    
    # Create temporary config with invalid timezone
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        temp_config = f.name
        test_config = {
            'account': {
                'DATA_CENTER': 'test',
                'DEFAULT_DIRECTORY': 'TEST',
                'LIBRARY_ID': 'TEST',
                'VERIFY': False
            },
            'project': {
                'SURVEY_ID': 'TEST',
                'MESSAGE_ID': 'TEST',
                'MESSAGE_ID_EMAIL': 'TEST',
                'MAILING_LIST_ID': 'TEST',
                'TIMEZONE': 'Invalid/Timezone',  # Invalid timezone
                'MINUTES_EXPIRE': 60
            },
            'embedded_data': {
                'StartDate': '2025-10-26',
                'SurveysScheduled': 0,
                'TimeSlots': '800,1200,1600,2000',
                'ContactMethod': 'sms',
                'DeleteUnsent': 0,
                'NumDays': 0,
                'ExpireMinutes': 60,
                'LogData': '[{"action":"init"}]',
                'TimeZone': 'America/Chicago'
            }
        }
        yaml.dump(test_config, f)
    
    qd = QualtricsDist()
    
    try:
        qd.read_config(temp_config)
        print("❌ FAIL: Invalid timezone was accepted (should have exited)")
        success = False
    except SystemExit:
        # SystemExit is expected when validation fails
        print("✅ PASS: Invalid timezone correctly rejected")
        success = True
    finally:
        if os.path.exists(temp_config):
            os.unlink(temp_config)
    
    return success


def test_invalid_embedded_timezone():
    """Test that invalid embedded_data TimeZone raises an error."""
    print("\nTest 3: Invalid embedded_data TimeZone")
    
    # Create temporary config with invalid embedded data timezone
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        temp_config = f.name
        test_config = {
            'account': {
                'DATA_CENTER': 'test',
                'DEFAULT_DIRECTORY': 'TEST',
                'LIBRARY_ID': 'TEST',
                'VERIFY': False
            },
            'project': {
                'SURVEY_ID': 'TEST',
                'MESSAGE_ID': 'TEST',
                'MESSAGE_ID_EMAIL': 'TEST',
                'MAILING_LIST_ID': 'TEST',
                'TIMEZONE': 'America/Chicago',
                'MINUTES_EXPIRE': 60
            },
            'embedded_data': {
                'StartDate': '2025-10-26',
                'SurveysScheduled': 0,
                'TimeSlots': '800,1200,1600,2000',
                'ContactMethod': 'sms',
                'DeleteUnsent': 0,
                'NumDays': 0,
                'ExpireMinutes': 60,
                'LogData': '[{"action":"init"}]',
                'TimeZone': 'Invalid/Timezone'  # Invalid timezone
            }
        }
        yaml.dump(test_config, f)
    
    qd = QualtricsDist()
    
    try:
        qd.read_config(temp_config)
        print("❌ FAIL: Invalid timezone was accepted (should have exited)")
        success = False
    except SystemExit:
        # SystemExit is expected when validation fails
        print("✅ PASS: Invalid timezone correctly rejected")
        success = True
    finally:
        if os.path.exists(temp_config):
            os.unlink(temp_config)
    
    return success


def test_missing_timezone():
    """Test that missing timezones are handled gracefully."""
    print("\nTest 4: Missing timezones (should be skipped)")
    
    # Create temporary config without timezones
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        temp_config = f.name
        test_config = {
            'account': {
                'DATA_CENTER': 'test',
                'DEFAULT_DIRECTORY': 'TEST',
                'LIBRARY_ID': 'TEST',
                'VERIFY': False
            },
            'project': {
                'SURVEY_ID': 'TEST',
                'MESSAGE_ID': 'TEST',
                'MESSAGE_ID_EMAIL': 'TEST',
                'MAILING_LIST_ID': 'TEST',
                'MINUTES_EXPIRE': 60
                # No TIMEZONE field
            },
            'embedded_data': {
                'StartDate': '2025-10-26',
                'SurveysScheduled': 0
                # No TimeZone field
            }
        }
        yaml.dump(test_config, f)
    
    qd = QualtricsDist()
    
    try:
        qd.read_config(temp_config)
        print("✅ PASS: Missing timezones handled gracefully")
        success = True
    except Exception as e:
        print(f"❌ FAIL: Should handle missing timezones: {e}")
        success = False
    finally:
        if os.path.exists(temp_config):
            os.unlink(temp_config)
    
    return success


def test_various_valid_timezones():
    """Test various valid IANA timezones."""
    print("\nTest 5: Various valid IANA timezones")
    
    valid_timezones = [
        'America/New_York',
        'America/Los_Angeles',
        'Europe/London',
        'Asia/Tokyo',
        'Australia/Sydney',
        'America/Chicago',
        'UTC'
    ]
    
    for tz in valid_timezones:
        try:
            ZoneInfo(tz)
        except Exception as e:
            print(f"❌ FAIL: {tz} should be valid but failed: {e}")
            return False
    
    print(f"✅ PASS: All {len(valid_timezones)} timezones are valid")
    return True


def main():
    """Run all timezone validation tests."""
    print("=" * 60)
    print("Testing Timezone Validation")
    print("=" * 60)
    
    results = []
    results.append(test_valid_timezone())
    results.append(test_invalid_project_timezone())
    results.append(test_invalid_embedded_timezone())
    results.append(test_missing_timezone())
    results.append(test_various_valid_timezones())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED!")
        print("=" * 60)
        sys.exit(1)


if __name__ == '__main__':
    main()
