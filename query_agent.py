from crewai import Agent
from crewai.tools import BaseTool
from typing import Dict, List, Any
import json
import os
from config import Config
import pandas as pd

class QueryAgent:
    """Crew AI Agent for handling user queries about scraped data."""
    
    def __init__(self):
        self.config = Config()
    
    def create_agent(self) -> Agent:
        """Create the Query Agent."""
        return Agent(
            role='Confluence Knowledge Expert',
            goal='Provide accurate and helpful answers to user queries about Confluence content',
            backstory="""You are a knowledgeable expert who has access to comprehensive 
            Confluence data. You excel at understanding user questions and providing 
            detailed, accurate responses based on the scraped content. You can search 
            through pages, analyze content, and synthesize information to answer queries.""",
            verbose=True,
            allow_delegation=False,
            tools=[
                ContentQueryTool(),
                PageContentTool(),
                ContentSummarizerTool()
            ]
        )

class ContentQueryTool(BaseTool):
    """Tool for querying scraped Confluence content."""
    
    name = "Confluence Content Query"
    description = "Searches through scraped Confluence content to answer user questions."
    
    def __init__(self):
        super().__init__()
    
    def _run(self, query: str, output_dir: str = None) -> str:
        """Query scraped content."""
        try:
            if output_dir is None:
                output_dir = Config.OUTPUT_DIR
            
            # Search for relevant content in output directory
            results = []
            for space_dir in os.listdir(output_dir):
                space_path = os.path.join(output_dir, space_dir)
                if not os.path.isdir(space_path):
                    continue
                
                for json_file in os.listdir(space_path):
                    if json_file.endswith('.json'):
                        file_path = os.path.join(space_path, json_file)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            title = data.get('title', '').lower()
                            content_snippet = data.get('content_snippet', '').lower()
                            if query.lower() in title or query.lower() in content_snippet:
                                results.append({
                                    'space': space_dir,
                                    'page_id': data.get('id'),
                                    'title': data.get('title'),
                                    'url': data.get('url')
                                })
            
            if not results:
                return f"No content found matching query: {query}"
            return json.dumps(results, indent=2)
        except Exception as e:
            return f"Error querying content: {str(e)}"

class PageContentTool(BaseTool):
    """Tool for getting detailed page content."""
    
    name = "Confluence Page Content Retriever"
    description = "Retrieves the full content of a specific Confluence page from scraped data by page ID."
    
    def __init__(self):
        super().__init__()
    
    def _run(self, page_id: str, output_dir: str = None) -> str:
        """Get full content of a specific page."""
        try:
            if output_dir is None:
                output_dir = Config.OUTPUT_DIR
            
            # Search for the page in output directory
            for space_dir in os.listdir(output_dir):
                space_path = os.path.join(output_dir, space_dir)
                if not os.path.isdir(space_path):
                    continue
                
                json_file = f"{page_id}.json"
                file_path = os.path.join(space_path, json_file)
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        return json.dumps(data, indent=2)
            
            return f"Page {page_id} not found in scraped data"
        except Exception as e:
            return f"Error retrieving page content: {str(e)}"

class ContentSummarizerTool(BaseTool):
    """Tool for summarizing content."""
    
    name = "Content Summarizer"
    description = "Summarizes Confluence content to provide concise answers to user questions."
    
    def __init__(self):
        super().__init__()
    
    def _run(self, question: str, output_dir: str = None) -> str:
        """Summarize content to answer a user question."""
        try:
            if output_dir is None:
                output_dir = Config.OUTPUT_DIR
            
            # First do a content query to get relevant pages
            query_result_str = ContentQueryTool()._run(question, output_dir)
            query_result = json.loads(query_result_str) if query_result_str.startswith("[") else []
            
            if not query_result:
                return f"No relevant content found to answer: {question}"
            
            summaries = []
            for item in query_result[:3]:  # Limit to top 3 results
                page_id = item.get('page_id')
                if page_id:
                    page_content_str = PageContentTool()._run(page_id, output_dir)
                    if page_content_str and not page_content_str.startswith("Error") and not page_content_str.startswith("Page not found"):
                        page_content = json.loads(page_content_str) if page_content_str.startswith("{") else {}
                        content_snippet = page_content.get('content_snippet', '')
                        summaries.append(f"From '{item.get('title', 'Untitled')}': {content_snippet[:200]}...")
            
            if not summaries:
                return f"Could not summarize content for: {question}"
            
            return "Summary of relevant content:\n" + "\n".join(summaries)
        except Exception as e:
            return f"Error summarizing content: {str(e)}"
