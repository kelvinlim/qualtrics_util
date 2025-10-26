"""
Message library operations.

This module provides functionality for retrieving messages from
Qualtrics message libraries.
"""

from typing import Dict, Any, List, Optional
import random
import string
from .base import BaseQualtricsClient


class MessagesAPI(BaseQualtricsClient):
    """API for working with Qualtrics message libraries."""
    
    def __init__(self, *args, library_id: str, **kwargs):
        """
        Initialize the Messages API client.
        
        Args:
            *args: Arguments to pass to BaseQualtricsClient
            library_id: Library ID
            **kwargs: Additional arguments to pass to BaseQualtricsClient
        """
        super().__init__(*args, **kwargs)
        self.library_id = library_id
    
    def get_message(self, message_id: str) -> str:
        """
        Get a message from the library.
        
        Args:
            message_id: Message ID
            
        Returns:
            Message text in English
            
        Raises:
            QualtricsAPIError: If the API request fails
        """
        path = f"/API/v3/libraries/{self.library_id}/messages/{message_id}"
        
        url = self.build_url(path)
        headers = self.get_headers()
        
        try:
            response = self.make_request('GET', url, headers=headers)
            data = response.json()
            
            if 'meta' in data and data['meta'].get('httpStatus') == '200 - OK':
                return data['result']['messages']['en']
            else:
                raise Exception(f"Error getting message: {response.text}")
                
        except Exception as e:
            if self.verbose > 0:
                print(f"Error getting message {message_id}: {e}")
            raise
    
    def get_message_with_random_text(self, message_id: str, random_length: int = 8) -> str:
        """
        Get a message and append random text to avoid duplicate message issues.
        
        Args:
            message_id: Message ID
            random_length: Length of random text to append
            
        Returns:
            Message text with random text appended
        """
        message_text = self.get_message(message_id)
        
        # Generate random text
        random_text = '\n[' + ''.join([
            random.choice(string.ascii_letters + string.digits)
            for _ in range(random_length)
        ]) + ']\n'
        
        return message_text + random_text
    
    def get_all_messages(self) -> Dict[str, Any]:
        """
        Get all messages from the library.
        
        Returns:
            Dictionary of all messages
            
        Raises:
            QualtricsAPIError: If the API request fails
        """
        path = f"/API/v3/libraries/{self.library_id}/messages"
        
        url = self.build_url(path)
        headers = self.get_headers()
        
        try:
            response = self.make_request('GET', url, headers=headers)
            data = response.json()
            
            if 'meta' in data and data['meta'].get('httpStatus') == '200 - OK':
                return data['result']
            else:
                raise Exception(f"Error getting messages: {response.text}")
                
        except Exception as e:
            if self.verbose > 0:
                print(f"Error getting messages: {e}")
            raise

