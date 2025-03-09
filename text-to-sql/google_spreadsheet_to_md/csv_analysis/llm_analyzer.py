"""
Module for LLM-based CSV analysis functionality.
"""

from typing import Dict, Any
import pandas as pd
from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models.base import BaseChatModel
from .column_analyzer import analyze_column_names
from .csv_analysis import analyze_structure

def analyze_with_llm(
    df: pd.DataFrame,
    csv_filename: str,
    chat_model: BaseChatModel
) -> Dict[str, Any]:
    """
    Use an LLM to analyze the CSV file and determine its type.
    
    Args:
        df: DataFrame containing the CSV data
        csv_filename: Name of the CSV file
        chat_model: LangChain chat model to use for analysis
            
    Returns:
        Dictionary containing LLM analysis results
    """
    # First run rule-based analysis
    analysis_result = analyze_structure(df)
    table_score = analysis_result.get("table_description_score", 0)
    db_score = analysis_result.get("database_description_score", 0)
    sample_score = analysis_result.get("sample_data_score", 0)
    
    # Get analysis reasons
    table_reasons = analysis_result.get("table_description_reasons", [])
    db_reasons = analysis_result.get("database_description_reasons", [])
    sample_reasons = analysis_result.get("sample_data_reasons", [])
    
    # Prepare a sample of the CSV data for the LLM
    sample_rows = min(10, len(df))
    sample_df = df.head(sample_rows)
    
    # Convert sample to string representation
    sample_str = sample_df.to_string()
    
    # Format the analysis scores and reasons
    analysis_summary = f"""
    Programmatic Analysis Results:
    1. Table Description Score: {table_score}
       Reasons:
       {chr(10).join(f'   - {reason}' for reason in table_reasons)}
    
    2. Database Description Score: {db_score}
       Reasons:
       {chr(10).join(f'   - {reason}' for reason in db_reasons)}
    
    3. Sample Data Score: {sample_score}
       Reasons:
       {chr(10).join(f'   - {reason}' for reason in sample_reasons)}
    """
    
    # Format column names analysis
    column_name_analysis = analyze_column_names(df.columns)
    
    # Additional metadata about the file
    file_metadata = f"""
    File Statistics:
    - Total number of rows: {len(df)}
    - Total number of columns: {len(df.columns)}
    - Number of unique values in first column: {df[df.columns[0]].nunique() if len(df.columns) > 0 else 0}

    Column Headers Analysis:
    - Headers: {', '.join(df.columns)}
    - Header Types:
      {chr(10).join(f"  - {col}: {col_type}" for col, col_type in column_name_analysis.items())}
    """
    
    # Count metadata and data columns
    column_types = analyze_column_names(df.columns)
    metadata_count = sum(1 for t in column_types.values() if t.startswith('Metadata'))
    data_count = sum(1 for t in column_types.values() if t.startswith('Data'))
    
    # Prepare the prompt for the LLM
    prompt = f"""
    Analyze the following CSV file and determine what it describes. The CSV file is named '{csv_filename}'.
    
    CSV Sample (first {sample_rows} rows):
    {sample_str}

    {file_metadata}

    Here is the programmatic analysis of the file structure:
    {analysis_summary}
    
    Column Header Analysis:
    - Total rows in CSV: {len(df)}
    - Total columns: {len(df.columns)}
    - Metadata-related columns: {metadata_count}
    - Data-related columns: {data_count}
    - Unknown purpose columns: {len(df.columns) - metadata_count - data_count}
    
    Important indicators:
    1. High proportion of metadata columns ({metadata_count}/{len(df.columns)}) suggests this might be a description/documentation file
    2. High proportion of data columns ({data_count}/{len(df.columns)}) suggests this might be actual data records
    3. Total number of rows ({len(df)}) - fewer rows often indicate metadata/description files, more rows suggest actual data records
    
    Key characteristics to consider:
    1. Table Description files:
       - Each ROW describes a COLUMN in a database table
       - Usually have relatively few rows (one per table column)
       - Column headers are mostly metadata-related ('column_name', 'type', 'description', etc.)
       - Content is metadata about table structure
       - Example headers: 'column', 'field', 'type', 'description', 'constraints', etc.
    
    2. Database Description files:
       - Each ROW describes a TABLE in a database
       - Column headers describe table-level properties
       - Usually have metadata-related headers but focused on tables rather than columns
       - Example headers: 'table_name', 'schema', 'partition', 'source', 'production_flow', etc.
    
    3. Sample/Reference Data files:
       - Each ROW is an actual data record
       - Often have many rows of similar data
       - Column headers represent business attributes
       - Content is actual business data, not metadata
       - Example headers: 'id', 'name', 'date', 'amount', 'status', etc.
    
    Given the file's characteristics, especially its column headers, determine if this CSV is one of:
    1. TABLE_DESCRIPTION: Column headers focus on column-level properties
    2. DATABASE_DESCRIPTION: Column headers focus on table-level properties
    3. SAMPLE_DATA: Column headers represent business data attributes
    4. OTHER: None of the above patterns match
    
    Explain your reasoning thoroughly, addressing:
    1. The significance of the column headers and their types
    2. The file's structure and content patterns
    3. Agreement or disagreement with the programmatic analysis
    4. Whether the rows represent metadata (about columns/tables) or actual data records
    
    Then conclude with a final determination of the CSV type.
    """
    
    # Format messages for langchain
    messages = [
        SystemMessage(content="You are an expert data analyst specializing in database structures."),
        HumanMessage(content=prompt)
    ]
    
    # Get response from the model
    response = chat_model.invoke(messages)
    
    # Extract the LLM's response
    llm_response = response.content.strip()
    
    # Determine the type based on the LLM's response
    llm_type = "UNKNOWN"
    if "TABLE_DESCRIPTION" in llm_response.upper():
        llm_type = "TABLE_DESCRIPTION"
    elif "DATABASE_DESCRIPTION" in llm_response.upper():
        llm_type = "DATABASE_DESCRIPTION"
    elif "SAMPLE_DATA" in llm_response.upper():
        llm_type = "SAMPLE_DATA"
    elif "OTHER" in llm_response.upper():
        llm_type = "OTHER"
    
    return {
        "response": llm_response,
        "type": llm_type
    }