"""
Module for processing table description files.
"""

from typing import Dict, Any, Optional, Tuple
import pandas as pd

def process_table_description(
    df: pd.DataFrame,
    csv_filename: str,
    analysis_result: Dict[str, Any]
) -> Optional[str]:
    """
    Process a table columns description CSV file and generate analysis text.
    
    Args:
        df: DataFrame containing the CSV data
        csv_filename: Name of the CSV file
        analysis_result: Dictionary containing analysis results
        
    Returns:
        Analysis text or None if processing failed
    """
    try:
        # Extract table information
        table_name, columns_info = extract_table_info(df)
        
        # Generate analysis text
        analysis_text = f"Analysis of {csv_filename}\n"
        analysis_text += "=" * (len(analysis_text) - 1) + "\n\n"
        
        # Basic file information
        analysis_text += f"File Type: Tables Description\n"
        if table_name:
            analysis_text += f"Table Name: {table_name}\n"
        analysis_text += f"Number of Columns in CSV: {len(df.columns)}\n"
        analysis_text += f"Number of Rows in CSV: {len(df)}\n\n"
        
        # Structure explanation
        analysis_text += generate_table_structure_explanation(
            df, columns_info, analysis_result
        )
        
        return analysis_text
        
    except Exception as e:
        print(f"Error processing {csv_filename}: {str(e)}")
        return None

def extract_table_info(df: pd.DataFrame) -> Tuple[Optional[str], list[Dict[str, Any]]]:
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

def generate_table_structure_explanation(
    df: pd.DataFrame, 
    columns_info: list[Dict[str, Any]], 
    analysis_result: Dict[str, Any]
) -> str:
    """
    Generate the explanation text for table structure.
    
    Args:
        df: DataFrame containing the CSV data
        columns_info: List of column information dictionaries
        analysis_result: Dictionary containing analysis results
        
    Returns:
        Formatted explanation text
    """
    text = "Structure Explanation:\n"
    text += "-" * 20 + "\n"
    text += "This is a Tables Description file where:\n"
    text += "- Each ROW represents a COLUMN in the described database table\n"
    text += "- Each COLUMN in this CSV represents information about the database table columns\n"
    text += "- The CSV column headers indicate what information is provided about each database column\n\n"
    
    # CSV Column Headers
    text += "CSV Column Headers (Information Types):\n"
    text += "-" * 20 + "\n"
    for col in df.columns:
        text += f"- {col}\n"
    text += "\n"
    
    # Described Table Structure
    text += "Described Table Structure:\n"
    text += "-" * 20 + "\n"
    text += f"Number of Columns in Described Table: {len(columns_info)}\n\n"
    
    # Column information
    text += "Column Information:\n"
    text += "-" * 20 + "\n"
    
    for i, col_info in enumerate(columns_info):
        if 'name' in col_info:
            text += f"Column {i+1}: {col_info['name']}\n"
            
            # Add other information about the column
            for key, value in col_info.items():
                if key != 'name':
                    text += f"  {key}: {value}\n"
            
            text += "\n"
    
    # Analysis details
    text += "Analysis Details:\n"
    text += "-" * 20 + "\n"
    
    # Add analysis reasons
    analysis = analysis_result.get("analysis", {})
    
    if "table_description_reasons" in analysis:
        text += "Table Description Indicators:\n"
        for reason in analysis["table_description_reasons"]:
            text += f"  - {reason}\n"
        text += "\n"
    
    # Add LLM analysis if available
    llm_analysis = analysis_result.get("llm_analysis", {})
    if llm_analysis and "response" in llm_analysis:
        text += "LLM Analysis:\n"
        text += "-" * 20 + "\n"
        text += f"Type determined by LLM: {llm_analysis.get('type', 'UNKNOWN')}\n\n"
        text += "LLM Reasoning:\n"
        text += f"{llm_analysis['response']}\n\n"
    
    return text