#!/usr/bin/env python3
"""
Confluence Scraper Agent - Main Application
A Crew AI-based system for scraping Confluence data, answering queries, and generating documents.
Uses local LLaMA model for AI processing.
"""

import os
import sys
import argparse
import json
from typing import Optional
from crew_manager import ConfluenceCrewManager
from config import Config
from llama_handler import llama_handler
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConfluenceScraperApp:
    """Main application class for the Confluence Scraper Agent."""
    
    def __init__(self):
        """Initialize the application."""
        self.config = Config()
        self.crew_manager = None
        
        # Validate configuration
        try:
            self.config.validate()
            
            # Check LLaMA model status
            print("🤖 Checking LLaMA model status...")
            if not llama_handler.is_model_loaded():
                print("📥 Loading LLaMA model...")
                if not llama_handler.load_model():
                    raise RuntimeError("Failed to load LLaMA model")
            
            model_info = llama_handler.get_model_info()
            print(f"✅ LLaMA model loaded successfully on {model_info.get('device', 'Unknown').upper()}")
            
            self.crew_manager = ConfluenceCrewManager()
            logger.info("Application initialized successfully")
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            logger.error("Please check your .env file and ensure all required variables are set")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Initialization error: {e}")
            sys.exit(1)
    
    def list_spaces(self) -> None:
        """List all available Confluence spaces."""
        try:
            logger.info("Fetching available Confluence spaces...")
            spaces = self.crew_manager.get_available_spaces()
            
            if spaces:
                print("\n=== Available Confluence Spaces ===")
                for space in spaces:
                    print(f"• {space['key']}: {space['name']}")
                print()
            else:
                print("No spaces found or unable to connect to Confluence.")
                
        except Exception as e:
            logger.error(f"Error listing spaces: {e}")
            print(f"Error: {e}")
    
    def scrape_space(self, space_key: str) -> None:
        """Scrape a specific Confluence space."""
        try:
            logger.info(f"Starting to scrape space: {space_key}")
            print(f"\n🚀 Starting Confluence scraping for space: {space_key}")
            
            # Create and run scraping crew
            scraping_crew = self.crew_manager.create_scraping_crew(space_key)
            result = scraping_crew.kickoff()
            
            print(f"✅ Scraping completed successfully!")
            print(f"📊 Result: {result}")
            
        except Exception as e:
            logger.error(f"Error scraping space {space_key}: {e}")
            print(f"❌ Error: {e}")
    
    def query_content(self, query: str, space_key: Optional[str] = None) -> None:
        """Query the scraped content."""
        try:
            logger.info(f"Processing query: {query}")
            print(f"\n🔍 Processing query: {query}")
            
            # Create and run query crew
            query_crew = self.crew_manager.create_query_crew(query, space_key)
            result = query_crew.kickoff()
            
            print(f"✅ Query processed successfully!")
            print(f"📝 Answer: {result}")
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            print(f"❌ Error: {e}")
    
    def generate_document(self, content_summary: str, document_type: str = "markdown") -> None:
        """Generate a document from scraped content."""
        try:
            logger.info(f"Generating {document_type} document")
            print(f"\n📄 Generating {document_type.upper()} document...")
            
            # Create and run document generation crew
            doc_crew = self.crew_manager.create_document_generation_crew(content_summary, document_type)
            result = doc_crew.kickoff()
            
            print(f"✅ {document_type.upper()} document generated successfully!")
            print(f"📄 Result: {result}")
            
        except Exception as e:
            logger.error(f"Error generating document: {e}")
            print(f"❌ Error: {e}")
    
    def run_full_workflow(self, space_key: str, user_query: Optional[str] = None, 
                         generate_document: bool = False) -> None:
        """Run the complete workflow: scrape, query, and optionally generate document."""
        try:
            logger.info(f"Running full workflow for space: {space_key}")
            print(f"\n🚀 Running complete workflow for space: {space_key}")
            
            # Run the full workflow
            results = self.crew_manager.run_full_workflow(space_key, user_query, generate_document)
            
            print(f"✅ Full workflow completed successfully!")
            print(f"📊 Results summary:")
            
            if 'scraping' in results:
                print(f"  • Scraping: {results['scraping']}")
            
            if 'query' in results:
                print(f"  • Query: {results['query']}")
            
            if 'document' in results:
                print(f"  • Document: {results['document']}")
                
        except Exception as e:
            logger.error(f"Error in full workflow: {e}")
            print(f"❌ Error: {e}")
    
    def interactive_mode(self) -> None:
        """Run the application in interactive mode."""
        print("\n" + "="*60)
        print("🤖 Confluence Scraper Agent - Interactive Mode")
        print("="*60)
        print("This system uses Crew AI with local LLaMA model for intelligent processing.")
        print("="*60)
        
        while True:
            print("\n📋 Available commands:")
            print("1. List Confluence spaces")
            print("2. Scrape a space")
            print("3. Query scraped content")
            print("4. Generate document")
            print("5. Run full workflow")
            print("6. Show system status")
            print("0. Exit")
            
            try:
                choice = input("\n🎯 Enter your choice (0-6): ").strip()
                
                if choice == "0":
                    print("👋 Goodbye!")
                    break
                elif choice == "1":
                    self.list_spaces()
                elif choice == "2":
                    space_key = input("🔑 Enter space key: ").strip()
                    if space_key:
                        self.scrape_space(space_key)
                    else:
                        print("❌ Space key is required.")
                elif choice == "3":
                    query = input("❓ Enter your query: ").strip()
                    if query:
                        space_key = input("🔑 Enter space key (optional): ").strip() or None
                        self.query_content(query, space_key)
                    else:
                        print("❌ Query is required.")
                elif choice == "4":
                    content = input("📝 Enter content summary: ").strip()
                    if content:
                        doc_type = input("📄 Document type (markdown/pdf): ").strip() or "markdown"
                        self.generate_document(content, doc_type)
                    else:
                        print("❌ Content summary is required.")
                elif choice == "5":
                    space_key = input("🔑 Enter space key: ").strip()
                    if space_key:
                        user_query = input("❓ Enter query (optional): ").strip() or None
                        generate_doc = input("📄 Generate document? (y/n): ").strip().lower() == 'y'
                        self.run_full_workflow(space_key, user_query, generate_doc)
                    else:
                        print("❌ Space key is required.")
                elif choice == "6":
                    self.show_system_status()
                else:
                    print("❌ Invalid choice. Please enter a number between 0-6.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def show_system_status(self) -> None:
        """Show the current system status."""
        print("\n=== System Status ===")
        
        # Configuration status
        print(f"🔧 Configuration:")
        print(f"  • Confluence URL: {self.config.CONFLUENCE_URL}")
        print(f"  • Username: {self.config.CONFLUENCE_USERNAME}")
        print(f"  • API Token: {'✅ Set' if not self.config.CONFLUENCE_API_TOKEN.startswith('your-') else '❌ Not set'}")
        print(f"  • Output Directory: {self.config.OUTPUT_DIR}")
        
        # LLaMA model status
        print(f"\n🤖 LLaMA Model:")
        model_info = llama_handler.get_model_info()
        if model_info['status'] == 'loaded':
            print(f"  • Status: ✅ Loaded")
            print(f"  • Device: {model_info['device'].upper()}")
            print(f"  • Model Path: {model_info['model_path']}")
            print(f"  • CUDA Available: {'✅ Yes' if model_info['cuda_available'] else '❌ No'}")
        else:
            print(f"  • Status: ❌ Not loaded")
        
        # Crew status
        print(f"\n👥 Crew AI:")
        if self.crew_manager:
            print(f"  • Status: ✅ Initialized")
            print(f"  • Agents: 3 (Scraper, Query, PDF Generator)")
        else:
            print(f"  • Status: ❌ Not initialized")
        
        print()

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description="Confluence Scraper Agent using Crew AI and local LLaMA model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --interactive                    # Run in interactive mode
  %(prog)s --list-spaces                    # List available Confluence spaces
  %(prog)s --scrape-space SPACE_KEY        # Scrape a specific space
  %(prog)s --query "your question"         # Query scraped content
  %(prog)s --generate-doc "content"        # Generate document from content
  %(prog)s --full-workflow SPACE_KEY       # Run complete workflow
        """
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Run in interactive mode'
    )
    
    parser.add_argument(
        '--list-spaces', '-l',
        action='store_true',
        help='List available Confluence spaces'
    )
    
    parser.add_argument(
        '--scrape-space', '-s',
        metavar='SPACE_KEY',
        help='Scrape a specific Confluence space'
    )
    
    parser.add_argument(
        '--query', '-q',
        metavar='QUERY',
        help='Query the scraped content'
    )
    
    parser.add_argument(
        '--generate-doc', '-g',
        metavar='CONTENT',
        help='Generate a document from content'
    )
    
    parser.add_argument(
        '--full-workflow', '-f',
        metavar='SPACE_KEY',
        help='Run the complete workflow for a space'
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show system status'
    )
    
    args = parser.parse_args()
    
    try:
        app = ConfluenceScraperApp()
        
        if args.status:
            app.show_system_status()
        elif args.list_spaces:
            app.list_spaces()
        elif args.scrape_space:
            app.scrape_space(args.scrape_space)
        elif args.query:
            app.query_content(args.query)
        elif args.generate_doc:
            app.generate_document(args.generate_doc)
        elif args.full_workflow:
            app.run_full_workflow(args.full_workflow)
        elif args.interactive:
            app.interactive_mode()
        else:
            # Default to interactive mode if no arguments provided
            app.interactive_mode()
            
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
