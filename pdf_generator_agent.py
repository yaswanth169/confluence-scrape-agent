from crewai import Agent
from crewai.tools import BaseTool
from typing import Dict, List, Any
import json
import os
from config import Config
import pandas as pd

class PDFGeneratorAgent:
    """Crew AI Agent for generating PDF documents from scraped content."""
    
    def __init__(self):
        self.config = Config()
    
    def create_agent(self) -> Agent:
        """Create the PDF Generator Agent."""
        return Agent(
            role='Document Generation Specialist',
            goal='Create well-formatted documents from Confluence content',
            backstory="""You are an expert in document creation with a keen eye for formatting, 
            structure, and presentation. You specialize in transforming raw Confluence data into 
            professional, polished documents such as PDFs or Markdown files. Your documents are 
            clear, organized, and visually appealing.""",
            verbose=True,
            allow_delegation=False,
            tools=[
                PDFGeneratorTool(),
                MarkdownGeneratorTool(),
                ContentStructureTool()
            ]
        )

class PDFGeneratorTool(BaseTool):
    """Tool for generating PDF documents from content."""
    
    name = "PDF Document Generator"
    description = "Creates a formatted PDF document from Confluence content data."
    
    def __init__(self):
        super().__init__()
    
    def _run(self, content_data: str, output_filename: str, output_dir: str = None) -> str:
        """Generate a PDF document from content data."""
        try:
            if output_dir is None:
                output_dir = Config.OUTPUT_DIR
            
            # Parse content data
            content = json.loads(content_data) if content_data.startswith("{") or content_data.startswith("[") else {"content": content_data}
            
            # Placeholder for PDF generation logic
            output_path = os.path.join(output_dir, f"{output_filename}.pdf")
            os.makedirs(output_dir, exist_ok=True)
            
            # Here you would use a library like reportlab or pdfkit to create the PDF
            # For now, we'll simulate it
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("This is a placeholder PDF content for: " + output_filename)
            
            return f"PDF generated successfully at: {output_path}"
        except Exception as e:
            return f"Error generating PDF: {str(e)}"

class MarkdownGeneratorTool(BaseTool):
    """Tool for generating Markdown documents from content."""
    
    name = "Markdown Document Generator"
    description = "Creates a formatted Markdown document from Confluence content data."
    
    def __init__(self):
        super().__init__()
    
    def _run(self, content_data: str, output_filename: str, output_dir: str = None) -> str:
        """Generate a Markdown document from content data."""
        try:
            if output_dir is None:
                output_dir = Config.OUTPUT_DIR
            
            # Parse content data
            content = json.loads(content_data) if content_data.startswith("{") or content_data.startswith("[") else {"content": content_data}
            
            output_path = os.path.join(output_dir, f"{output_filename}.md")
            os.makedirs(output_dir, exist_ok=True)
            
            # Basic Markdown conversion (placeholder for real HTML-to-Markdown conversion)
            markdown_content = "# Confluence Content\n\n"
            if isinstance(content, dict):
                if 'title' in content:
                    markdown_content += f"## {content.get('title')}\n\n"
                if 'content' in content:
                    markdown_content += content.get('content', 'No content available')
                elif 'content_snippet' in content:
                    markdown_content += content.get('content_snippet', 'No content available')
            else:
                markdown_content += str(content)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            return f"Markdown document generated successfully at: {output_path}"
        except Exception as e:
            return f"Error generating Markdown: {str(e)}"

class ContentStructureTool(BaseTool):
    """Tool for structuring content for document generation."""
    
    name = "Content Structurer"
    description = "Analyzes and structures Confluence content in preparation for document generation."
    
    def __init__(self):
        super().__init__()
    
    def _run(self, content_data: str, structure_type: str = "standard") -> str:
        """Structure content for document generation."""
        try:
            # Parse content data
            content = json.loads(content_data) if content_data.startswith("{") or content_data.startswith("[") else {"content": content_data}
            
            # Create a structured representation based on structure_type
            structured_content = {
                "structure_type": structure_type,
                "original_content": content,
                "sections": []
            }
            
            if structure_type == "standard":
                if isinstance(content, dict):
                    if 'title' in content:
                        structured_content["sections"].append({
                            "type": "header",
                            "level": 1,
                            "text": content.get('title')
                        })
                    if 'content' in content:
                        structured_content["sections"].append({
                            "type": "body",
                            "text": content.get('content')
                        })
            elif structure_type == "detailed":
                # More complex structuring logic could be added here
                structured_content["sections"].append({
                    "type": "body",
                    "text": str(content)
                })
            
            return json.dumps(structured_content, indent=2)
        except Exception as e:
            return f"Error structuring content: {str(e)}"
