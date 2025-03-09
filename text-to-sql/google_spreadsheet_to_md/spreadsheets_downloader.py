import logging
from sheets import SheetProcessor
from sheets.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
def process_spreadsheet(spreadsheet_id: str, output_dir: str = 'output') -> dict:
    """
    Process Google Sheets data for a given spreadsheet.

    Args:
        spreadsheet_id: The ID of the Google Spreadsheet to process
        output_dir: Directory where CSV files will be saved, defaults to 'output'
    Returns:
        dict: Analysis results for all sheets
    """
    try:
        # Initialize processor with configuration
        config = Config(spreadsheet_id=spreadsheet_id)
        config.update(output_dir=output_dir)
        processor = SheetProcessor(config)
        
        # Process spreadsheet and get analyses
        logger.info("Processing Google Sheets data...")
        analyses = processor.process_spreadsheet()
        
        # Display summary
        logger.info("\nProcessing Summary:")
        for sheet_name, analysis in analyses.items():
            logger.info(f"\nSheet: {sheet_name}")
            logger.info(f"Rows: {analysis['row_count']}")
            logger.info(f"Columns: {analysis['column_count']}")
            logger.info("Column Types:")
            for col, details in analysis['columns'].items():
                logger.info(f"  - {col}: {details['type']}")
        
        logger.info("\nProcess completed successfully!")
        return analyses
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise