"""
Base API client for Qualtrics REST API.

This module provides the foundation for all Qualtrics API interactions,
including authentication, request handling, and error management.
"""

import requests
from typing import Dict, Optional, Any, List
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning


class QualtricsAPIError(Exception):
    """Custom exception for Qualtrics API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(message)


class BaseQualtricsClient:
    """
    Base client for all Qualtrics API operations.
    
    This class provides:
    - Authentication via API token
    - Consistent request/response handling
    - Error handling and logging
    - URL construction helpers
    """
    
    def __init__(self, api_token: str, data_center: str, verify: bool = True, verbose: int = 1):
        """
        Initialize the base Qualtrics API client.
        
        Args:
            api_token: Qualtrics API token for authentication
            data_center: Qualtrics data center (e.g., 'yul1')
            verify: Whether to verify SSL certificates (default: True)
            verbose: Verbosity level (0-3, default: 1)
        """
        self.api_token = api_token
        self.data_center = data_center
        self.verify = verify
        self.verbose = verbose
        
        # Disable SSL warnings if verify is False
        if not verify:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    
    def get_headers(self, content_type: str = 'application/json') -> Dict[str, str]:
        """
        Get request headers with authentication.
        
        Args:
            content_type: Content-Type header value
            
        Returns:
            Dictionary of HTTP headers
        """
        headers = {
            'x-api-token': self.api_token,
        }
        
        if content_type:
            headers['Content-Type'] = content_type
        
        return headers
    
    def build_url(self, path: str, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Build a full Qualtrics API URL.
        
        Args:
            path: API endpoint path (e.g., '/directories/xxx/mailinglists/yyy/contacts')
            params: Optional query parameters
            
        Returns:
            Complete URL string
        """
        base_url = f"https://{self.data_center}.qualtrics.com{path}"
        
        if params:
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            base_url = f"{base_url}?{query_string}"
        
        return base_url
    
    def make_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict] = None,
        **kwargs
    ) -> requests.Response:
        """
        Make an HTTP request to the Qualtrics API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            url: Complete URL
            headers: Optional request headers
            params: Optional query parameters
            json_data: Optional JSON request body
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Response object
            
        Raises:
            QualtricsAPIError: If the API request fails
        """
        if headers is None:
            headers = self.get_headers()
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params, verify=self.verify, **kwargs)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=json_data, params=params, verify=self.verify, **kwargs)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, json=json_data, params=params, verify=self.verify, **kwargs)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, params=params, verify=self.verify, **kwargs)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Check for API errors
            if not response.ok:
                self._handle_error_response(response)
            
            return response
            
        except requests.exceptions.RequestException as e:
            raise QualtricsAPIError(f"Request failed: {str(e)}") from e
    
    def _handle_error_response(self, response: requests.Response) -> None:
        """
        Handle error responses from the API.
        
        Args:
            response: The response object containing the error
            
        Raises:
            QualtricsAPIError: Always raises an error with details
        """
        try:
            error_data = response.json()
            
            # Try to extract error message
            error_message = error_data.get('meta', {}).get('error', {}).get('errorMessage', '')
            if not error_message:
                error_message = response.text[:200]  # Fallback to first 200 chars
            
        except (json.JSONDecodeError, AttributeError):
            error_message = response.text[:200]
        
        raise QualtricsAPIError(
            f"API request failed with status {response.status_code}: {error_message}",
            status_code=response.status_code,
            response=error_data if 'error_data' in locals() else None
        )
    
    def get_paginated(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        max_pages: Optional[int] = None
    ) -> List[Dict]:
        """
        Make a paginated GET request and collect all results.
        
        Args:
            url: Initial URL
            headers: Optional request headers
            max_pages: Maximum number of pages to fetch (None for all)
            
        Returns:
            List of all result elements from all pages
        """
        if headers is None:
            headers = self.get_headers()
        
        all_elements = []
        current_url = url
        page_count = 0
        
        if self.verbose > 0:
            print("Getting results...", end="", flush=True)
        
        while current_url:
            try:
                response = requests.get(current_url, headers=headers, verify=self.verify)
                response.raise_for_status()
                
                data = response.json()
                status = data.get('meta', {}).get('httpStatus', '')
                
                # Check if we got valid data
                if '200' not in status:
                    break
                
                # Collect elements from this page
                elements = data.get('result', {}).get('elements', [])
                all_elements.extend(elements)
                
                # Check for next page
                next_page = data.get('result', {}).get('nextPage')
                
                if next_page:
                    current_url = next_page
                    page_count += 1
                    
                    if max_pages and page_count >= max_pages:
                        if self.verbose > 0:
                            print(f"Reached max pages limit ({max_pages})")
                        break
                else:
                    current_url = None
                    
            except requests.exceptions.RequestException as e:
                raise QualtricsAPIError(f"Pagination request failed: {str(e)}") from e
        
        if self.verbose > 0:
            print(f" Done ({len(all_elements)} items)")
        
        return all_elements
