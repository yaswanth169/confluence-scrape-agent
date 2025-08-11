import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the Confluence scraper agent system."""
    
    # Confluence Configuration
    CONFLUENCE_URL = os.getenv('CONFLUENCE_URL', 'https://your-domain.atlassian.net')
    CONFLUENCE_USERNAME = os.getenv('CONFLUENCE_USERNAME', 'your-email@barclays.com')
    CONFLUENCE_API_TOKEN = os.getenv('CONFLUENCE_API_TOKEN', 'your-api-token')
    
    # LLaMA Model Configuration
    LLAMA_MODEL_PATH = os.getenv('LLAMA_MODEL_PATH', 'C:/devhome/projects/meta-llama-Llama-3-2-1B-Instruct/meta-llama-Llama-3-2-1B-Instruct')
    
    # Output Configuration
    OUTPUT_DIR = os.getenv('OUTPUT_DIR', './output')
    TEMP_DIR = os.getenv('TEMP_DIR', './temp')
    
    # Agent Configuration
    MAX_TOKENS = 4000
    TEMPERATURE = 0.7
    TOP_P = 0.9
    
    # Confluence Scraping Configuration
    MAX_PAGES_PER_SPACE = 100
    INCLUDE_ATTACHMENTS = True
    INCLUDE_COMMENTS = False
    
    @classmethod
    def validate(cls):
        """Validate that all required configuration is present."""
        required_vars = [
            'CONFLUENCE_URL',
            'CONFLUENCE_USERNAME', 
            'CONFLUENCE_API_TOKEN'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var) or getattr(cls, var).startswith('your-'):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required configuration: {', '.join(missing_vars)}")
        
        return True
