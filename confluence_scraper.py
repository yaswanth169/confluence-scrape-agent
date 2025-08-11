import os
import json
import requests
from bs4 import BeautifulSoup
from atlassian import Confluence
from typing import Dict, List, Optional, Any
import logging
from config import Config
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfluenceScraper:
    """Confluence scraper utility for extracting data from Confluence pages."""
    
    def __init__(self):
        """Initialize the Confluence scraper with configuration."""
        self.config = Config()
        self.confluence = None
        self._connect()
    
    def _connect(self):
        """Establish connection to Confluence."""
        try:
            self.confluence = Confluence(
                url=self.config.CONFLUENCE_URL,
                username=self.config.CONFLUENCE_USERNAME,
                password=self.config.CONFLUENCE_API_TOKEN,
                cloud=True
            )
            logger.info("Successfully connected to Confluence")
        except Exception as e:
            logger.error(f"Failed to connect to Confluence: {e}")
            raise
    
    def get_spaces(self) -> List[Dict[str, Any]]:
        """Get all accessible spaces."""
        try:
            spaces = self.confluence.get_all_spaces()
            logger.info(f"Found {len(spaces)} spaces")
            return spaces
        except Exception as e:
            logger.error(f"Failed to get spaces: {e}")
            return []
    
    def get_pages_in_space(self, space_key: str, limit: int = None) -> List[Dict[str, Any]]:
        """Get all pages in a specific space."""
        try:
            limit = limit or self.config.MAX_PAGES_PER_SPACE
            pages = self.confluence.get_all_pages_from_space(space_key, start=0, limit=limit)
            logger.info(f"Found {len(pages)} pages in space {space_key}")
            return pages
        except Exception as e:
            logger.error(f"Failed to get pages for space {space_key}: {e}")
            return []
    
    def get_page_content(self, page_id: str) -> Dict[str, Any]:
        """Get detailed content of a specific page."""
        try:
            page = self.confluence.get_page_by_id(page_id, expand='body.storage,version,ancestors')
            
            # Extract text content from HTML
            soup = BeautifulSoup(page['body']['storage']['value'], 'html.parser')
            text_content = soup.get_text(separator='\n', strip=True)
            
            # Get page metadata
            page_data = {
                'id': page['id'],
                'title': page['title'],
                'space_key': page['space']['key'],
                'content': text_content,
                'html_content': page['body']['storage']['value'],
                'version': page['version']['number'],
                'created': page['created'],
                'last_modified': page['version']['when'],
                'url': f"{self.config.CONFLUENCE_URL}/wiki{page['_links']['webui']}",
                'ancestors': [ancestor['title'] for ancestor in page.get('ancestors', [])]
            }
            
            # Get attachments if enabled
            if self.config.INCLUDE_ATTACHMENTS:
                attachments = self.confluence.get_attachments_from_content(page_id)
                page_data['attachments'] = [
                    {
                        'filename': att['title'],
                        'size': att['extensions']['fileSize'],
                        'url': att['_links']['download']
                    }
                    for att in attachments
                ]
            
            logger.info(f"Successfully extracted content from page: {page['title']}")
            return page_data
            
        except Exception as e:
            logger.error(f"Failed to get page content for {page_id}: {e}")
            return {}
    
    def scrape_space(self, space_key: str, output_dir: str = None) -> Dict[str, Any]:
        """Scrape all pages in a space and save to output directory."""
        output_dir = output_dir or self.config.OUTPUT_DIR
        os.makedirs(output_dir, exist_ok=True)
        
        space_data = {
            'space_key': space_key,
            'scraped_at': str(pd.Timestamp.now()),
            'pages': []
        }
        
        # Get all pages in the space
        pages = self.get_pages_in_space(space_key)
        
        for page in pages:
            page_content = self.get_page_content(page['id'])
            if page_content:
                space_data['pages'].append(page_content)
                
                # Save individual page as JSON
                page_file = os.path.join(output_dir, f"page_{page['id']}.json")
                with open(page_file, 'w', encoding='utf-8') as f:
                    json.dump(page_content, f, indent=2, ensure_ascii=False, default=str)
        
        # Save complete space data
        space_file = os.path.join(output_dir, f"space_{space_key}_complete.json")
        with open(space_file, 'w', encoding='utf-8') as f:
            json.dump(space_data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Successfully scraped space {space_key} with {len(space_data['pages'])} pages")
        return space_data
    
    def search_pages(self, query: str, space_key: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for pages using Confluence search."""
        try:
            search_results = self.confluence.search(query, cql=f"space={space_key}" if space_key else None, limit=limit)
            logger.info(f"Search for '{query}' returned {len(search_results)} results")
            return search_results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def get_page_hierarchy(self, space_key: str) -> Dict[str, Any]:
        """Get the page hierarchy for a space."""
        try:
            pages = self.get_pages_in_space(space_key)
            hierarchy = {}
            
            for page in pages:
                page_content = self.get_page_content(page['id'])
                if page_content and 'ancestors' in page_content:
                    current_level = hierarchy
                    for ancestor in page_content['ancestors']:
                        if ancestor not in current_level:
                            current_level[ancestor] = {}
                        current_level = current_level[ancestor]
                    current_level[page_content['title']] = {}
            
            return hierarchy
        except Exception as e:
            logger.error(f"Failed to get hierarchy for space {space_key}: {e}")
            return {}
