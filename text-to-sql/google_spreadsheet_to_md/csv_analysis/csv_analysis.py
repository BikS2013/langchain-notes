"""
Module for core CSV analysis functions.
"""

from typing import Dict, Any, List, Tuple
import pandas as pd
from .column_analyzer import analyze_column_names

def check_table_description(df: pd.DataFrame) -> Tuple[List[int], List[str]]:
    """
    Check if the CSV looks like a table description/schema.
    
    Args:
        df: DataFrame containing the CSV data
        
    Returns:
        Tuple containing a list of scores and a list of reasons
    """
    scores = []
    reasons = []
    
    column_names = df.columns.tolist()
    
    # Check for column name column
    col_name_indicators = ['column', 'column_name', 'columnname', 'field', 'attribute', 'name']
    has_col_name = any(col.lower() in col_name_indicators or
                      any(ind in col.lower() for ind in col_name_indicators)
                      for col in column_names)
    scores.append(3 if has_col_name else 0)
    if has_col_name:
        reasons.append("Contains column that appears to list column names")
    
    # Check for data type column
    type_indicators = ['type', 'data_type', 'datatype', 'data type']
    has_type_col = any(col.lower() in type_indicators or
                      any(ind in col.lower() for ind in type_indicators)
                      for col in column_names)
    scores.append(3 if has_type_col else 0)
    if has_type_col:
        reasons.append("Contains column for data types")
    
    # Check for description column
    desc_indicators = ['description', 'desc', 'comment', 'notes', 'details']
    has_desc_col = any(col.lower() in desc_indicators or
                      any(ind in col.lower() for ind in desc_indicators)
                      for col in column_names)
    scores.append(2 if has_desc_col else 0)
    if has_desc_col:
        reasons.append("Contains column for field descriptions")
    
    # Check for key/constraint indicators
    key_indicators = ['key', 'primary', 'foreign', 'constraint', 'index', 'unique']
    has_key_col = any(col.lower() in key_indicators or
                     any(ind in col.lower() for ind in key_indicators)
                     for col in column_names)
    scores.append(2 if has_key_col else 0)
    if has_key_col:
        reasons.append("Contains column referencing keys or constraints")
    
    # Check if type column contains SQL data types
    if has_type_col:
        type_col = next((col for col in column_names
                       if col.lower() in type_indicators or
                       any(ind in col.lower() for ind in type_indicators)), None)
        if type_col:
            sql_types = ['int', 'varchar', 'char', 'text', 'date', 'datetime', 'timestamp',
                        'decimal', 'numeric', 'float', 'boolean', 'bool', 'string']
            type_values = df[type_col].astype(str).str.lower()
            has_sql_types = any(type_values.str.contains(t).any() for t in sql_types)
            scores.append(2 if has_sql_types else 0)
            if has_sql_types:
                reasons.append("Type column contains SQL data type values")
    
    # Check if rows look like column definitions
    if has_col_name:
        col_name_col = next((col for col in column_names
                           if col.lower() in col_name_indicators or
                           any(ind in col.lower() for ind in col_name_indicators)), None)
        if col_name_col:
            column_names_values = df[col_name_col].astype(str).str.strip()
            valid_column_names = column_names_values.str.match(r'^[a-zA-Z][a-zA-Z0-9_]*$').mean() > 0.5
            scores.append(3 if valid_column_names else 0)
            if valid_column_names:
                reasons.append("Rows contain values that look like valid column names")
    
    return scores, reasons

def check_database_description(df: pd.DataFrame) -> Tuple[List[int], List[str]]:
    """
    Check if the CSV looks like a database description.
    
    Args:
        df: DataFrame containing the CSV data
        
    Returns:
        Tuple containing a list of scores and a list of reasons
    """
    scores = []
    reasons = []
    
    column_names = df.columns.tolist()
    
    # Check for table name column
    table_name_indicators = ['table', 'table_name', 'tablename', 'name', 'entity']
    has_table_name_col = any(col.lower() in table_name_indicators or
                            any(ind in col.lower() for ind in table_name_indicators)
                            for col in column_names)
    scores.append(3 if has_table_name_col else 0)
    if has_table_name_col:
        reasons.append("Contains column that appears to list table names")
    
    # Check for description column
    desc_indicators = ['description', 'desc', 'comment', 'notes', 'details']
    has_desc_col = any(col.lower() in desc_indicators or
                      any(ind in col.lower() for ind in desc_indicators)
                      for col in column_names)
    scores.append(2 if has_desc_col else 0)
    if has_desc_col:
        reasons.append("Contains column for table descriptions")
    
    # Check for schema/database column
    schema_indicators = ['schema', 'database', 'db', 'catalog']
    has_schema_col = any(col.lower() in schema_indicators or
                        any(ind in col.lower() for ind in schema_indicators)
                        for col in column_names)
    scores.append(1 if has_schema_col else 0)
    if has_schema_col:
        reasons.append("Contains column referencing schema or database")
    
    # Check if rows look like table names
    if has_table_name_col:
        table_name_col = next((col for col in column_names
                             if col.lower() in table_name_indicators or
                             any(ind in col.lower() for ind in table_name_indicators)), None)
        if table_name_col:
            table_names = df[table_name_col].astype(str).str.strip()
            valid_table_names = table_names.str.match(r'^[a-zA-Z][a-zA-Z0-9_]*$').mean() > 0.7
            scores.append(2 if valid_table_names else 0)
            if valid_table_names:
                reasons.append("Rows contain values that look like valid table names")
    
    return scores, reasons

def check_sample_data(df: pd.DataFrame) -> Tuple[List[int], List[str]]:
    """
    Check if the CSV looks like sample data.
    
    Args:
        df: DataFrame containing the CSV data
        
    Returns:
        Tuple containing a list of scores and a list of reasons
    """
    scores = []
    reasons = []
    
    column_names = df.columns.tolist()
    
    # Check for high row count relative to column count
    row_to_col_ratio = len(df) / len(column_names) if len(column_names) > 0 else 0
    high_row_ratio = row_to_col_ratio > 5  # More than 5 rows per column suggests sample data
    scores.append(2 if high_row_ratio else 0)
    if high_row_ratio:
        reasons.append(f"High row-to-column ratio ({row_to_col_ratio:.1f}), suggesting sample data")
    
    # Check for absence of metadata columns
    metadata_indicators = ['column', 'type', 'description', 'key', 'constraint', 'table']
    has_metadata_cols = any(any(ind in col.lower() for ind in metadata_indicators)
                           for col in column_names)
    scores.append(2 if not has_metadata_cols else 0)
    if not has_metadata_cols:
        reasons.append("Column names don't appear to be metadata-related")
    
    # Check for numeric columns with varied values
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        varied_values = any(df[col].nunique() > 5 for col in numeric_cols)
        scores.append(2 if varied_values else 0)
        if varied_values:
            reasons.append("Contains numeric columns with varied values")
    
    # Check for date columns with varied values
    date_indicators = ['date', 'time', 'day', 'month', 'year']
    potential_date_cols = [col for col in column_names
                          if any(ind in col.lower() for ind in date_indicators)]
    if potential_date_cols:
        varied_dates = any(df[col].nunique() > 3 for col in potential_date_cols
                          if col in df.columns)
        scores.append(1 if varied_dates else 0)
        if varied_dates:
            reasons.append("Contains date-like columns with varied values")
    
    return scores, reasons

def analyze_structure(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze the structure of a CSV file to determine if it's a database description,
    table description, or sample data.
    
    Args:
        df: DataFrame containing the CSV data
        
    Returns:
        Dictionary containing analysis results
    """
    # Check for table description patterns
    table_description_indicators, table_description_reasons = check_table_description(df)
    
    # Check for database description patterns
    database_description_indicators, database_description_reasons = check_database_description(df)
    
    # Check for sample data patterns
    sample_data_indicators, sample_data_reasons = check_sample_data(df)
    
    return {
        "row_count": len(df),
        "column_count": len(df.columns),
        "column_names": df.columns.tolist(),
        "table_description_score": sum(table_description_indicators),
        "table_description_reasons": table_description_reasons,
        "database_description_score": sum(database_description_indicators),
        "database_description_reasons": database_description_reasons,
        "sample_data_score": sum(sample_data_indicators),
        "sample_data_reasons": sample_data_reasons
    }

def determine_likely_type(analysis: Dict[str, Any]) -> str:
    """
    Determine the most likely type based on analysis scores.
    
    Args:
        analysis: Dictionary containing analysis results
        
    Returns:
        String indicating the likely type
    """
    table_score = analysis.get("table_description_score", 0)
    db_score = analysis.get("database_description_score", 0)
    sample_score = analysis.get("sample_data_score", 0)
    
    if table_score > db_score and table_score > sample_score:
        return "TABLE_DESCRIPTION"
    elif db_score > table_score and db_score > sample_score:
        return "DATABASE_DESCRIPTION"
    elif sample_score > db_score and sample_score > table_score:
        return "SAMPLE_DATA"
    else:
        # If scores are tied or all low, make a best guess
        if max(db_score, table_score, sample_score) < 3:
            return "UNKNOWN"
        elif db_score == table_score and db_score > sample_score:
            return "DATABASE_OR_TABLE_DESCRIPTION"
        elif db_score == sample_score and db_score > table_score:
            return "DATABASE_DESCRIPTION_OR_SAMPLE_DATA"
        elif table_score == sample_score and table_score > db_score:
            return "TABLE_DESCRIPTION_OR_SAMPLE_DATA"
        else:
            return "UNKNOWN"