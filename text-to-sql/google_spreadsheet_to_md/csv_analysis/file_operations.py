"""
Module for handling file operations related to CSV analysis.
"""

import os
from typing import List, Dict, Any, Optional
import pandas as pd
import json

def get_csv_files(output_dir: str) -> List[str]:
    """
    Get a list of all CSV files in the output directory.
    
    Args:
        output_dir: Directory to search for CSV files
    
    Returns:
        List of CSV filenames
    """
    return [f for f in os.listdir(output_dir) if f.endswith('.csv')]

def save_analysis(output_dir: str, csv_filename: str, analysis_text: str) -> None:
    """
    Save analysis text to a file with _analysis.txt suffix.
    
    Args:
        output_dir: Directory to save the analysis file
        csv_filename: Name of the CSV file
        analysis_text: Analysis text to save
    """
    # Generate output filename
    output_filename = csv_filename.replace(".csv", "_analysis.txt")
    output_path = os.path.join(output_dir, output_filename)
    
    # Save analysis text to file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(analysis_text)
        
    print(f"Analysis saved to {output_path}")

def extract_table_info(df: pd.DataFrame) -> tuple[Optional[str], List[Dict[str, Any]]]:
    """
    Extract table information from a Tables Description DataFrame.
    
    Args:
        df: DataFrame containing table description data
        
    Returns:
        Tuple containing table name (if found) and list of column information dictionaries
    """
    # Try to determine the table name from the filename or content
    table_name = None
    
    # Extract column information
    columns_info = []
    
    # Find the column name column
    column_name_indicators = ['column', 'name', 'field', 'attribute']
    column_name_col = next(
        (col for col in df.columns if any(ind in col.lower() for ind in column_name_indicators)),
        None
    )
    
    if column_name_col:
        # For each row (which represents a column in the described table)
        for _, row in df.iterrows():
            column_info = {}
            
            # Extract column name
            column_info['name'] = row[column_name_col]
            
            # Extract other information about the column
            for col in df.columns:
                if col != column_name_col and pd.notna(row[col]):
                    # Use the column header as the key and the cell value as the value
                    column_info[col] = row[col]
            
            columns_info.append(column_info)
    
    return table_name, columns_info

def read_csv_file(output_dir: str, csv_filename: str) -> pd.DataFrame:
    """
    Read a CSV file from the specified directory.
    
    Args:
        output_dir: Directory containing the CSV file
        csv_filename: Name of the CSV file
    
    Returns:
        DataFrame containing the CSV data
    """
    csv_path = os.path.join(output_dir, csv_filename)
    return pd.read_csv(csv_path)