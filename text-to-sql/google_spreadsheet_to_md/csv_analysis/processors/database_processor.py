"""
Module for processing database description files.
"""

from typing import Dict, Any, Optional
import pandas as pd

def process_database_description(
    df: pd.DataFrame, 
    csv_filename: str, 
    analysis_result: Dict[str, Any]
) -> Optional[str]:
    """
    Process a database description CSV file and generate analysis text.
    
    Args:
        df: DataFrame containing the CSV data
        csv_filename: Name of the CSV file
        analysis_result: Dictionary containing analysis results
        
    Returns:
        Analysis text or None if processing failed
    """
    try:
        # Generate analysis text
        analysis_text = f"Analysis of {csv_filename}\n"
        analysis_text += "=" * (len(analysis_text) - 1) + "\n\n"
        
        # Basic file information
        analysis_text += f"File Type: Database Description\n"
        analysis_text += f"Number of Columns in CSV: {len(df.columns)}\n"
        analysis_text += f"Number of Rows in CSV: {len(df)}\n\n"
        
        # Explanation of database description structure
        analysis_text += generate_database_structure_explanation(
            df, analysis_result
        )
        
        return analysis_text
        
    except Exception as e:
        print(f"Error processing {csv_filename}: {str(e)}")
        return None

def generate_database_structure_explanation(
    df: pd.DataFrame,
    analysis_result: Dict[str, Any]
) -> str:
    """
    Generate the explanation text for database structure.
    
    Args:
        df: DataFrame containing the CSV data
        analysis_result: Dictionary containing analysis results
        
    Returns:
        Formatted explanation text
    """
    text = "Structure Explanation:\n"
    text += "-" * 20 + "\n"
    text += "This is a Database Description file where:\n"
    text += "- Each ROW describes a TABLE in the database\n"
    text += "- Each COLUMN describes table-level properties\n"
    text += "- The CSV column headers indicate what information is provided about each table\n\n"
    
    # CSV Column Headers
    text += "CSV Column Headers (Information Types):\n"
    text += "-" * 20 + "\n"
    for col in df.columns:
        text += f"- {col}\n"
    text += "\n"
    
    # Tables Information
    text += "Tables Information:\n"
    text += "-" * 20 + "\n"
    
    # Find table name column
    table_name_indicators = ['table', 'table_name', 'tablename', 'big_data_table']
    table_name_col = next(
        (col for col in df.columns if any(ind in col.lower() for ind in table_name_indicators)),
        df.columns[0]  # Fallback to first column if no obvious table name column
    )
    
    # Process each table
    for i, row in df.iterrows():
        table_name = row[table_name_col]
        text += f"Table {i+1}: {table_name}\n"
        
        # Add other information about the table
        for col in df.columns:
            if col != table_name_col and pd.notna(row[col]):
                text += f"  {col}: {row[col]}\n"
        
        text += "\n"
    
    # Analysis details
    text += "Analysis Details:\n"
    text += "-" * 20 + "\n"
    
    # Add analysis reasons
    analysis = analysis_result.get("analysis", {})
    
    if "database_description_reasons" in analysis:
        text += "Database Description Indicators:\n"
        for reason in analysis["database_description_reasons"]:
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