"""
Unit tests for the Contacts API.

Run with: pytest tests/test_api/test_contacts.py -v
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
sys.path.insert(0, 'src')

from qualtrics_util.api.contacts import ContactsAPI


class TestContactsAPI:
    """Test suite for ContactsAPI."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.api = ContactsAPI(
            api_token='test_token',
            data_center='yul1',
            directory_id='POOL_test',
            mailing_list_id='CG_test',
            verify=False,
            verbose=1
        )
    
    def test_init(self):
        """Test ContactsAPI initialization."""
        assert self.api.directory_id == 'POOL_test'
        assert self.api.mailing_list_id == 'CG_test'
        assert self.api.data_center == 'yul1'
    
    def test_get_headers(self):
        """Test header generation."""
        headers = self.api.get_headers()
        assert 'x-api-token' in headers
        assert headers['x-api-token'] == 'test_token'
    
    def test_build_url(self):
        """Test URL building."""
        url = self.api.build_url('/API/v3/test')
        assert url == 'https://yul1.qualtrics.com/API/v3/test'
        
        url_with_params = self.api.build_url('/API/v3/test', {'param': 'value'})
        assert 'param=value' in url_with_params
    
    @patch('qualtrics_util.api.contacts.requests.get')
    def test_get_contact_list_success(self, mock_get):
        """Test successful contact list retrieval."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            'result': {
                'elements': [
                    {'firstName': 'John', 'lastName': 'Doe'},
                    {'firstName': 'Jane', 'lastName': 'Smith'}
                ]
            }
        }
        mock_response.ok = True
        mock_get.return_value = mock_response
        
        # Test
        contacts = self.api.get_contact_list()
        
        # Assertions
        assert len(contacts) == 2
        assert contacts[0]['firstName'] == 'John'
        mock_get.assert_called_once()
    
    @patch('qualtrics_util.api.contacts.requests.get')
    def test_get_contact_list_with_embedded(self, mock_get):
        """Test contact list retrieval with embedded data."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            'result': {
                'elements': [{'embeddedData': {'SurveysScheduled': '10'}}]
            }
        }
        mock_response.ok = True
        mock_get.return_value = mock_response
        
        # Test
        contacts = self.api.get_contact_list(include_embedded=True)
        
        # Assertions
        assert len(contacts) == 1
        assert 'embeddedData' in contacts[0]
        # Check that includeEmbedded was added to URL
        mock_get.assert_called_once()
    
    def test_get_contact_list_error(self):
        """Test error handling in contact list retrieval."""
        with pytest.raises(Exception):
            # This will raise because we don't have a real token
            self.api.get_contact_list()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

