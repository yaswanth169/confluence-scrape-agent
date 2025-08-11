from crewai import Agent, Task
from crewai.tools import BaseTool
from typing import Dict, List, Any
import json
import os
from confluence_scraper import ConfluenceScraper
from config import Config
from llama_handler import llama_handler
import pandas as pd

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
                ContentSearchTool(),
                PageAnalysisTool(),
                KnowledgeQueryTool()
            ]
        )

class PDFGeneratorAgent:
    """Crew AI Agent for generating PDF and Markdown files."""
    
    def __init__(self):
        self.config = Config()
    
    def create_agent(self) -> Agent:
        """Create the PDF Generator Agent."""
        return Agent(
            role='Document Generator',
            goal='Create well-formatted PDF and Markdown documents from Confluence content',
            backstory="""You are a document formatting specialist with expertise in creating 
            professional, well-structured documents. You understand how to organize content 
            logically, apply proper formatting, and generate both PDF and Markdown outputs 
            that are easy to read and navigate.""",
            verbose=True,
            allow_delegation=False,
            tools=[
                PDFGenerationTool(),
                MarkdownGenerationTool(),
                DocumentStructureTool()
            ]
        )

# Custom Tools for the Agents

class ConfluenceScraperTool(BaseTool):
    """Tool for scraping Confluence spaces."""
    
    name: str = "confluence_scraper"
    description: str = "Scrapes all pages from a specified Confluence space"
    
    def __init__(self, scraper: ConfluenceScraper):
        super().__init__()
        self.scraper = scraper
    
    def _run(self, space_key: str) -> str:
        """Scrape a Confluence space."""
        try:
            result = self.scraper.scrape_space(space_key)
            return f"Successfully scraped space {space_key} with {len(result['pages'])} pages. Data saved to output directory."
        except Exception as e:
            return f"Error scraping space {space_key}: {str(e)}"

class SpaceListTool(BaseTool):
    """Tool for listing available Confluence spaces."""
    
    name: str = "list_spaces"
    description: str = "Lists all accessible Confluence spaces"
    
    def __init__(self, scraper: ConfluenceScraper):
        super().__init__()
        self.scraper = scraper
    
    def _run(self) -> str:
        """List all available spaces."""
        try:
            spaces = self.scraper.get_spaces()
            space_list = "\n".join([f"- {space['key']}: {space['name']}" for space in spaces])
            return f"Available Confluence spaces:\n{space_list}"
        except Exception as e:
            return f"Error listing spaces: {str(e)}"

class PageSearchTool(BaseTool):
    """Tool for searching Confluence pages."""
    
    name: str = "search_pages"
    description: str = "Searches for pages in Confluence using keywords"
    
    def __init__(self, scraper: ConfluenceScraper):
        super().__init__()
        self.scraper = scraper
    
    def _run(self, query: str, space_key: str = None) -> str:
        """Search for pages using keywords."""
        try:
            results = self.scraper.search_pages(query, space_key)
            if results:
                result_list = "\n".join([f"- {result['title']} (ID: {result['id']})" for result in results])
                return f"Search results for '{query}':\n{result_list}"
            else:
                return f"No results found for query: {query}"
        except Exception as e:
            return f"Error searching pages: {str(e)}"

class ContentSearchTool(BaseTool):
    """Tool for searching through scraped content."""
    
    name: str = "content_search"
    description: str = "Searches through scraped Confluence content for specific information"
    
    def _run(self, query: str, output_dir: str = None) -> str:
        """Search through scraped content."""
        try:
            output_dir = output_dir or Config().OUTPUT_DIR
            
            # Check if output directory exists and contains scraped data
            if not os.path.exists(output_dir):
                return "No scraped data found. Please scrape Confluence content first."
            
            # Look for JSON files with scraped data
            json_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
            
            if not json_files:
                return "No scraped data files found. Please scrape Confluence content first."
            
            # Search through the most recent scraped data file
            latest_file = max(json_files, key=lambda x: os.path.getctime(os.path.join(output_dir, x)))
            file_path = os.path.join(output_dir, latest_file)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Search through the content
            relevant_content = []
            for page in data.get('pages', []):
                content = page.get('content', '').lower()
                title = page.get('title', '').lower()
                
                if query.lower() in content or query.lower() in title:
                    relevant_content.append({
                        'title': page.get('title', 'No title'),
                        'content': page.get('content', '')[:200] + '...',
                        'url': page.get('url', 'No URL')
                    })
            
            if relevant_content:
                result = f"Found {len(relevant_content)} relevant pages for query: '{query}'\n\n"
                for item in relevant_content:
                    result += f"**Title:** {item['title']}\n"
                    result += f"**Content:** {item['content']}\n"
                    result += f"**URL:** {item['url']}\n\n"
                return result
            else:
                return f"No relevant content found for query: '{query}'"
                
        except Exception as e:
            return f"Error searching content: {str(e)}"

class PageAnalysisTool(BaseTool):
    """Tool for analyzing specific page content."""
    
    name: str = "analyze_page"
    description: str = "Analyzes and summarizes content from a specific page"
    
    def _run(self, page_id: str, output_dir: str = None) -> str:
        """Analyze a specific page."""
        try:
            output_dir = output_dir or Config().OUTPUT_DIR
            
            # Check if output directory exists
            if not os.path.exists(output_dir):
                return "No scraped data found. Please scrape Confluence content first."
            
            # Look for JSON files with scraped data
            json_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
            
            if not json_files:
                return "No scraped data files found. Please scrape Confluence content first."
            
            # Search through the most recent scraped data file
            latest_file = max(json_files, key=lambda x: os.path.getctime(os.path.join(output_dir, x)))
            file_path = os.path.join(output_dir, latest_file)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Find the specific page
            target_page = None
            for page in data.get('pages', []):
                if page.get('id') == page_id:
                    target_page = page
                    break
            
            if not target_page:
                return f"Page with ID '{page_id}' not found in scraped data."
            
            # Use LLaMA to analyze the page content
            analysis_prompt = f"""
            Analyze the following Confluence page content and provide a comprehensive summary:
            
            Title: {target_page.get('title', 'No title')}
            Content: {target_page.get('content', 'No content')}
            
            Please provide:
            1. A concise summary of the main content
            2. Key points and insights
            3. Any important details or recommendations
            4. Overall assessment of the content quality and usefulness
            """
            
            # Generate analysis using LLaMA
            analysis = llama_handler.generate_response(
                analysis_prompt,
                max_tokens=400,
                temperature=0.7,
                top_p=0.9
            )
            
            return f"**Page Analysis for: {target_page.get('title', 'No title')}**\n\n{analysis}"
            
        except Exception as e:
            return f"Error analyzing page: {str(e)}"

class KnowledgeQueryTool(BaseTool):
    """Tool for answering knowledge-based queries."""
    
    name: str = "knowledge_query"
    description: str = "Answers questions based on scraped Confluence knowledge"
    
    def _run(self, question: str, output_dir: str = None) -> str:
        """Answer a knowledge-based question."""
        try:
            output_dir = output_dir or Config().OUTPUT_DIR
            
            # Check if output directory exists
            if not os.path.exists(output_dir):
                return "No scraped data found. Please scrape Confluence content first."
            
            # Look for JSON files with scraped data
            json_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
            
            if not json_files:
                return "No scraped data files found. Please scrape Confluence content first."
            
            # Search through the most recent scraped data file
            latest_file = max(json_files, key=lambda x: os.path.getctime(os.path.join(output_dir, x)))
            file_path = os.path.join(output_dir, latest_file)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract relevant content for the question
            relevant_content = []
            for page in data.get('pages', []):
                content = page.get('content', '').lower()
                title = page.get('title', '').lower()
                
                # Simple keyword matching (can be improved with embeddings)
                question_keywords = question.lower().split()
                if any(keyword in content or keyword in title for keyword in question_keywords):
                    relevant_content.append({
                        'title': page.get('title', 'No title'),
                        'content': page.get('content', ''),
                        'url': page.get('url', 'No URL')
                    })
            
            if not relevant_content:
                return f"I couldn't find relevant information in the scraped Confluence data to answer your question: '{question}'"
            
            # Prepare context for LLaMA
            context = "\n\n".join([
                f"Page: {item['title']}\nContent: {item['content'][:500]}..."
                for item in relevant_content[:3]  # Limit to 3 most relevant pages
            ])
            
            # Generate answer using LLaMA
            answer_prompt = f"""
            Based on the following Confluence content, please answer this question: "{question}"
            
            Context from Confluence pages:
            {context}
            
            Please provide a comprehensive answer based on the available information. If the answer cannot be found in the provided content, please say so clearly.
            """
            
            answer = llama_handler.generate_response(
                answer_prompt,
                max_tokens=500,
                temperature=0.7,
                top_p=0.9
            )
            
            return f"**Answer to: {question}**\n\n{answer}\n\n*Based on {len(relevant_content)} relevant Confluence pages*"
            
        except Exception as e:
            return f"Error answering question: {str(e)}"

class PDFGenerationTool(BaseTool):
    """Tool for generating PDF documents."""
    
    name: str = "generate_pdf"
    description: str = "Generates PDF documents from Confluence content"
    
    def _run(self, content_data: str, output_filename: str, output_dir: str = None) -> str:
        """Generate a PDF document."""
        try:
            output_dir = output_dir or Config().OUTPUT_DIR
            
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Use LLaMA to structure the content for PDF generation
            structure_prompt = f"""
            Please structure the following content for a professional PDF document:
            
            {content_data}
            
            Provide a well-organized structure with:
            1. Clear headings and subheadings
            2. Logical flow and organization
            3. Professional formatting suggestions
            4. Executive summary if applicable
            """
            
            structured_content = llama_handler.generate_response(
                structure_prompt,
                max_tokens=600,
                temperature=0.7,
                top_p=0.9
            )
            
            # For now, save as markdown (PDF generation can be added later)
            output_path = os.path.join(output_dir, f"{output_filename}.md")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"# {output_filename}\n\n")
                f.write(structured_content)
            
            return f"PDF content structured and saved as markdown: {output_path}"
            
        except Exception as e:
            return f"Error generating PDF: {str(e)}"

class MarkdownGenerationTool(BaseTool):
    """Tool for generating Markdown documents."""
    
    name: str = "generate_markdown"
    description: str = "Generates Markdown documents from Confluence content"
    
    def _run(self, content_data: str, output_filename: str, output_dir: str = None) -> str:
        """Generate a Markdown document."""
        try:
            output_dir = output_dir or Config().OUTPUT_DIR
            
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Use LLaMA to create a well-structured markdown document
            markdown_prompt = f"""
            Convert the following content into a well-structured markdown document:
            
            {content_data}
            
            Please format it with:
            1. Clear headings using #, ##, ###
            2. Bullet points and numbered lists where appropriate
            3. Bold and italic text for emphasis
            4. Code blocks if technical content is present
            5. Tables if data is structured
            6. Professional and clean formatting
            """
            
            markdown_content = llama_handler.generate_response(
                markdown_prompt,
                max_tokens=800,
                temperature=0.7,
                top_p=0.9
            )
            
            output_path = os.path.join(output_dir, f"{output_filename}.md")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            return f"Markdown document generated successfully: {output_path}"
            
        except Exception as e:
            return f"Error generating markdown: {str(e)}"

class DocumentStructureTool(BaseTool):
    """Tool for structuring documents."""
    
    name: str = "structure_document"
    description: str = "Structures and organizes content for document generation"
    
    def _run(self, content_data: str, structure_type: str = "standard") -> str:
        """Structure content for document generation."""
        try:
            # Use LLaMA to structure the content based on the specified type
            structure_prompt = f"""
            Structure the following content for a {structure_type} document:
            
            {content_data}
            
            Please organize it with:
            1. Clear document structure
            2. Appropriate headings and sections
            3. Logical flow and organization
            4. Professional formatting
            5. Executive summary if applicable
            6. Table of contents structure
            """
            
            structured_content = llama_handler.generate_response(
                structure_prompt,
                max_tokens=600,
                temperature=0.7,
                top_p=0.9
            )
            
            return f"Content structured for {structure_type} document:\n\n{structured_content}"
            
        except Exception as e:
            return f"Error structuring document: {str(e)}"
