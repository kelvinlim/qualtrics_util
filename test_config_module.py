#!/usr/bin/env python3
"""
Quick test to demonstrate the new configuration module.

Run: python test_config_module.py
"""

import sys
sys.path.insert(0, 'src')

from qualtrics_util.config import load_configuration

print("Testing new configuration module...")
print("=" * 50)

# Load configuration
loader, success = load_configuration(
    config_file='config_qualtrics.yaml',
    env_file='qualtrics_token'
)

if success:
    print("✅ Configuration loaded successfully!")
    print()
    
    # Test accessing configuration values
    data_center = loader.get('account.DATA_CENTER')
    survey_id = loader.get('project.SURVEY_ID')
    mailing_list_id = loader.get('project.MAILING_LIST_ID')
    timezone = loader.get('project.TIMEZONE')
    
    print(f"Data Center: {data_center}")
    print(f"Survey ID: {survey_id}")
    print(f"Mailing List ID: {mailing_list_id}")
    print(f"Timezone: {timezone}")
    print()
    print("✅ Configuration module working perfectly!")
else:
    print("❌ Configuration loading failed")
    sys.exit(1)

