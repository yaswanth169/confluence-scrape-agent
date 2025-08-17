from crewai import Agent
from crewai.tools import BaseTool
from typing import Dict, List, Any
import json
import os
from confluence_scraper import ConfluenceScraper
from config import Config
import pandas as pd
import asyncio

class ConfluenceScraperAgent:
    """Crew AI Agent for scraping Confluence data."""
    
    def __init__(self):
        self.config = Config()
        self.scraper = ConfluenceScraper()
    
    def create_agent(self) -> Agent:
        """Create the Confluence Scraper Agent."""
        return Agent(
            role='Confluence Data Scraper',
            goal='Extract comprehensive data from Confluence spaces and pages',
            backstory="""You are an expert data extraction specialist with deep knowledge of 
            Confluence's structure and content organization. Your expertise lies in systematically 
            gathering information from Confluence spaces while maintaining data integrity and 
            organizing content in a structured format.""",
            verbose=True,
            allow_delegation=False,
            tools=[
                ConfluenceScraperTool(self.scraper),
                SpaceListTool(self.scraper),
                PageSearchTool(self.scraper)
            ]
        )

class ConfluenceScraperTool(BaseTool):
    """Tool for scraping Confluence spaces."""
    
    name = "Confluence Space Scraper"
    description = "Extracts all pages, content, metadata and optionally attachments from a Confluence space."
    
    def __init__(self, scraper: ConfluenceScraper):
        self.scraper = scraper
        super().__init__()
    
    def _run(self, space_key: str) -> str:
        """Scrape a Confluence space and return the results."""
        try:
            # Ensure the event loop is running and handle async operation
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, use ensure_future or create_task
                result = loop.run_until_complete(self.scraper.scrape_space(space_key))
            else:
                # Otherwise, it's safe to use run_until_complete directly
                result = asyncio.run(self.scraper.scrape_space(space_key))
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error scraping space {space_key}: {str(e)}"

class SpaceListTool(BaseTool):
    """Tool for listing available Confluence spaces."""
    
    name = "Confluence Space Lister"
    description = "Lists all available Confluence spaces that the user has access to."
    
    def __init__(self, scraper: ConfluenceScraper):
        self.scraper = scraper
        super().__init__()
    
    def _run(self) -> str:
        """List all available Confluence spaces."""
        try:
            # Handle async operation
            loop = asyncio.get_event_loop()
            if loop.is_running():
                spaces = loop.run_until_complete(self.scraper.get_spaces())
            else:
                spaces = asyncio.run(self.scraper.get_spaces())
            return json.dumps(spaces, indent=2)
        except Exception as e:
            return f"Error listing spaces: {str(e)}"

class PageSearchTool(BaseTool):
    """Tool for searching pages in Confluence."""
    
    name = "Confluence Page Search"
    description = "Searches for pages in Confluence by title or content. Optionally limited to a specific space."
    
    def __init__(self, scraper: ConfluenceScraper):
        self.scraper = scraper
        super().__init__()
    
    def _run(self, query: str, space_key: str = None) -> str:
        """Search for pages in Confluence."""
        try:
            # Handle async operation
            loop = asyncio.get_event_loop()
            if loop.is_running():
                results = loop.run_until_complete(self.scraper.search_pages(query, space_key))
            else:
                results = asyncio.run(self.scraper.search_pages(query, space_key))
            return json.dumps(results, indent=2)
        except Exception as e:
            return f"Error searching pages: {str(e)}"
