"""
Survey data export operations.

This module provides functionality for exporting survey response data
from Qualtrics surveys in various formats.
"""

from typing import Optional, Union
import requests
import time
import zipfile
import io
import os
import glob
import tempfile
import shutil
import json
import pandas as pd
from .base import BaseQualtricsClient


class SurveysAPI(BaseQualtricsClient):
    """API for exporting survey data from Qualtrics."""
    
    def __init__(self, *args, survey_id: str, **kwargs):
        """
        Initialize the Surveys API client.
        
        Args:
            *args: Arguments to pass to BaseQualtricsClient
            survey_id: Survey ID
            **kwargs: Additional arguments to pass to BaseQualtricsClient
        """
        super().__init__(*args, **kwargs)
        self.survey_id = survey_id
    
    def export_responses(
        self,
        file_format: str = 'json',
        wait_time: float = 7.5,
        return_format: str = 'df',
        max_retries: int = 5
    ) -> Union[pd.DataFrame, dict]:
        """
        Export survey responses to a file and return as dataframe or dict.
        
        Args:
            file_format: Export format ('json' or 'csv')
            wait_time: Time to wait between progress checks (seconds)
            return_format: Return format ('df' for DataFrame or 'dict')
            max_retries: Maximum number of retries for export
            
        Returns:
            DataFrame or dict containing survey responses
            
        Raises:
            QualtricsAPIError: If the export fails
        """
        url = self.build_url(f'/API/v3/surveys/{self.survey_id}/export-responses/')
        headers = self.get_headers()
        
        # Step 1: Create export request
        data = {'format': file_format}
        
        try:
            response = self.make_request('POST', url, headers=headers, json_data=data)
            progress_id = response.json()["result"]["progressId"]
        except KeyError:
            print(response.json())
            raise
        
        # Step 2: Check export progress and wait until ready
        progress_status = "inProgress"
        file_id = None
        retry_count = 0
        
        while progress_status not in ["complete", "failed"] and file_id is None:
            check_url = url + progress_id
            progress_response = self.make_request('GET', check_url, headers=headers)
            
            try:
                file_id = progress_response.json()["result"]["fileId"]
            except KeyError:
                pass
            
            progress = progress_response.json()["result"]["percentComplete"]
            progress_status = progress_response.json()["result"]["status"]
            
            if self.verbose > 0:
                print(f"Download is {progress}% complete")
            
            if progress_status not in ["complete", "failed"]:
                retry_count += 1
                if retry_count > max_retries:
                    raise Exception("Exceeded maximum retries. Exiting.")
                
                sleep_interval = wait_time * (2 ** (retry_count - 1))
                if self.verbose > 0:
                    print(f"Retrying in {sleep_interval} seconds...")
                time.sleep(sleep_interval)
        
        # Step 3: Download the file
        download_url = url + file_id + '/file'
        download_response = requests.get(download_url, headers=headers, stream=True, verify=self.verify)
        
        # Step 4: Unzip and process
        with tempfile.TemporaryDirectory() as temp_dir:
            zipfile.ZipFile(io.BytesIO(download_response.content)).extractall(temp_dir)
            tmp_path = glob.glob(os.path.join(temp_dir, f"*{file_format}"))[0]
            base_name = os.path.basename(tmp_path)
            clean_base_name = base_name.replace(" ", "_").replace(":", "")
            
            local_dir = os.getcwd()
            new_path = os.path.join(local_dir, clean_base_name)
            
            if file_format == 'csv':
                shutil.copy(tmp_path, new_path)
                df = pd.read_csv(tmp_path, skiprows=[1, 2])
                result_data = df
            elif file_format == 'json':
                with open(tmp_path) as fp:
                    ddict = json.load(fp)
                
                ddict['source'] = 'qualtrics'
                
                with open(new_path, 'w') as fp:
                    json.dump(ddict, fp, indent=4)
                
                df = pd.DataFrame(ddict['responses'])
                result_data = ddict if return_format == 'dict' else df
            
            if self.verbose > 0:
                print(f'Complete: data written to {new_path}')
            
            return result_data

