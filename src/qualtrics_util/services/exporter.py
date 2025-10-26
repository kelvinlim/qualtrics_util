"""
Export service for survey data.

This module provides functionality for exporting survey responses
to various formats with progress tracking.
"""

from typing import Optional, Union, Dict, Any
import pandas as pd
from ..api.surveys import SurveysAPI
from ..api.base import BaseQualtricsClient


class SurveyExporter:
    """
    Service for exporting survey responses.
    
    This service builds on the SurveysAPI to provide higher-level
    export functionality with progress tracking and error handling.
    """
    
    def __init__(self, surveys_api: SurveysAPI, verbose: int = 1):
        """
        Initialize the survey exporter.
        
        Args:
            surveys_api: SurveysAPI instance
            verbose: Verbosity level (0-3)
        """
        self.surveys_api = surveys_api
        self.verbose = verbose
    
    def export_to_csv(
        self,
        output_file: Optional[str] = None,
        wait_time: float = 7.5
    ) -> pd.DataFrame:
        """
        Export survey responses to CSV file.
        
        Args:
            output_file: Output file path (defaults to auto-generated name)
            wait_time: Time to wait between progress checks
            
        Returns:
            DataFrame containing survey responses
        """
        if self.verbose > 0:
            print("Exporting survey responses to CSV...")
        
        df = self.surveys_api.export_responses(
            file_format='csv',
            wait_time=wait_time
        )
        
        if output_file:
            df.to_csv(output_file, index=False)
            if self.verbose > 0:
                print(f"CSV exported to: {output_file}")
        
        return df
    
    def export_to_json(
        self,
        output_file: Optional[str] = None,
        wait_time: float = 7.5
    ) -> Union[pd.DataFrame, Dict[str, Any]]:
        """
        Export survey responses to JSON file.
        
        Args:
            output_file: Output file path (defaults to auto-generated name)
            wait_time: Time to wait between progress checks
            
        Returns:
            DataFrame or dictionary containing survey responses
        """
        if self.verbose > 0:
            print("Exporting survey responses to JSON...")
        
        result = self.surveys_api.export_responses(
            file_format='json',
            wait_time=wait_time,
            return_format='df'
        )
        
        if isinstance(result, dict):
            if output_file:
                import json
                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=4)
                if self.verbose > 0:
                    print(f"JSON exported to: {output_file}")
        else:
            if output_file:
                result.to_json(output_file, orient='records', indent=2)
                if self.verbose > 0:
                    print(f"JSON exported to: {output_file}")
        
        return result
    
    def export_summary_statistics(self) -> Dict[str, Any]:
        """
        Export summary statistics about survey responses.
        
        Returns:
            Dictionary with summary statistics
        """
        df = self.surveys_api.export_responses(
            file_format='json',
            wait_time=7.5,
            return_format='df'
        )
        
        summary = {
            'total_responses': len(df),
            'columns': list(df.columns),
            'date_range': None
        }
        
        # Try to find date column
        for col in df.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    summary['date_range'] = {
                        'start': str(df[col].min()),
                        'end': str(df[col].max())
                    }
                break
        
        return summary

