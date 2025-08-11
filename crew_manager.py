from crewai import Crew, Task
from agents import ConfluenceScraperAgent, QueryAgent, PDFGeneratorAgent
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
            """,
            agent=self.scraper_agent,
            expected_output="""A detailed report confirming successful scraping of the space, 
            including the number of pages processed, any errors encountered, and the location 
            where the data has been saved."""
        )
        
        # Task 2: Analyze scraped data
        analysis_task = Task(
            description=f"""
            Analyze the scraped data from space '{space_key}' to understand the content structure.
            
            Your responsibilities:
            1. Review the scraped data for completeness
            2. Identify key themes and topics covered
            3. Analyze the content hierarchy and relationships
            4. Identify any missing or incomplete data
            5. Provide a summary of the content coverage
            
            Expected output: A comprehensive analysis report of the scraped content including 
            content summary, key themes, and data quality assessment.
            """,
            agent=self.query_agent,
            expected_output="""An analysis report containing:
            - Content overview and summary
            - Key themes and topics identified
            - Content hierarchy analysis
            - Data quality assessment
            - Recommendations for any additional scraping if needed."""
        )
        
        # Create the crew
        crew = Crew(
            agents=[self.scraper_agent, self.query_agent],
            tasks=[scraping_task, analysis_task],
            verbose=True,
            memory=True
        )
        
        return crew
    
    def create_query_crew(self, query: str, space_key: str = None) -> Crew:
        """Create a crew for answering user queries about scraped data."""
        
        # Task 1: Search and analyze content
        search_task = Task(
            description=f"""
            Search through the scraped Confluence data to find relevant information for the query: '{query}'
            
            Your responsibilities:
            1. Search through all scraped content for relevant information
            2. Analyze the context and relevance of found content
            3. Synthesize information from multiple sources if needed
            4. Identify the most relevant and accurate answers
            5. Provide comprehensive and well-structured responses
            
            Expected output: A detailed answer to the user's query based on the scraped Confluence data.
            """,
            agent=self.query_agent,
            expected_output="""A comprehensive answer that:
            - Directly addresses the user's query
            - Provides relevant information from the scraped data
            - Includes source references where applicable
            - Is well-structured and easy to understand
            - Uses the LLaMA model to generate intelligent responses"""
        )
        
        # Create the crew
        crew = Crew(
            agents=[self.query_agent],
            tasks=[search_task],
            verbose=True,
            memory=True
        )
        
        return crew
    
    def create_document_generation_crew(self, content_summary: str, document_type: str = "pdf") -> Crew:
        """Create a crew for generating documents from scraped content."""
        
        # Task 1: Structure content for document generation
        structure_task = Task(
            description=f"""
            Structure and organize the scraped Confluence content for {document_type.upper()} document generation.
            
            Your responsibilities:
            1. Analyze the content summary and organize it logically
            2. Create a clear document structure with appropriate sections
            3. Ensure content flows logically and is easy to follow
            4. Apply professional formatting standards
            5. Prepare content for the specified document type
            
            Content to structure: {content_summary}
            
            Expected output: Well-structured content ready for {document_type.upper()} generation.
            """,
            agent=self.pdf_agent,
            expected_output="""Structured content that:
            - Has clear logical organization
            - Includes appropriate headings and sections
            - Follows professional formatting standards
            - Is optimized for {document_type.upper()} output
            - Uses the LLaMA model for intelligent content structuring"""
        )
        
        # Task 2: Generate the document
        generation_task = Task(
            description=f"""
            Generate a {document_type.upper()} document from the structured content.
            
            Your responsibilities:
            1. Use the structured content to create the final document
            2. Apply appropriate formatting for the document type
            3. Ensure the document is professional and well-presented
            4. Include any necessary metadata or headers
            5. Save the document to the appropriate output location
            
            Expected output: A complete, well-formatted {document_type.upper()} document.
            """,
            agent=self.pdf_agent,
            expected_output="""A complete document that:
            - Is properly formatted for {document_type.upper()} output
            - Contains all the structured content
            - Has professional appearance
            - Is saved to the correct output location
            - Uses the LLaMA model for intelligent document generation"""
        )
        
        # Create the crew
        crew = Crew(
            agents=[self.pdf_agent],
            tasks=[structure_task, generation_task],
            verbose=True,
            memory=True
        )
        
        return crew
    
    def run_full_workflow(self, space_key: str, user_query: str = None, generate_document: bool = False) -> dict:
        """Run the complete workflow: scrape, query, and optionally generate documents."""
        
        try:
            results = {}
            
            # Step 1: Scrape Confluence space
            logger.info(f"Starting scraping workflow for space: {space_key}")
            scraping_crew = self.create_scraping_crew(space_key)
            scraping_result = scraping_crew.kickoff()
            results['scraping'] = scraping_result
            
            # Step 2: Handle user query if provided
            if user_query:
                logger.info(f"Processing user query: {user_query}")
                query_crew = self.create_query_crew(user_query, space_key)
                query_result = query_crew.kickoff()
                results['query'] = query_result
            
            # Step 3: Generate document if requested
            if generate_document:
                logger.info("Generating document from scraped content")
                content_summary = str(results.get('query', 'No query results available'))
                doc_crew = self.create_document_generation_crew(content_summary, "markdown")
                doc_result = doc_crew.kickoff()
                results['document'] = doc_result
            
            logger.info("Full workflow completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error in full workflow: {str(e)}")
            raise
    
    def get_available_spaces(self) -> list:
        """Get list of available Confluence spaces."""
        try:
            scraper = ConfluenceScraperAgent().scraper
            return scraper.get_spaces()
        except Exception as e:
            logger.error(f"Error getting spaces: {str(e)}")
            return []
    
    def search_content(self, query: str, space_key: str = None) -> dict:
        """Search through scraped content."""
        try:
            query_crew = self.create_query_crew(query, space_key)
            result = query_crew.kickoff()
            return {"query": query, "result": result}
        except Exception as e:
            logger.error(f"Error searching content: {str(e)}")
            return {"query": query, "error": str(e)}
    
    def cleanup(self):
        """Clean up resources."""
        try:
            llama_handler.cleanup()
            logger.info("Resources cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
