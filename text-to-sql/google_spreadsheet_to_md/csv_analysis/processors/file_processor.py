"""
Module for coordinating file processing and analysis.
"""

import time
from typing import Dict, Any, Optional
import pandas as pd
from langchain.chat_models.base import BaseChatModel

from ..file_operations import get_csv_files, save_analysis, read_csv_file
from ..csv_analysis import analyze_structure, determine_likely_type
from ..llm_analyzer import analyze_with_llm
from .table_processor import process_table_description
from .database_processor import process_database_description

class FileProcessor:
    """Class for processing multiple CSV files and coordinating analysis."""
    
    def __init__(self,
                 output_dir: str,
                 use_llm: bool = True,
                 chat_model: Optional[BaseChatModel] = None):
        """
        Initialize the file processor.
        
        Args:
            output_dir: Directory containing CSV files to analyze
            use_llm: Whether to use LLM-based analysis
            chat_model: LangChain chat model (required if use_llm is True)
        """
        if use_llm and chat_model is None:
            raise ValueError("chat_model must be provided when use_llm is True")

        self.output_dir = output_dir
        self.use_llm = use_llm
        self.chat_model = chat_model

    def process_all_files(self) -> None:
        """Process all CSV files in the output directory."""
        csv_files = get_csv_files(self.output_dir)
        
        if not csv_files:
            print("No CSV files found in the output directory.")
            return
            
        print(f"Found {len(csv_files)} CSV files in the output directory.")
        
        tables_description_count = 0
        database_description_count = 0
        processed_count = 0
        skipped_count = 0
        error_count = 0
        
        start_time = time.time()
        
        for i, csv_file in enumerate(csv_files):
            print(f"\nProcessing {i+1}/{len(csv_files)}: {csv_file}...")
            
            try:
                # Analyze the CSV file
                analysis_result = self.analyze_csv(csv_file)
                file_type = self.determine_file_type(analysis_result)
                
                analysis_text = None
                
                # Process based on file type
                if file_type == "TABLE_DESCRIPTION":
                    print(f"{csv_file} is a Table Columns Description. Processing...")
                    tables_description_count += 1
                    df = read_csv_file(self.output_dir, csv_file)
                    analysis_text = process_table_description(df, csv_file, analysis_result)
                    
                elif file_type == "DATABASE_DESCRIPTION":
                    print(f"{csv_file} is a Database Description. Processing...")
                    database_description_count += 1
                    df = read_csv_file(self.output_dir, csv_file)
                    analysis_text = process_database_description(df, csv_file, analysis_result)
                    
                if analysis_text:
                    # Save the analysis
                    save_analysis(self.output_dir, csv_file, analysis_text)
                    processed_count += 1
                else:
                    print(f"Failed to process {csv_file}.")
                    error_count += 1
                    
                if file_type in ["SAMPLE_DATA", "OTHER"]:
                    print(f"{csv_file} is {file_type}. Skipping.")
                    skipped_count += 1
                    
            except Exception as e:
                print(f"Error processing {csv_file}: {str(e)}")
                error_count += 1
        
        elapsed_time = time.time() - start_time
        
        print(f"\nProcessing complete in {elapsed_time:.2f} seconds.")
        print(f"Found {tables_description_count} Table Columns Description files.")
        print(f"Found {database_description_count} Database Description files.")
        print(f"Successfully processed: {processed_count}")
        print(f"Skipped (Sample Data or Other): {skipped_count}")
        print(f"Errors: {error_count}")

    def analyze_csv(self, csv_filename: str) -> Dict[str, Any]:
        """
        Analyze a CSV file to determine its type.
        
        Args:
            csv_filename: Name of the CSV file to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Read the CSV file
            df = read_csv_file(self.output_dir, csv_filename)
            
            # Analyze the structure of the CSV file
            analysis_result = analyze_structure(df)
            
            # Determine likely type based on rule-based analysis
            likely_type = determine_likely_type(analysis_result)
            
            # Use LLM for additional analysis if enabled
            llm_analysis = {}
            if self.use_llm:
                try:
                    llm_analysis = analyze_with_llm(
                        df,
                        csv_filename,
                        self.chat_model
                    )
                    print(f"LLM analysis completed for {csv_filename}")
                except Exception as e:
                    print(f"Error in LLM analysis for {csv_filename}: {str(e)}")
                    llm_analysis = {"error": str(e)}
            
            return {
                "filename": csv_filename,
                "analysis": analysis_result,
                "likely_type": likely_type,
                "llm_analysis": llm_analysis
            }
        except Exception as e:
            print(f"Error analyzing {csv_filename}: {str(e)}")
            return {"error": str(e)}

    def determine_file_type(self, analysis_result: Dict[str, Any]) -> str:
        """
        Determine the type of CSV file based on LLM analysis results.
        Falls back to rule-based scoring only if LLM is uncertain.
        
        Args:
            analysis_result: Dictionary containing analysis results
            
        Returns:
            String indicating the file type
        """
        if "error" in analysis_result:
            return "OTHER"
        
        # Get LLM analysis and rule-based analysis
        llm_analysis = analysis_result.get("llm_analysis", {})
        rule_based_type = analysis_result.get("likely_type", "")
        analysis = analysis_result.get("analysis", {})
        table_score = analysis.get("table_description_score", 0)
        db_score = analysis.get("database_description_score", 0)
        
        # If LLM analysis is available, prioritize its decision
        if llm_analysis and "type" in llm_analysis:
            llm_type = llm_analysis.get("type", "")
            
            # If LLM confidently identifies the type
            if llm_type in ["TABLE_DESCRIPTION", "DATABASE_DESCRIPTION", "SAMPLE_DATA", "OTHER"]:
                print(f"LLM identified as {llm_type}")
                return llm_type
            
            # If LLM type is UNKNOWN or not clearly identified, it's uncertain
            print(f"LLM analysis uncertain, falling back to rule-based scoring")
        else:
            print(f"No LLM analysis available, using rule-based scoring")
        
        # Fall back to rule-based analysis only if LLM is uncertain or not available
        if "TABLE_DESCRIPTION" in rule_based_type:
            return "TABLE_DESCRIPTION"
        elif "DATABASE_DESCRIPTION" in rule_based_type:
            return "DATABASE_DESCRIPTION"
            
        # Check scores
        if table_score >= 5:  # If score is high enough, consider it a table description
            return "TABLE_DESCRIPTION"
        elif db_score >= 5:  # If score is high enough, consider it a database description
            return "DATABASE_DESCRIPTION"
            
        return "OTHER"