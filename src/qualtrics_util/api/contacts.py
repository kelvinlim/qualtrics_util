"""
Contact management for Qualtrics mailing lists.

This module provides functionality for retrieving and updating contacts
in Qualtrics mailing lists.
"""

from typing import List, Dict, Any, Optional
from .base import BaseQualtricsClient


class ContactsAPI(BaseQualtricsClient):
    """API for managing contacts in Qualtrics mailing lists."""
    
    def __init__(self, *args, directory_id: str, mailing_list_id: str, **kwargs):
        """
        Initialize the Contacts API client.
        
        Args:
            *args: Arguments to pass to BaseQualtricsClient
            directory_id: Qualtrics directory ID
            mailing_list_id: Mailing list ID
            **kwargs: Additional arguments to pass to BaseQualtricsClient
        """
        super().__init__(*args, **kwargs)
        self.directory_id = directory_id
        self.mailing_list_id = mailing_list_id
    
    def get_contact_list(self, include_embedded: bool = True) -> List[Dict[str, Any]]:
        """
        Get all contacts from the mailing list.
        
        Args:
            include_embedded: Whether to include embedded data (default: True)
            
        Returns:
            List of contact dictionaries
            
        Raises:
            QualtricsAPIError: If the API request fails
        """
        path = f"/API/v3/directories/{self.directory_id}/mailinglists/{self.mailing_list_id}/contacts"
        
        params = {}
        if include_embedded:
            params['includeEmbedded'] = 'true'
        
        url = self.build_url(path, params)
        headers = self.get_headers()
        
        try:
            response = self.make_request('GET', url, headers=headers)
            data = response.json()
            return data.get('result', {}).get('elements', [])
        except Exception as e:
            if self.verbose > 0:
                print(f"Error getting contact list: {e}")
            raise
    
    def get_contact(self, contact_id: str) -> Dict[str, Any]:
        """
        Get a single contact by ID.
        
        Args:
            contact_id: The contact ID
            
        Returns:
            Contact dictionary
            
        Raises:
            QualtricsAPIError: If the API request fails
        """
        path = f"/API/v3/directories/{self.directory_id}/mailinglists/{self.mailing_list_id}/contacts/{contact_id}"
        
        url = self.build_url(path)
        headers = self.get_headers()
        
        try:
            response = self.make_request('GET', url, headers=headers)
            data = response.json()
            return data.get('result', {})
        except Exception as e:
            if self.verbose > 0:
                print(f"Error getting contact {contact_id}: {e}")
            raise
    
    def get_contact_lookup_id(self, mailing_list_id: str, contact_id: str) -> str:
        """
        Get the ContactLookupId for a specific contact.
        
        The ContactLookupId begins with "CGC_" and is required when sending
        distributions from a mailing list to an individual.
        
        Args:
            mailing_list_id: The mailing list ID
            contact_id: The contact ID
            
        Returns:
            ContactLookupId string
            
        Raises:
            QualtricsAPIError: If the API request fails
        """
        path = f"/API/v3/directories/{self.directory_id}/contacts/{contact_id}"
        
        url = self.build_url(path)
        headers = self.get_headers()
        
        try:
            response = self.make_request('GET', url, headers=headers)
            data = response.json()
            
            # Extract the ContactLookupId from the mailing list membership
            membership = data.get('result', {}).get('mailingListMembership', {})
            mailing_list_membership = membership.get(mailing_list_id, {})
            
            return mailing_list_membership.get('contactLookupId')
            
        except Exception as e:
            if self.verbose > 0:
                print(f"Error getting contact lookup ID: {e}")
            raise
    
    def update_contact(
        self,
        contact_id: str,
        data: Dict[str, Any],
        **kwargs
    ) -> bool:
        """
        Update a contact in the mailing list.
        
        Args:
            contact_id: The contact ID to update
            data: Dictionary of fields to update
            **kwargs: Additional update parameters
            
        Returns:
            True if successful
            
        Raises:
            QualtricsAPIError: If the API request fails
        """
        path = f"/API/v3/directories/{self.directory_id}/mailinglists/{self.mailing_list_id}/contacts/{contact_id}"
        
        url = self.build_url(path)
        headers = self.get_headers()
        
        try:
            # Remove contactId if it exists to avoid error
            if 'contactId' in data:
                del data['contactId']
            
            # Ensure language is set
            if data.get('language') is None:
                data['language'] = 'en'
            
            response = self.make_request('PUT', url, headers=headers, json_data=data)
            return response.ok
            
        except Exception as e:
            if self.verbose > 0:
                print(f"Error updating contact {contact_id}: {e}")
            raise

