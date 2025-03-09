"""
Module for analyzing CSV column names and structures.
"""

from typing import Dict, List

def analyze_column_names(columns: List[str]) -> Dict[str, str]:
    """
    Analyze column names to determine their likely types and purposes.
    
    Args:
        columns: List of column names
        
    Returns:
        Dictionary mapping column names to their likely types
    """
    # Common indicators for different types of columns
    metadata_indicators = {
        'description': 'Metadata - Description field',
        'type': 'Metadata - Data type field',
        'column': 'Metadata - Column name field',
        'key': 'Metadata - Key/constraint field',
        'constraint': 'Metadata - Key/constraint field',
        'comment': 'Metadata - Description field',
        'table': 'Metadata - Table information field',
        'database': 'Metadata - Database information field',
        'schema': 'Metadata - Schema information field',
        'field': 'Metadata - Column name field',
        'attribute': 'Metadata - Column name field',
        'datatype': 'Metadata - Data type field',
        'nullable': 'Metadata - Constraint field',
        'primary': 'Metadata - Key field',
        'foreign': 'Metadata - Key field',
        'index': 'Metadata - Index field',
        'partition': 'Metadata - Table property field',
        'source': 'Metadata - Source information field',
        'production': 'Metadata - Environment field',
        'flow': 'Metadata - Process field',
        'pending': 'Metadata - Status field'
    }
    
    # Common indicators for data/content columns
    data_indicators = {
        'id': 'Data - Identifier field',
        'date': 'Data - Temporal field',
        'time': 'Data - Temporal field',
        'name': 'Data - Label field',
        'code': 'Data - Code field',
        'value': 'Data - Value field',
        'amount': 'Data - Numeric field',
        'status': 'Data - Status field',
        'count': 'Data - Numeric field',
        'total': 'Data - Numeric field',
        'price': 'Data - Numeric field',
        'cost': 'Data - Numeric field'
    }
    
    result = {}
    
    for col in columns:
        col_lower = col.lower()
        
        # First check for metadata indicators
        metadata_match = False
        for indicator, type_desc in metadata_indicators.items():
            if indicator in col_lower:
                result[col] = type_desc
                metadata_match = True
                break
        
        # If not metadata, check for data indicators
        if not metadata_match:
            data_match = False
            for indicator, type_desc in data_indicators.items():
                if indicator in col_lower:
                    result[col] = type_desc
                    data_match = True
                    break
            
            # If neither metadata nor data, mark as unknown
            if not data_match:
                result[col] = 'Unknown purpose'
    
    return result