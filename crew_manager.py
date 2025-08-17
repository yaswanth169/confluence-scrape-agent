from crewai import Crew, Task
from scraper_agent import ConfluenceScraperAgent
from query_agent import QueryAgent
from pdf_generator_agent import PDFGeneratorAgent
from config import Config
from llama_handler import llama_handler
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfluenceCrewManager:
    """Manages the Crew AI crew for Confluence scraping and processing."""
    
    def __init__(self):
        """Initialize the crew manager."""
        self.config = Config()
        
        # Initialize LLaMA model
        logger.info("Initializing LLaMA model...")
        if not llama_handler.is_model_loaded():
            if llama_handler.load_model():
                logger.info("✅ LLaMA model loaded successfully")
            else:
                logger.error("❌ Failed to load LLaMA model")
                raise RuntimeError("LLaMA model could not be loaded")
        
        # Create agents
        self.scraper_agent = ConfluenceScraperAgent().create_agent()
        self.query_agent = QueryAgent().create_agent()
        self.pdf_agent = PDFGeneratorAgent().create_agent()
        
        logger.info("Crew AI agents initialized successfully")
    
    def create_scraping_crew(self, space_key: str) -> Crew:
        """Create a crew for scraping Confluence data."""
        
        # Task 1: Scrape Confluence space
        scraping_task = Task(
            description=f"""
            Scrape all pages from the Confluence space '{space_key}'.
            
            Your responsibilities:
            1. Connect to the Confluence instance
            2. Retrieve all pages from the specified space
            3. Extract content, metadata, and attachments
            4. Save the data in a structured JSON format
            5. Ensure data integrity and completeness
            
            Expected output: A comprehensive dataset containing all pages, their content, 
            metadata, and any attachments from the space.
            
            Space key: {space_key}
            Maximum pages: {self.config.MAX_PAGES_PER_SPACE}
            Include attachments: {self.config.INCLUDE_ATTACHMENTS}
            Include comments: {self.config.INCLUDE_COMMENTS}
            Output directory: {self.config.OUTPUT_DIR}
            """,
            agent=self.scraper_agent,
            expected_output="JSON data representing the scraped content from the space"
        )
        
        # Create crew
        crew = Crew(
            agents=[self.scraper_agent],
            tasks=[scraping_task],
            verbose=2
        )
        
        logger.info(f"Created scraping crew for space: {space_key}")
        return crew
    
    def create_query_crew(self, query: str, space_key: str = None) -> Crew:
        """Create a crew for querying scraped Confluence content."""
        
        # Task 1: Process user query
        query_task = Task(
            description=f"""
            Analyze the user's query and search through scraped Confluence content to provide 
            a comprehensive answer.
            
            Query: {query}
            Space (optional): {space_key if space_key else 'All spaces'}
            Output directory: {self.config.OUTPUT_DIR}
            
            Your responsibilities:
            1. Understand the user's question or information need
            2. Search through the scraped content to find relevant information
            3. Synthesize a clear, detailed response to the query
            4. Include references to source pages where applicable
            
            Expected output: A detailed response to the user's query with relevant information 
            from the Confluence content and source references.
            """,
            agent=self.query_agent,
            expected_output="Detailed response to the user's query"
        )
        
        # Create crew
        crew = Crew(
            agents=[self.query_agent],
            tasks=[query_task],
            verbose=2
        )
        
        logger.info(f"Created query crew for query: {query}")
        return crew
    
    def create_document_generation_crew(self, content_summary: str, document_type: str = "pdf") -> Crew:
        """Create a crew for generating documents from scraped content."""
        
        # Task 1: Generate document
        gen_task = Task(
            description=f"""
            Create a professional, well-formatted document from the provided Confluence content summary.
            
            Content summary: {content_summary[:200]}...
            Document type: {document_type}
            Output directory: {self.config.OUTPUT_DIR}
            
            Your responsibilities:
            1. Analyze the content summary or dataset provided
            2. Structure the content logically for document format
            3. Generate a polished document in the specified format ({document_type})
            4. Ensure the document is clear, organized, and visually appealing
            
            Expected output: A file path to the generated document in {document_type} format.
            """,
            agent=self.pdf_agent,
            expected_output=f"Path to generated {document_type} document"
        )
        
        # Create crew
        crew = Crew(
            agents=[self.pdf_agent],
            tasks=[gen_task],
            verbose=2
        )
        
        logger.info(f"Created document generation crew for {document_type} document")
        return crew
    
    def run_full_workflow(self, space_key: str, user_query: str = None, generate_document: bool = False) -> dict:
        """Run a full workflow: scrape, query (optional), and generate document (optional)."""
        result = {
            "scraping": None,
            "query": None,
            "document": None
        }
        
        try:
            # Step 1: Scrape the space
            scraping_crew = self.create_scraping_crew(space_key)
            result["scraping"] = scraping_crew.kickoff()
            logger.info(f"Completed scraping for space {space_key}")
            
            # Step 2: Process user query if provided
            if user_query:
                query_crew = self.create_query_crew(user_query, space_key)
                result["query"] = query_crew.kickoff()
                logger.info(f"Completed query processing for: {user_query}")
            
            # Step 3: Generate document if requested
            if generate_document:
                content_summary = result.get("query") or result.get("scraping")
                if content_summary:
                    doc_crew = self.create_document_generation_crew(content_summary)
                    result["document"] = doc_crew.kickoff()
                    logger.info("Completed document generation")
                else:
                    logger.warning("No content available for document generation")
                    result["document"] = "No content available for document generation"
            
            return result
        except Exception as e:
            logger.error(f"Error in full workflow for space {space_key}: {e}")
            raise
    
    def get_available_spaces(self) -> list:
        """Get a list of available Confluence spaces."""
        # This would be implemented with the scraper directly or through an agent task
        # For now, we'll return an empty list as placeholder
        logger.info("Fetching available spaces (placeholder)")
        return []
    
    def search_content(self, query: str, space_key: str = None) -> dict:
        """Search scraped content for a specific query."""
        query_crew = self.create_query_crew(query, space_key)
        result = query_crew.kickoff()
        return {"query": query, "result": result}
    
    def cleanup(self):
        """Clean up resources used by the crew manager."""
        logger.info("Cleaning up crew manager resources")
        # Any cleanup tasks would go here
        pass
