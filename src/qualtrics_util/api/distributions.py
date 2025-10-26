"""
Distribution management for Qualtrics surveys.

This module provides functionality for managing survey distributions via
SMS and email in Qualtrics.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import requests
import random
import string
from .base import BaseQualtricsClient


class DistributionsAPI(BaseQualtricsClient):
    """API for managing survey distributions in Qualtrics."""
    
    def __init__(self, *args, survey_id: str, **kwargs):
        """
        Initialize the Distributions API client.
        
        Args:
            *args: Arguments to pass to BaseQualtricsClient
            survey_id: Survey ID for distributions
            **kwargs: Additional arguments to pass to BaseQualtricsClient
        """
        super().__init__(*args, **kwargs)
        self.survey_id = survey_id
    
    def get_email_distributions(
        self,
        mailing_list_id: Optional[str] = None,
        send_start_date: Optional[str] = None,
        distribution_type: str = 'Invite'
    ) -> List[Dict[str, Any]]:
        """
        Get email distributions for a survey.
        
        Args:
            mailing_list_id: Optional mailing list ID to filter
            send_start_date: Optional start date filter
            distribution_type: Type of distribution (default: 'Invite')
            
        Returns:
            List of distribution dictionaries
            
        Raises:
            QualtricsAPIError: If the API request fails
        """
        params = {
            'surveyId': self.survey_id,
            'distributionRequestType': distribution_type,
            'useNewPaginationScheme': 'true'
        }
        
        if mailing_list_id:
            params['mailingListId'] = mailing_list_id
        
        if send_start_date:
            params['sendStartDate'] = send_start_date
        
        url = self.build_url('/API/v3/distributions/', params)
        
        return self.get_paginated(url)
    
    def get_sms_distributions(
        self,
        survey_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get SMS distributions for a survey.
        
        Args:
            survey_id: Optional survey ID (uses self.survey_id if not provided)
            
        Returns:
            List of SMS distribution dictionaries
            
        Raises:
            QualtricsAPIError: If the API request fails
        """
        if survey_id is None:
            survey_id = self.survey_id
        
        params = {'surveyId': survey_id}
        
        url = self.build_url('/API/v3/distributions/sms', params)
        
        return self.get_paginated(url)
    
    def delete_sms_distribution(
        self,
        distribution_id: str,
        survey_id: Optional[str] = None
    ) -> bool:
        """
        Delete an SMS distribution.
        
        Args:
            distribution_id: The distribution ID to delete
            survey_id: Optional survey ID
            
        Returns:
            True if successful
            
        Raises:
            QualtricsAPIError: If the API request fails
        """
        if survey_id is None:
            survey_id = self.survey_id
        
        params = {'surveyId': survey_id}
        
        url = self.build_url(f'/API/v3/distributions/sms/{distribution_id}', params)
        headers = self.get_headers()
        
        try:
            response = self.make_request('DELETE', url, headers=headers)
            
            if self.verbose > 1:
                print(f"Deleted SMS distribution {distribution_id}")
            
            return response.ok
            
        except Exception as e:
            if self.verbose > 0:
                print(f"Error deleting SMS distribution {distribution_id}: {e}")
            return False
    
    def delete_email_distribution(
        self,
        distribution_id: str
    ) -> bool:
        """
        Delete an email distribution.
        
        Args:
            distribution_id: The distribution ID to delete
            
        Returns:
            True if successful
            
        Raises:
            QualtricsAPIError: If the API request fails
        """
        url = self.build_url(f'/API/v3/distributions/{distribution_id}')
        headers = self.get_headers()
        
        try:
            response = self.make_request('DELETE', url, headers=headers)
            
            if self.verbose > 1:
                print(f"Deleted email distribution {distribution_id}")
            
            return response.ok
            
        except Exception as e:
            if self.verbose > 0:
                print(f"Error deleting email distribution {distribution_id}: {e}")
            return False
    
    def send_sms_distribution(
        self,
        contact_lookup_id: str,
        send_date: datetime,
        expiration_date: datetime,
        message_text: str,
        mailing_list_id: str,
        method: str = 'Invite',
        survey_id: Optional[str] = None
    ) -> requests.Response:
        """
        Send an SMS distribution.
        
        Args:
            contact_lookup_id: Contact lookup ID
            send_date: When to send the distribution
            expiration_date: When the survey link expires
            message_text: SMS message text
            mailing_list_id: Mailing list ID
            method: Distribution method (default: 'Invite')
            survey_id: Optional survey ID
            
        Returns:
            Response object
            
        Raises:
            QualtricsAPIError: If the API request fails
        """
        if survey_id is None:
            survey_id = self.survey_id
        
        url = self.build_url('/API/v3/distributions/sms')
        headers = self.get_headers()
        
        recipients = {
            'mailingListId': mailing_list_id,
            'contactId': contact_lookup_id
        }
        
        # Add random text to avoid duplicate message issues
        import random
        import string
        
        random_text = '\n[' + ''.join([
            random.choice(string.ascii_letters + string.digits)
            for _ in range(8)
        ]) + ']\n'
        
        message = {
            'messageText': message_text + random_text
        }
        
        data = {
            'sendDate': send_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'surveyLinkExpirationDate': expiration_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'method': method,
            'surveyId': survey_id,
            'name': "SMS message",
            'recipients': recipients,
            'message': message
        }
        
        if self.verbose > 2:
            from pprint import pprint
            pprint(data)
        
        try:
            response = self.make_request('POST', url, headers=headers, json_data=data)
            
            if self.verbose > 1:
                from pprint import pprint
                pprint(response.json())
            
            return response
            
        except Exception as e:
            if self.verbose > 0:
                print(f"Error sending SMS distribution: {e}")
            raise

