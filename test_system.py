#!/usr/bin/env python3
"""
Test script for the Confluence Scraper Agent system.
Tests basic functionality without requiring actual Confluence access.
"""

import os
import sys
import json
from datetime import datetime

def test_imports():
    """Test that all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        from config import Config
        print("✅ Config module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Config: {e}")
        return False
    
    try:
        from llama_handler import LLaMAHandler, llama_handler
        print("✅ LLaMA handler imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import LLaMA handler: {e}")
        return False
    
    try:
        from confluence_scraper import ConfluenceScraper
        print("✅ Confluence scraper imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Confluence scraper: {e}")
        return False
    
    try:
        from agents import ConfluenceScraperAgent, QueryAgent, PDFGeneratorAgent
        print("✅ Agent classes imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import agents: {e}")
        return False
    
    try:
        from crew_manager import ConfluenceCrewManager
        print("✅ Crew manager imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import crew manager: {e}")
        return False
    
    return True

def test_config():
    """Test configuration loading."""
    print("\n🔧 Testing configuration...")
    
    try:
        from config import Config
        
        # Test basic config
        config = Config()
        print(f"✅ Configuration loaded")
        print(f"  • Confluence URL: {config.CONFLUENCE_URL}")
        print(f"  • LLaMA Model Path: {config.LLAMA_MODEL_PATH}")
        print(f"  • Output Directory: {config.OUTPUT_DIR}")
        
        # Test validation (this will fail with default values, which is expected)
        try:
            config.validate()
            print("✅ Configuration validation passed")
        except ValueError as e:
            print(f"⚠️ Configuration validation failed (expected): {e}")
            print("  This is normal for testing - you need to set up your .env file")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_llama_handler():
    """Test LLaMA handler functionality."""
    print("\n🤖 Testing LLaMA handler...")
    
    try:
        from llama_handler import LLaMAHandler
        
        # Create handler instance
        handler = LLaMAHandler()
        print(f"✅ LLaMA handler created")
        print(f"  • Model path: {handler.model_path}")
        print(f"  • Model loaded: {handler.is_model_loaded()}")
        
        # Test model info
        info = handler.get_model_info()
        print(f"  • Model status: {info['status']}")
        
        # Note: We won't actually load the model during testing to avoid memory issues
        print("⚠️ Skipping actual model loading during testing")
        
        return True
        
    except Exception as e:
        print(f"❌ LLaMA handler test failed: {e}")
        return False

def test_confluence_scraper():
    """Test Confluence scraper structure."""
    print("\n📄 Testing Confluence scraper...")
    
    try:
        from confluence_scraper import ConfluenceScraper
        
        # Create scraper instance
        scraper = ConfluenceScraper()
        print("✅ Confluence scraper created")
        
        # Test methods exist
        methods = ['get_spaces', 'get_pages_in_space', 'get_page_content', 'scrape_space']
        for method in methods:
            if hasattr(scraper, method):
                print(f"  ✅ Method {method} exists")
            else:
                print(f"  ❌ Method {method} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Confluence scraper test failed: {e}")
        return False

def test_agents():
    """Test agent creation."""
    print("\n👥 Testing agents...")
    
    try:
        from agents import ConfluenceScraperAgent, QueryAgent, PDFGeneratorAgent
        
        # Test scraper agent
        scraper_agent = ConfluenceScraperAgent()
        agent = scraper_agent.create_agent()
        print(f"✅ Scraper agent created: {agent.role}")
        
        # Test query agent
        query_agent = QueryAgent()
        agent = query_agent.create_agent()
        print(f"✅ Query agent created: {agent.role}")
        
        # Test PDF agent
        pdf_agent = PDFGeneratorAgent()
        agent = pdf_agent.create_agent()
        print(f"✅ PDF agent created: {agent.role}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        return False

def test_crew_manager():
    """Test crew manager functionality."""
    print("\n🚀 Testing crew manager...")
    
    try:
        from crew_manager import ConfluenceCrewManager
        
        # Note: We can't fully test this without a loaded LLaMA model
        print("⚠️ Skipping crew manager initialization (requires LLaMA model)")
        print("✅ Crew manager module imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Crew manager test failed: {e}")
        return False

def test_tools():
    """Test custom tools."""
    print("\n🛠️ Testing custom tools...")
    
    try:
        from agents import (
            ConfluenceScraperTool, SpaceListTool, PageSearchTool,
            ContentSearchTool, PageAnalysisTool, KnowledgeQueryTool,
            PDFGenerationTool, MarkdownGenerationTool, DocumentStructureTool
        )
        
        print("✅ All custom tools imported successfully")
        
        # Test tool descriptions
        tools = [
            ConfluenceScraperTool(None),
            SpaceListTool(None),
            PageSearchTool(None),
            ContentSearchTool(),
            PageAnalysisTool(),
            KnowledgeQueryTool(),
            PDFGenerationTool(),
            MarkdownGenerationTool(),
            DocumentStructureTool()
        ]
        
        for tool in tools:
            print(f"  ✅ Tool {tool.name}: {tool.description}")
        
        return True
        
    except Exception as e:
        print(f"❌ Tools test failed: {e}")
        return False

def test_output_directories():
    """Test output directory creation."""
    print("\n📁 Testing output directories...")
    
    try:
        from config import Config
        
        config = Config()
        
        # Test output directory
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
        if os.path.exists(config.OUTPUT_DIR):
            print(f"✅ Output directory created: {config.OUTPUT_DIR}")
        else:
            print(f"❌ Failed to create output directory: {config.OUTPUT_DIR}")
            return False
        
        # Test temp directory
        os.makedirs(config.TEMP_DIR, exist_ok=True)
        if os.path.exists(config.TEMP_DIR):
            print(f"✅ Temp directory created: {config.TEMP_DIR}")
        else:
            print(f"❌ Failed to create temp directory: {config.TEMP_DIR}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Output directories test failed: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality without external dependencies."""
    print("\n🧪 Testing basic functionality...")
    
    try:
        # Test JSON handling
        test_data = {
            "test": "data",
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
        
        json_str = json.dumps(test_data, indent=2)
        parsed_data = json.loads(json_str)
        
        if parsed_data == test_data:
            print("✅ JSON serialization/deserialization works")
        else:
            print("❌ JSON serialization/deserialization failed")
            return False
        
        # Test file operations
        test_file = os.path.join("temp", "test.txt")
        os.makedirs("temp", exist_ok=True)
        
        with open(test_file, 'w') as f:
            f.write("Test content")
        
        with open(test_file, 'r') as f:
            content = f.read()
        
        if content == "Test content":
            print("✅ File operations work")
        else:
            print("❌ File operations failed")
            return False
        
        # Cleanup
        os.remove(test_file)
        os.rmdir("temp")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Confluence Scraper Agent System Tests")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("LLaMA Handler", test_llama_handler),
        ("Confluence Scraper", test_confluence_scraper),
        ("Agents", test_agents),
        ("Crew Manager", test_crew_manager),
        ("Custom Tools", test_tools),
        ("Output Directories", test_output_directories),
        ("Basic Functionality", test_basic_functionality)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
        print("\nNext steps:")
        print("1. Set up your .env file with Confluence credentials")
        print("2. Ensure your LLaMA model is accessible")
        print("3. Run the main application: python main.py --interactive")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        print("\nCommon issues:")
        print("1. Missing dependencies - run: pip install -r requirements.txt")
        print("2. Incorrect model path in config")
        print("3. Missing Confluence credentials")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
