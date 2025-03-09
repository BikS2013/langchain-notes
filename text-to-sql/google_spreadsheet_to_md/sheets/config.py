import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

class Config:
    """Configuration management for the sheet processor."""
    
    def __init__(self, spreadsheet_id: Optional[str] = None):
        # Load environment variables
        load_dotenv()
        
        # Optional settings with defaults
        self.spreadsheet_id = spreadsheet_id
        self.credentials_path = os.getenv('CREDENTIALS_PATH', 'credentials.json')
        self.output_dir = os.getenv('OUTPUT_DIR', 'output')
        self.analysis_dir = os.getenv('ANALYSIS_DIR', 'analysis')
        
        # CSV export options
        self.csv_options = self._get_csv_options()
    
    @staticmethod
    def _get_required_env(key: str) -> str:
        """Get a required environment variable."""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"{key} environment variable is not set")
        return value
    
    def _get_csv_options(self) -> Dict[str, Any]:
        """Get CSV export options from environment variables."""
        return {
            'encoding': os.getenv('CSV_ENCODING', 'utf-8'),
            'date_format': os.getenv('CSV_DATE_FORMAT', '%Y-%m-%d'),
            'float_format': os.getenv('CSV_FLOAT_FORMAT', '%.2f'),
            'na_rep': os.getenv('CSV_NA_REP', ''),
            'quoting': 1  # csv.QUOTE_ALL
        }
    
    def get_sheet_specific_config(self, sheet_name: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration specific to a sheet.
        Allows for custom handling of specific sheets.
        
        Args:
            sheet_name (str): Name of the sheet
            
        Returns:
            Optional[Dict[str, Any]]: Sheet-specific configuration if available
        """
        # Could be extended to load from a config file
        return None
    
    def update(self, **kwargs) -> None:
        """
        Update configuration values.
        
        Args:
            **kwargs: Key-value pairs to update
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Unknown configuration key: {key}")