import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Azure Search Configuration
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
AZURE_SEARCH_INDEX_NAME = "athena-sp-latest-docs-index" #"athena-sp-docs" # "athena-index"#
AZURE_SEARCH_API_VERSION = "2023-11-01"


# Azure OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

# Document Processing Configuration
CHUNK_SIZE = 3000
CHUNK_OVERLAP = 500

# Logging Configuration
LOG_FILE = os.path.join(os.path.dirname(__file__), 'logs', 'azure_search.log')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = 'INFO'

# Create logs directory if it doesn't exist
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)