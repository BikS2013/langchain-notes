#!/usr/bin/env python3
"""
Main script that coordinates the spreadsheet downloading and CSV analysis processes.
Takes a spreadsheet ID as input and organizes output files in a spreadsheet-specific directory.
"""

import os
import argparse
import logging
from typing import Dict, Any
from sheets import SheetProcessor
from sheets.config import Config
from table_analyzer import TableDescriptionAnalyzer
from analysis_to_markdown import process_analysis_files
from model_selector import ModelType, use_model

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_output_directory(spreadsheet_id: str) -> str:
    """
    Create and return the path to the spreadsheet-specific output directory.
    
    Args:
        spreadsheet_id: The ID of the Google Spreadsheet
        
    Returns:
        str: Path to the spreadsheet-specific output directory
    """
    output_dir = os.path.join('output', spreadsheet_id)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

from spreadsheets_downloader import process_spreadsheet

def download_spreadsheet(spreadsheet_id: str, output_dir: str) -> Dict[str, Any]:
    """
    Download and process the Google Spreadsheet.
    
    Args:
        spreadsheet_id: The ID of the Google Spreadsheet
        output_dir: Directory where CSV files will be saved
        
    Returns:
        Dict[str, Any]: Analysis results from the sheet processor
    """
    # Process spreadsheet with output directory
    logger.info("Processing Google Sheets data...")
    return process_spreadsheet(spreadsheet_id, output_dir=output_dir)

def analyze_csv_files(output_dir: str, use_llm: bool = True) -> None:
    """
    Analyze CSV files in the output directory.
    
    Args:
        output_dir: Directory containing CSV files to analyze
        use_llm: Whether to use LLM-based analysis
    """
    # Create chat model if LLM analysis is enabled
    chat_model = None
    if use_llm:
        # Use DeepSeek as default
        chat_model = use_model(
            model_type=ModelType.DEEPSEEK,
            temperature=0
        )

    # Initialize and run CSV analyzer
    analyzer = TableDescriptionAnalyzer(
        output_dir=output_dir,
        use_llm=use_llm,
        chat_model=chat_model
    )
    analyzer.process_all_files()

def generate_markdown_docs(output_dir: str) -> None:
    """
    Generate markdown documentation from analysis files.

    Args:
        output_dir: Directory containing analysis files to process
    """
    # Get the analysis directory
    analysis_dir = os.path.join(output_dir, 'analysis')
    if os.path.exists(analysis_dir):
        for json_file in os.listdir(analysis_dir):
            if not json_file.endswith('_analysis.json'):
                continue

            table_name = json_file.replace('_analysis.json', '')
            json_path = os.path.join(analysis_dir, json_file)
            text_path = os.path.join(output_dir, f'{table_name}_analysis.txt')

            process_analysis_files(json_path, text_path, output_dir)

def main():
    """Main function to orchestrate the downloading and analysis processes."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Download and analyze Google Spreadsheet data.')
    parser.add_argument('spreadsheet_id', help='The ID of the Google Spreadsheet to process')
    parser.add_argument('--no-llm', action='store_true', help='Disable LLM-based analysis')

    args = parser.parse_args()

    try:
        # Set up output directory for this spreadsheet
        output_dir = setup_output_directory(args.spreadsheet_id)
        logger.info(f"Output directory: {output_dir}")

        # Step 1: Download and process spreadsheet
        logger.info("\nStep 1: Downloading spreadsheet...")
        analyses = download_spreadsheet(args.spreadsheet_id, output_dir)

        # Step 2: Analyze generated CSV files
        logger.info("\nStep 2: Analyzing CSV files...")
        analyze_csv_files(output_dir, use_llm=not args.no_llm)

        # Step 3: Generate markdown documentation
        if not args.no_llm:
            logger.info("\nStep 3: Generating markdown documentation...")
            generate_markdown_docs(output_dir)
        else:
            logger.info("\nSkipping markdown generation (--no-llm flag used)")

        logger.info("\nProcessing completed successfully!")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()