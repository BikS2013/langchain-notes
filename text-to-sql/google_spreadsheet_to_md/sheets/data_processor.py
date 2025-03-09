import pandas as pd
import numpy as np
import logging
import re
from typing import List, Dict, Any, Union

logger = logging.getLogger(__name__)

class SheetDataProcessor:
    """Handles processing of Google Sheets data."""
    
    def __init__(self):
        self.processed_sheets: Dict[str, pd.DataFrame] = {}
        self._date_format_cache: Dict[str, str] = {}  # Cache detected date formats
    
    def process_sheet_values(self, values: List[List[str]], sheet_name: str) -> pd.DataFrame:
        """
        Process sheet values into a DataFrame, handling varying column counts.
        
        Args:
            values (List[List[str]]): Raw values from the sheet
            sheet_name (str): Name of the sheet for logging
            
        Returns:
            pd.DataFrame: Processed DataFrame
        """
        if not values:
            logger.warning(f"No data found in sheet: {sheet_name}")
            return pd.DataFrame()
            
        # Find first non-empty row to use as header
        header_row_index = 0
        for i, row in enumerate(values):
            # Check if row has any non-empty values
            if any(str(cell).strip() for cell in row):
                header_row_index = i
                if i > 0:
                    logger.info(f"Skipped {i} empty rows at the start of sheet: {sheet_name}")
                break
        
        # Get header from first non-empty row
        header = [str(col).strip() for col in values[header_row_index]]
        data_rows = values[header_row_index + 1:]
        
        # Remove empty rows from data
        original_row_count = len(data_rows)
        data_rows = [
            row for row in data_rows
            if any(str(cell).strip() for cell in row)
        ]
        removed_rows = original_row_count - len(data_rows)
        
        if removed_rows > 0:
            logger.info(f"Removed {removed_rows} empty rows from data section in sheet: {sheet_name}")
        
        if not data_rows:
            logger.warning(f"No data rows found in sheet: {sheet_name} after removing empty rows")
            return pd.DataFrame()
        
        # Find the maximum number of columns
        data_cols = max(len(row) for row in data_rows) if data_rows else len(header)
        header_cols = len(header)
        max_cols = max(data_cols, header_cols)
        
        # Clean and standardize column headers
        cleaned_header = []
        seen_headers = set()
        for i, col in enumerate(header):
            # Create a base name, either from the column or a generic name
            if not col or col.isspace():
                base_name = f'column{i+1}'
            else:
                base_name = self.clean_column_name(col, sheet_name)
            
            # Ensure uniqueness by adding a number if needed
            final_name = base_name
            counter = 1
            while final_name in seen_headers:
                final_name = f"{base_name}_{counter}"
                counter += 1
            seen_headers.add(final_name)
            cleaned_header.append(final_name)
        
        # Handle missing column headers
        if max_cols > header_cols:
            for i in range(header_cols, max_cols):
                base_name = f'column{i+1}'
                final_name = base_name
                counter = 1
                while final_name in seen_headers:
                    final_name = f"{base_name}_{counter}"
                    counter += 1
                seen_headers.add(final_name)
                cleaned_header.append(final_name)
            logger.info(f"Added {max_cols - header_cols} column headers to sheet '{sheet_name}'")
        
        # Pad and clean data rows
        padded_data = []
        for row in data_rows:
            # Convert all values to strings and strip whitespace
            cleaned_row = [str(val).strip() if val is not None else '' for val in row]
            # Pad with empty strings if needed
            padded_row = cleaned_row + [''] * (max_cols - len(cleaned_row))
            padded_data.append(padded_row)
        
        df = pd.DataFrame(padded_data, columns=cleaned_header)
        self.processed_sheets[sheet_name] = df
        
        # Try to convert numeric columns
        # Try to infer better column names from data
        for col in df.columns:
            sample_values = df[col].dropna().head(10).tolist()
            better_name = self._guess_column_name(sample_values, col)
            if better_name != col:
                df = df.rename(columns={col: better_name})

        # Try to convert columns to appropriate types
        for col in df.columns:
            values = df[col].dropna()
            if len(values) == 0:
                continue

            # Try numeric conversion first
            try:
                numeric_series = pd.to_numeric(df[col], errors='coerce')
                if numeric_series.notna().sum() / len(numeric_series) > 0.9:  # 90% success rate
                    df[col] = numeric_series
                    continue
            except (ValueError, TypeError):
                pass

            # Try date conversion
            try:
                # Get non-empty values
                sample = values.astype(str).str.strip()
                sample = sample[sample != '']
                
                if len(sample) > 0:
                    # Check cache first
                    cached_format = self._date_format_cache.get(col)
                    if cached_format:
                        try:
                            df[col] = pd.to_datetime(df[col], format=cached_format,
                                                   dayfirst='%d' in cached_format,
                                                   errors='coerce')
                            if df[col].notna().sum() / len(df[col]) >= 0.8:
                                continue
                        except Exception:
                            pass

                    # Define common date formats with regular expressions
                    formats = {
                        # ISO formats
                        '%Y-%m-%d': r'^\d{4}-\d{2}-\d{2}$',
                        '%Y-%m-%d %H:%M:%S': r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$',
                        # Greek/European formats
                        '%d/%m/%Y': r'^\d{1,2}/\d{1,2}/\d{4}$',
                        '%d-%m-%Y': r'^\d{1,2}-\d{1,2}-\d{4}$',
                        '%d.%m.%Y': r'^\d{1,2}\.\d{1,2}\.\d{4}$',
                        # With time
                        '%d/%m/%Y %H:%M': r'^\d{1,2}/\d{1,2}/\d{4} \d{2}:\d{2}$',
                        '%d/%m/%Y %H:%M:%S': r'^\d{1,2}/\d{1,2}/\d{4} \d{2}:\d{2}:\d{2}$',
                        # Additional Greek formats
                        '%d-%m-%Y %H:%M': r'^\d{1,2}-\d{1,2}-\d{4} \d{2}:\d{2}$',
                        '%d.%m.%Y %H:%M': r'^\d{1,2}\.\d{1,2}\.\d{4} \d{2}:\d{2}$'
                    }
                    
                    # Try to identify the most common format
                    format_counts = {fmt: sum(1 for val in sample if re.match(pattern, val))
                                  for fmt, pattern in formats.items()}
                    
                    # Only attempt date parsing if column name or content suggests dates
                    date_indicators = ['date', 'dt', 'timestamp', 'time', 'ημερομηνία', 'χρόνος']
                    col_suggests_date = any(ind in col.lower() for ind in date_indicators)
                    
                    # Check if values look like dates (at least 3 numbers separated by delimiters)
                    sample_suggests_date = any(
                        len(re.findall(r'\d+', str(val))) >= 3 and
                        any(d in str(val) for d in ['/', '-', '.'])
                        for val in sample[:5] if pd.notna(val)
                    )
                    
                    if col_suggests_date or sample_suggests_date:
                        # Get the format that matches most values
                        best_format = None
                        max_matches = 0
                        for fmt, count in format_counts.items():
                            if count > max_matches and count / len(sample) >= 0.9:  # Increased threshold
                                max_matches = count
                                best_format = fmt
                        
                        if best_format:
                            # Use the detected format
                            df[col] = pd.to_datetime(df[col], format=best_format,
                                                   dayfirst='%d' in best_format,
                                                   errors='coerce')
                            # Cache the successful format
                            if df[col].notna().sum() / len(df[col]) >= 0.9:
                                self._date_format_cache[col] = best_format
                                continue
                    
                    # If we reach here, either:
                    # 1. Column doesn't look like dates
                    # 2. No consistent format found
                    # 3. Too many parsing errors
                    df[col] = values  # Keep original values
            except Exception:
                pass
        
        logger.info(f"Successfully processed sheet '{sheet_name}' with {len(df.columns)} columns")
        return df
    
    def _guess_column_name(self, values: List[str], original_name: str) -> str:
        """Try to guess a meaningful column name from its values."""
        if len(original_name) > 1 and not original_name.startswith('column'):
            return original_name

        sample_values = [str(v).strip() for v in values if str(v).strip()][:5]
        if not sample_values:
            return original_name

        # Check for dates
        if all(self._try_parse_date(v) for v in sample_values):
            return 'date'

        # Check for numeric values
        if all(str(v).replace('.', '').isdigit() for v in sample_values):
            return 'amount' if any('.' in str(v) for v in sample_values) else 'number'

        return original_name

    def clean_column_name(self, name: str, sheet_name: str) -> str:
        """Clean column name to be more readable."""
        # Convert to string and clean whitespace
        name = str(name).strip()
        
        # Remove sheet name prefix if it exists
        name = name.replace(f"{sheet_name}_Column", "")
        
        # Replace spaces with underscores
        name = re.sub(r'\s+', '_', name)
        
        # Remove any characters that aren't letters, numbers, underscores, or Greek letters
        name = re.sub(r'[^\w\u0370-\u03FF_]', '', name)
        
        # Remove repeated underscores
        name = re.sub(r'_+', '_', name)
        
        # Remove trailing underscores
        name = name.strip('_')
        
        # Ensure we have a valid name
        if not name:
            name = "column"
        
        return name

    def _try_parse_date(self, value: str) -> bool:
        """Try to parse a string as a date."""
        date_formats = [
            '%Y-%m-%d', '%d/%m/%Y', '%d.%m.%Y',
            '%Y/%m/%d', '%d-%m-%Y', '%m/%d/%Y',
            '%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S',
            '%d.%m.%Y %H:%M:%S'
        ]
        
        for fmt in date_formats:
            try:
                pd.to_datetime(str(value), format=fmt)
                return True
            except (ValueError, TypeError):
                continue
        return False

    def infer_column_types(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Infer data types for each column in the DataFrame.
        
        Args:
            df (pd.DataFrame): The DataFrame to analyze
            
        Returns:
            Dict[str, str]: Column names mapped to their inferred types
        """
        column_types = {}
        
        for column in df.columns:
            series = df[column].dropna()
            total_values = len(series)
            if total_values == 0:
                column_types[column] = 'string'
                continue

            # Convert series to strings for analysis
            str_series = series.astype(str).str.strip()
            
            # Check column name for hints
            col_lower = column.lower()
            
            # Identify specific column types by name
            if any(hint in col_lower for hint in ['id', 'code', 'κωδικός']):
                column_types[column] = 'identifier'
                continue
            elif any(hint in col_lower for hint in ['date', 'dt', 'ημερομηνία', 'χρόνος']):
                column_types[column] = 'datetime'
                continue
            elif any(hint in col_lower for hint in ['amount', 'price', 'cost', 'ποσό', 'τιμή', 'κόστος']):
                column_types[column] = 'decimal'
                continue
            
            # Try to infer type from values
            numeric_series = pd.to_numeric(series, errors='coerce')
            numeric_count = numeric_series.notna().sum()
            
            # Check for dates first
            date_count = sum(1 for val in str_series if self._try_parse_date(val))
            if date_count / total_values > 0.8:  # 80% threshold
                column_types[column] = 'datetime'
                continue
                
            # Check for numeric values
            if numeric_count / total_values > 0.8:  # 80% threshold
                if all(numeric_series[numeric_series.notna()] % 1 == 0):
                    column_types[column] = 'integer'
                else:
                    column_types[column] = 'decimal'
                continue
            
            # Check for boolean values (including Greek)
            bool_values = {'true', 'false', 't', 'f', 'yes', 'no', 'y', 'n', '1', '0',
                         'ναι', 'οχι', 'όχι', 'σωστό', 'λάθος', 'σ', 'λ'}
            series_lower = str_series.str.lower()
            if set(series_lower.unique()).issubset(bool_values):
                column_types[column] = 'boolean'
                continue
            
            # Check for specific value patterns
            if str_series.str.match(r'^[A-Z0-9-_]+$').all():
                column_types[column] = 'code'
            else:
                column_types[column] = 'string'
            
        return column_types
    
    def _convert_to_python_native(self, value: Any) -> Union[int, float, str, None]:
        """Convert numpy/pandas types to Python native types."""
        if isinstance(value, (np.integer, pd.Int64Dtype)):
            return int(value)
        elif isinstance(value, (np.floating, pd.Float64Dtype)):
            return float(value)
        elif isinstance(value, (np.bool_, pd.BooleanDtype)):
            return bool(value)
        elif pd.isna(value):
            return None
        return str(value)

    def analyze_sheet_data(self, sheet_name: str) -> Dict[str, Any]:
        """
        Analyze the data in a processed sheet.
        
        Args:
            sheet_name (str): Name of the sheet to analyze
            
        Returns:
            Dict[str, Any]: Analysis results including column types and stats
        """
        if sheet_name not in self.processed_sheets:
            raise KeyError(f"Sheet '{sheet_name}' not found in processed sheets")
            
        df = self.processed_sheets[sheet_name]
        column_types = self.infer_column_types(df)
        
        analysis = {
            'sheet_name': sheet_name,
            'row_count': int(len(df)),  # Convert np.int64 to int
            'column_count': int(len(df.columns)),  # Convert np.int64 to int
            'columns': {}
        }
        
        for col in df.columns:
            unique_values = len(df[col].unique())
            null_count = int(df[col].isna().sum())  # Convert np.int64 to int
            sample_values = [
                self._convert_to_python_native(val)
                for val in df[col].dropna().head(5)
            ]
            
            analysis['columns'][col] = {
                'type': column_types[col],
                'unique_values': int(unique_values),  # Convert np.int64 to int
                'null_count': null_count,
                'sample_values': sample_values
            }
        
        return analysis