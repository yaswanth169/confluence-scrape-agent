import logging
from typing import Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfluenceScraperError(Exception):
    """Base exception class for Confluence Scraper Agent errors."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)
        logger.error(f"{self.__class__.__name__}: {message}")
        if original_error:
            logger.error(f"Original error: {str(original_error)}")

class ConfigurationError(ConfluenceScraperError):
    """Exception raised for configuration-related errors."""
    pass

class ConnectionError(ConfluenceScraperError):
    """Exception raised for connection-related errors."""
    pass

class AuthenticationError(ConfluenceScraperError):
    """Exception raised for authentication failures."""
    pass

class ScraperError(ConfluenceScraperError):
    """Exception raised for errors during scraping operations."""
    pass

class QueryError(ConfluenceScraperError):
    """Exception raised for errors during query processing."""
    pass

class DocumentGenerationError(ConfluenceScraperError):
    """Exception raised for errors during document generation."""
    pass

class ModelLoadingError(ConfluenceScraperError):
    """Exception raised for errors during LLaMA model loading."""
    pass

def handle_error(error: Exception, context: str = "General operation") -> str:
    """Handle an exception and return a user-friendly error message."""
    if isinstance(error, ConfluenceScraperError):
        return f"Error in {context}: {str(error)}"
    else:
        logger.error(f"Unexpected error in {context}: {str(error)}")
        return f"Unexpected error in {context}: {str(error)}"
