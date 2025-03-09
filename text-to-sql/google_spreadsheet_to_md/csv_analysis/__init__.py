"""
CSV Analysis package initialization.
"""

from .column_analyzer import analyze_column_names
from .file_operations import get_csv_files, save_analysis, read_csv_file, extract_table_info
from .csv_analysis import analyze_structure, determine_likely_type
from .llm_analyzer import analyze_with_llm
from .processors.file_processor import FileProcessor
from .processors.table_processor import process_table_description
from .processors.database_processor import process_database_description

__all__ = [
    'analyze_column_names',
    'get_csv_files',
    'save_analysis',
    'read_csv_file',
    'extract_table_info',
    'analyze_structure',
    'determine_likely_type',
    'analyze_with_llm',
    'FileProcessor',
    'process_table_description',
    'process_database_description'
]