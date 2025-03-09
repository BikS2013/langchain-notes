import os
import json
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Union

def _json_serializable(obj: Any) -> Union[int, float, str, None]:
    """Convert numpy types to Python native types for JSON serialization."""
    if isinstance(obj, (np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64,
                       np.uint8, np.uint16, np.uint32, np.uint64)):
        return int(obj)
    elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif pd.isna(obj):
        return None
    return obj

logger = logging.getLogger(__name__)

class FileManager:
    """Handles file operations for the sheet processor."""
    
    def __init__(self, base_dir: str = '.', output_dir: str = None):
        self.base_dir = base_dir
        self.output_dir = output_dir or os.path.join(base_dir, 'output')
        # Place analysis directory under the output directory
        self.analysis_dir = os.path.join(self.output_dir, 'analysis')
        
        # Create directories
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.analysis_dir, exist_ok=True)

    def save_metadata(self, metadata: Dict[str, Any]) -> None:
        """
        Saves spreadsheet metadata to a JSON file.
        
        Args:
            metadata (Dict[str, Any]): Metadata to save
        """
        metadata_path = os.path.join(self.output_dir, 'metadata.json')
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved spreadsheet metadata to {metadata_path}")
        except Exception as e:
            logger.error(f"Failed to save metadata: {str(e)}")

    def load_metadata(self) -> Dict[str, Any]:
        """
        Loads spreadsheet metadata from JSON file.
        
        Returns:
            Dict[str, Any]: The loaded metadata
        """
        metadata_path = os.path.join(self.output_dir, 'metadata.json')
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("No metadata file found")
            return {}
        except Exception as e:
            logger.error(f"Failed to load metadata: {str(e)}")
            return {}
    
    def export_to_csv(self, dataframes: Dict[str, pd.DataFrame], options: Dict[str, Any] = None) -> None:
        """
        Exports each DataFrame to a CSV file.
        
        Args:
            dataframes (Dict[str, pd.DataFrame]): Dictionary of sheet names and their DataFrames
            options (Dict[str, Any], optional): CSV export options like encoding, date_format etc.
        """
        default_options = {
            'encoding': 'utf-8',
            'index': False,
            'date_format': '%Y-%m-%d',
            'quoting': 1  # csv.QUOTE_ALL
        }
        options = {**default_options, **(options or {})}
        
        for sheet_name, df in dataframes.items():
            output_path = os.path.join(self.output_dir, f"{sheet_name}.csv")
            try:
                df.to_csv(output_path, **options)
                logger.info(f"Exported {sheet_name} to {output_path}")
            except Exception as e:
                logger.error(f"Failed to export {sheet_name}: {str(e)}")
    
    def save_analysis(self, analysis: Dict[str, Any], sheet_name: str) -> None:
        """
        Saves sheet analysis results to a JSON file.
        
        Args:
            analysis (Dict[str, Any]): Analysis results to save
            sheet_name (str): Name of the sheet
        """
        analysis_path = os.path.join(self.analysis_dir, f"{sheet_name}_analysis.json")
        try:
            # Convert all values to JSON serializable format
            serializable_analysis = {
                k: {
                    k2: _json_serializable(v2) if isinstance(v2, (np.generic, pd.Timestamp)) else v2
                    for k2, v2 in v.items()
                } if isinstance(v, dict) else _json_serializable(v)
                for k, v in analysis.items()
            }
            
            with open(analysis_path, 'w', encoding='utf-8') as f:
                json.dump(serializable_analysis, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved analysis for {sheet_name} to {analysis_path}")
        except Exception as e:
            logger.error(f"Failed to save analysis for {sheet_name}: {str(e)}")
    
    def load_analysis(self, sheet_name: str) -> Dict[str, Any]:
        """
        Loads sheet analysis results from a JSON file.
        
        Args:
            sheet_name (str): Name of the sheet
            
        Returns:
            Dict[str, Any]: The loaded analysis data
        """
        analysis_path = os.path.join(self.analysis_dir, f"{sheet_name}_analysis.json")
        try:
            with open(analysis_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"No analysis file found for {sheet_name}")
            return {}
        except Exception as e:
            logger.error(f"Failed to load analysis for {sheet_name}: {str(e)}")
            return {}

    def get_all_analyses(self) -> Dict[str, Dict[str, Any]]:
        """
        Loads all available sheet analyses.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of sheet names and their analyses
        """
        analyses = {}
        for filename in os.listdir(self.analysis_dir):
            if filename.endswith('_analysis.json'):
                sheet_name = filename.replace('_analysis.json', '')
                analyses[sheet_name] = self.load_analysis(sheet_name)
        return analyses