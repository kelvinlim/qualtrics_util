#!/usr/bin/env python3
"""
Quick test to validate Phase 2 API layer implementation.

Run: python test_phase2_api.py
"""

import sys
sys.path.insert(0, 'src')

from qualtrics_util.config import load_configuration
from qualtrics_util.api import ContactsAPI, DistributionsAPI, MessagesAPI, SurveysAPI

print("Testing Phase 2 API Layer...")
print("=" * 50)

# Load configuration
loader, success = load_configuration(
    config_file='config_qualtrics.yaml',
    env_file='qualtrics_token'
)

if not success:
    print("❌ Configuration loading failed")
    sys.exit(1)

print("✅ Configuration loaded")
print()

# Initialize API clients
print("Initializing API clients...")

try:
    # Contacts API
    contacts_api = ContactsAPI(
        api_token=loader.api_token,
        data_center=loader.get('account.DATA_CENTER'),
        directory_id=loader.get('account.DEFAULT_DIRECTORY'),
        mailing_list_id=loader.get('project.MAILING_LIST_ID'),
        verify=False,
        verbose=1
    )
    print("✅ ContactsAPI initialized")
    
    # Distributions API
    distributions_api = DistributionsAPI(
        api_token=loader.api_token,
        data_center=loader.get('account.DATA_CENTER'),
        survey_id=loader.get('project.SURVEY_ID'),
        verify=False,
        verbose=1
    )
    print("✅ DistributionsAPI initialized")
    
    # Messages API
    messages_api = MessagesAPI(
        api_token=loader.api_token,
        data_center=loader.get('account.DATA_CENTER'),
        library_id=loader.get('account.LIBRARY_ID'),
        verify=False,
        verbose=1
    )
    print("✅ MessagesAPI initialized")
    
    # Surveys API
    surveys_api = SurveysAPI(
        api_token=loader.api_token,
        data_center=loader.get('account.DATA_CENTER'),
        survey_id=loader.get('project.SURVEY_ID'),
        verify=False,
        verbose=1
    )
    print("✅ SurveysAPI initialized")
    
    print()
    print("✅ All API clients initialized successfully!")
    print()
    
    # Test getting contacts
    print("Testing: Get contact list (first 3 contacts)...")
    contacts = contacts_api.get_contact_list()
    print(f"✅ Retrieved {len(contacts)} contacts")
    
    if contacts:
        print(f"   First contact: {contacts[0].get('lastName')}, {contacts[0].get('firstName')}")
    
    print()
    print("=" * 50)
    print("✅ Phase 2 API Layer - ALL TESTS PASSED!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

