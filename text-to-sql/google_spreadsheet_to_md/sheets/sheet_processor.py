from typing import Dict, Any, Optional, List
import logging
import pandas as pd
from .google_client import GoogleSheetsClient
from .data_processor import SheetDataProcessor
from .file_manager import FileManager
from .config import Config

logger = logging.getLogger(__name__)

class SheetProcessor:
    """Main class that orchestrates the sheet processing workflow."""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.google_client = GoogleSheetsClient(self.config.credentials_path)
        self.data_processor = SheetDataProcessor()
        self.file_manager = FileManager(base_dir='.', output_dir=self.config.output_dir)
    
    def process_spreadsheet(self) -> Dict[str, Dict[str, Any]]:
        """
        Process all sheets in the configured spreadsheet.
        
        Returns:
            Dict[str, Dict[str, Any]]: Analysis results for all sheets
        """
        try:
            sheets = self.google_client.get_service()
            
            # Get spreadsheet metadata
            metadata = sheets.get(spreadsheetId=self.config.spreadsheet_id).execute()
            spreadsheet_title = metadata.get('properties', {}).get('title', '')
            sheet_names = [sheet['properties']['title'] for sheet in metadata['sheets']]
            
            # Save metadata separately
            metadata = {
                'spreadsheet_title': spreadsheet_title,
                'spreadsheet_id': self.config.spreadsheet_id
            }
            self.file_manager.save_metadata(metadata)
            
            analyses = {}
            dataframes = {}
            
            # Process each sheet
            for sheet_name in sheet_names:
                logger.info(f"Processing sheet: {sheet_name}")
                
                try:
                    df = self._process_single_sheet(sheets, sheet_name)
                    if not df.empty:
                        dataframes[sheet_name] = df
                        analyses[sheet_name] = self.data_processor.analyze_sheet_data(sheet_name)
                        self.file_manager.save_analysis(analyses[sheet_name], sheet_name)
                except Exception as e:
                    logger.error(f"Error processing sheet {sheet_name}: {str(e)}")
                    continue
            
            # Export all processed sheets
            if dataframes:
                self.file_manager.export_to_csv(dataframes, self.config.csv_options)
            
            return analyses
            
        except Exception as e:
            logger.error(f"Error processing spreadsheet: {str(e)}")
            raise
    
    def _process_single_sheet(self, sheets, sheet_name: str) -> pd.DataFrame:
        """
        Process a single sheet from the spreadsheet.
        
        Args:
            sheets: Google Sheets service
            sheet_name (str): Name of the sheet to process
            
        Returns:
            pd.DataFrame: Processed sheet data
        """
        # Get sheet data
        result = sheets.values().get(
            spreadsheetId=self.config.spreadsheet_id,
            range=sheet_name
        ).execute()
        
        values = result.get('values', [])
        if not values:
            logger.warning(f"No data found in sheet: {sheet_name}")
            return pd.DataFrame()
        
        # Process the sheet values
        return self.data_processor.process_sheet_values(values, sheet_name)
    
    def get_sheet_analysis(self, sheet_name: str) -> Optional[Dict[str, Any]]:
        """
        Get analysis results for a specific sheet.
        
        Args:
            sheet_name (str): Name of the sheet
            
        Returns:
            Optional[Dict[str, Any]]: Analysis results if available
        """
        return self.file_manager.load_analysis(sheet_name)
    
    def get_all_analyses(self) -> Dict[str, Dict[str, Any]]:
        """
        Get analysis results for all processed sheets.
        
        Returns:
            Dict[str, Dict[str, Any]]: All available sheet analyses
        """
        return self.file_manager.get_all_analyses()