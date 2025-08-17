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
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', '4000'))
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))
    TOP_P = float(os.getenv('TOP_P', '0.9'))
    
    # Confluence Scraping Configuration
    MAX_PAGES_PER_SPACE = int(os.getenv('MAX_PAGES_PER_SPACE', '100'))
    INCLUDE_ATTACHMENTS = os.getenv('INCLUDE_ATTACHMENTS', 'True').lower() == 'true'
    INCLUDE_COMMENTS = os.getenv('INCLUDE_COMMENTS', 'False').lower() == 'true'
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that all required configuration is present and correct."""
        required_vars = [
            ('CONFLUENCE_URL', cls.CONFLUENCE_URL),
            ('CONFLUENCE_USERNAME', cls.CONFLUENCE_USERNAME), 
            ('CONFLUENCE_API_TOKEN', cls.CONFLUENCE_API_TOKEN),
            ('LLAMA_MODEL_PATH', cls.LLAMA_MODEL_PATH)
        ]
        
        missing_vars = []
        invalid_vars = []
        
        for var_name, var_value in required_vars:
            if not var_value or var_value.startswith('your-'):
                missing_vars.append(var_name)
            elif var_name == 'CONFLUENCE_URL' and not var_value.startswith(('http://', 'https://')):
                invalid_vars.append(f"{var_name}: Must be a valid URL starting with http:// or https://")
            elif var_name == 'CONFLUENCE_USERNAME' and '@' not in var_value:
                invalid_vars.append(f"{var_name}: Must be a valid email address")
            elif var_name == 'LLAMA_MODEL_PATH' and not os.path.exists(var_value):
                invalid_vars.append(f"{var_name}: Path does not exist")
        
        # Validate numeric values
        if cls.MAX_TOKENS <= 0:
            invalid_vars.append("MAX_TOKENS: Must be greater than 0")
        if not (0 <= cls.TEMPERATURE <= 1):
            invalid_vars.append("TEMPERATURE: Must be between 0 and 1")
        if not (0 <= cls.TOP_P <= 1):
            invalid_vars.append("TOP_P: Must be between 0 and 1")
        if cls.MAX_PAGES_PER_SPACE <= 0:
            invalid_vars.append("MAX_PAGES_PER_SPACE: Must be greater than 0")
        
        if missing_vars or invalid_vars:
            error_messages = []
            if missing_vars:
                error_messages.append(f"Missing required configuration: {', '.join(missing_vars)}")
            if invalid_vars:
                error_messages.append(f"Invalid configuration values: {'; '.join(invalid_vars)}")
            raise ValueError("Configuration errors: " + "; ".join(error_messages))
        
        # Ensure output directories exist
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
        os.makedirs(cls.TEMP_DIR, exist_ok=True)
        
        return True
