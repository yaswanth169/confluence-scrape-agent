import os
import json
import requests
from bs4 import BeautifulSoup
from atlassian import Confluence
from typing import Dict, List, Optional, Any
import logging
from config import Config
import pandas as pd
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfluenceScraper:
    """Confluence scraper utility for extracting data from Confluence pages."""
    
    def __init__(self):
        """Initialize the Confluence scraper with configuration."""
        self.config = Config()
        self.confluence = None
        self.session = None
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
    
    async def _async_connect_session(self):
        """Create an asynchronous HTTP session for API calls."""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(
                auth=aiohttp.BasicAuth(
                    self.config.CONFLUENCE_USERNAME,
                    self.config.CONFLUENCE_API_TOKEN
                )
            )
        return self.session
    
    async def get_spaces(self) -> List[Dict[str, Any]]:
        """Get all accessible spaces asynchronously."""
        try:
            # Use ThreadPoolExecutor to run synchronous code in an async context
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as pool:
                spaces = await loop.run_in_executor(pool, self.confluence.get_all_spaces)
            logger.info(f"Found {len(spaces)} spaces")
            return spaces
        except Exception as e:
            logger.error(f"Failed to get spaces: {e}")
            return []
    
    async def get_pages_in_space(self, space_key: str, limit: int = None) -> List[Dict[str, Any]]:
        """Get all pages in a specific space asynchronously."""
        try:
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as pool:
                pages = await loop.run_in_executor(
                    pool, 
                    lambda: self.confluence.get_all_pages_from_space(
                        space=space_key, 
                        start=0, 
                        limit=limit or self.config.MAX_PAGES_PER_SPACE,
                        status=None, 
                        expand='metadata'
                    )
                )
            logger.info(f"Found {len(pages)} pages in space {space_key}")
            return pages
        except Exception as e:
            logger.error(f"Failed to get pages in space {space_key}: {e}")
            return []
    
    async def get_page_content(self, page_id: str) -> Dict[str, Any]:
        """Get content of a specific page asynchronously."""
        try:
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as pool:
                page_data = await loop.run_in_executor(
                    pool, 
                    lambda: self.confluence.get_page_by_id(
                        page_id=page_id, 
                        expand='body.storage,version'
                    )
                )
            
            # Extract content
            content_html = page_data.get('body', {}).get('storage', {}).get('value', '')
            soup = BeautifulSoup(content_html, 'html.parser')
            content_text = soup.get_text()
            
            result = {
                'id': page_id,
                'title': page_data.get('title', 'Untitled'),
                'content': content_text,
                'content_html': content_html,
                'url': page_data.get('_links', {}).get('webui', ''),
                'version': page_data.get('version', {}).get('number', 1),
                'last_modified': page_data.get('version', {}).get('when', ''),
                'content_snippet': content_text[:200] + '...' if len(content_text) > 200 else content_text
            }
            
            # Optionally include attachments
            if self.config.INCLUDE_ATTACHMENTS:
                attachments = await loop.run_in_executor(
                    pool, 
                    lambda: self.confluence.get_attachments_from_content(page_id)
                )
                result['attachments'] = attachments
            
            logger.info(f"Retrieved content for page {page_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to get content for page {page_id}: {e}")
            return {'id': page_id, 'error': str(e)}
    
    async def scrape_space(self, space_key: str, output_dir: str = None) -> Dict[str, Any]:
        """Scrape all pages in a space asynchronously and save to output directory."""
        if output_dir is None:
            output_dir = os.path.join(self.config.OUTPUT_DIR, space_key)
        
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Starting scraping of space {space_key} to {output_dir}")
        
        # Get all pages in the space
        pages = await self.get_pages_in_space(space_key)
        
        # Fetch content for all pages concurrently
        tasks = [self.get_page_content(page['id']) for page in pages]
        page_contents = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Save results
        result = {
            'space_key': space_key,
            'total_pages': len(pages),
            'pages': []
        }
        
        for content in page_contents:
            if isinstance(content, dict) and 'error' not in content:
                page_id = content['id']
                output_file = os.path.join(output_dir, f"{page_id}.json")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(content, f, indent=2)
                result['pages'].append({
                    'id': page_id,
                    'title': content.get('title', 'Untitled'),
                    'saved_to': output_file
                })
            else:
                logger.error(f"Failed to process content: {content}")
        
        # Save summary file
        summary_file = os.path.join(output_dir, "summary.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        
        logger.info(f"Completed scraping of space {space_key}. Summary saved to {summary_file}")
        return result
    
    async def search_pages(self, query: str, space_key: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for pages in Confluence asynchronously."""
        try:
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as pool:
                results = await loop.run_in_executor(
                    pool, 
                    lambda: self.confluence.cql(
                        f"siteSearch ~ \"{query}\"" + (f" AND space = {space_key}" if space_key else ""),
                        limit=limit
                    )
                )
            logger.info(f"Search for '{query}' returned {len(results.get('results', []))} results")
            return results.get('results', [])
        except Exception as e:
            logger.error(f"Failed to search pages: {e}")
            return []
    
    async def get_page_hierarchy(self, space_key: str) -> Dict[str, Any]:
        """Get the page hierarchy for a space asynchronously."""
        try:
            pages = await self.get_pages_in_space(space_key)
            hierarchy = {
                'space_key': space_key,
                'pages': []
            }
            
            for page in pages:
                hierarchy['pages'].append({
                    'id': page['id'],
                    'title': page['title'],
                    'parentId': page.get('parentId', None)
                })
            
            logger.info(f"Retrieved page hierarchy for space {space_key}")
            return hierarchy
        except Exception as e:
            logger.error(f"Failed to get page hierarchy for space {space_key}: {e}")
            return {'space_key': space_key, 'error': str(e)}
    
    async def close_session(self):
        """Close the asynchronous HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("Closed aiohttp session")
