# Google Spreadsheet to Markdown Documentation Generator

This tool processes Google Spreadsheets containing database table descriptions and generates comprehensive markdown documentation through a multi-step automated workflow.

## Project Purpose

The project aims to:
1. Download and process Google Spreadsheets containing database table descriptions
2. Analyze the structure and content of these descriptions
3. Generate clear, well-structured markdown documentation for each database table
4. Handle multiple table formats and descriptions intelligently

## Workflow

The process consists of three main steps:

1. **Download & Process**: Downloads the Google Spreadsheet and converts each sheet to CSV format
2. **Analysis**: Analyzes each CSV file to determine its type and structure
3. **Documentation**: For table description files, generates comprehensive markdown documentation using AI

## Features

- **Intelligent File Type Detection**: Automatically identifies and processes only table description files
- **Smart Documentation Generation**: Uses AI to:
  - Understand column relationships and patterns
  - Generate meaningful descriptions even when not explicitly provided
  - Recognize and document related column groups
- **Organized Output**: All files are neatly organized in spreadsheet-specific directories

## Setup

1. Install dependencies:
```bash
poetry install
```

2. Create a `.env` file with your credentials:
```env
SPREADSHEET_ID=your_default_spreadsheet_id
OPENAI_API_KEY=your_openai_key  # If using OpenAI models
ANTHROPIC_API_KEY=your_anthropic_key  # If using Anthropic models
DEEPSEEK_API_KEY=your_deepseek_key  # If using Deepseek models

# Model Configuration (optional)
MODEL_TYPE=deepseek  # Options: openai, anthropic, deepseek
MODEL_NAME=deepseek-coder  # Model-specific name
MODEL_TEMPERATURE=0  # Temperature setting (0-1)
```

3. Place your Google Sheets credentials in `credentials.json`

## Usage

Process a spreadsheet and generate documentation:

```bash
# Basic usage - downloads, analyzes, and generates documentation
poetry run python main.py your_spreadsheet_id

# Skip LLM-based analysis and documentation
poetry run python main.py your_spreadsheet_id --no-llm
```

### Output Structure

All files are organized under `output/{spreadsheet_id}/`:
```
output/
└── spreadsheet_id/
    ├── table1.csv              # Downloaded CSV files
    ├── table1_analysis.txt     # Analysis results
    ├── table1_analysis.json    # Structured analysis data
    ├── table1.md              # Generated markdown documentation
    └── analysis/              # Additional analysis data
```

### Generated Documentation

For each table description file, the tool generates a markdown document containing:
1. Database name as the main heading
2. Table name as a subheading
3. A comprehensive table of columns including:
   - Column Name: As used in the database
   - Column Type: The data type
   - Column Description: Clear explanation of the column's purpose

### Options

- `spreadsheet_id`: (Required) The ID of the Google Spreadsheet to process
- `--no-llm`: Disable LLM-based analysis and documentation generation

Model configuration (temperature, model type, etc.) is handled through environment variables. See the Environment Variables section above.