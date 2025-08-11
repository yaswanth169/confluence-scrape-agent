#!/usr/bin/env python3
"""
Example usage of the Confluence Scraper Agent system.
This script demonstrates the basic functionality of the system.
"""

import os
import sys
from crew_manager import ConfluenceCrewManager
from config import Config

def main():
    """Example usage of the Confluence Scraper Agent system."""
    
    print("🚀 Confluence Scraper Agent - Example Usage")
    print("=" * 50)
    
    try:
        # Initialize the crew manager
        print("📋 Initializing Crew Manager...")
        crew_manager = ConfluenceCrewManager()
        print("✅ Crew Manager initialized successfully!")
        
        # Example 1: List available spaces
        print("\n🔍 Example 1: Listing available Confluence spaces...")
        try:
            spaces = crew_manager.get_available_spaces()
            if spaces:
                print("Available spaces:")
                for space in spaces[:5]:  # Show first 5 spaces
                    print(f"  • {space['key']}: {space['name']}")
                if len(spaces) > 5:
                    print(f"  ... and {len(spaces) - 5} more spaces")
            else:
                print("No spaces found or unable to connect to Confluence.")
        except Exception as e:
            print(f"⚠️  Warning: Could not list spaces - {e}")
        
        # Example 2: Demonstrate scraping workflow (without actually running)
        print("\n📚 Example 2: Scraping workflow demonstration...")
        print("To scrape a Confluence space, you would use:")
        print("  crew_manager.create_scraping_crew('SPACE_KEY')")
        print("  result = scraping_crew.kickoff()")
        
        # Example 3: Demonstrate query workflow
        print("\n❓ Example 3: Query workflow demonstration...")
        print("To query scraped content, you would use:")
        print("  crew_manager.create_query_crew('Your question here')")
        print("  answer = query_crew.kickoff()")
        
        # Example 4: Demonstrate document generation
        print("\n📄 Example 4: Document generation demonstration...")
        print("To generate a document, you would use:")
        print("  crew_manager.create_document_generation_crew('Content summary', 'pdf')")
        print("  document = doc_crew.kickoff()")
        
        # Example 5: Full workflow
        print("\n🔄 Example 5: Full workflow demonstration...")
        print("To run the complete workflow, you would use:")
        print("  crew_manager.run_full_workflow('SPACE_KEY', 'Your question', True)")
        
        print("\n" + "=" * 50)
        print("💡 Tips for using the system:")
        print("1. Start with --interactive mode: python main.py --interactive")
        print("2. Always verify your .env configuration before running")
        print("3. Test with a small space first")
        print("4. Monitor the output directory for generated files")
        print("5. Use the logging system for debugging")
        
        print("\n🎯 Ready to use! Run 'python main.py --help' for command options.")
        
    except Exception as e:
        print(f"❌ Error during example execution: {e}")
        print("Please check your configuration and ensure all dependencies are installed.")
        return 1
    
    return 0

def demonstrate_config():
    """Demonstrate configuration validation."""
    print("\n⚙️  Configuration Check:")
    print("-" * 30)
    
    try:
        config = Config()
        print("✅ Configuration loaded successfully")
        
        # Check if configuration is valid
        try:
            config.validate()
            print("✅ Configuration validation passed")
        except ValueError as e:
            print(f"⚠️  Configuration validation failed: {e}")
            print("   Please check your .env file")
        
        # Show current configuration (without sensitive data)
        print(f"📁 Output directory: {config.OUTPUT_DIR}")
        print(f"📁 Temp directory: {config.TEMP_DIR}")
        print(f"🔢 Max pages per space: {config.MAX_PAGES_PER_SPACE}")
        print(f"📎 Include attachments: {config.INCLUDE_ATTACHMENTS}")
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")

if __name__ == "__main__":
    print("🔧 Running configuration check...")
    demonstrate_config()
    
    print("\n🚀 Running example usage...")
    exit_code = main()
    sys.exit(exit_code)
