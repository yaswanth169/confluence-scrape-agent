#!/usr/bin/env pwsh
# PowerShell script for running the Confluence Scraper Agent System
# This script provides various execution modes and dependency checking

param(
    [Parameter(Position=0)]
    [ValidateSet("interactive", "test", "scrape", "query", "generate", "status", "llama", "help")]
    [string]$Mode = "interactive",
    
    [Parameter(Position=1)]
    [string]$Argument = ""
)

# Function to check if Python is installed
function Test-Python {
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
            return $true
        }
    }
    catch {
        Write-Host "❌ Python not found" -ForegroundColor Red
        return $false
    }
    return $false
}

# Function to check if pip is available
function Test-Pip {
    try {
        $pipVersion = pip --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ pip found: $pipVersion" -ForegroundColor Green
            return $true
        }
    }
    catch {
        Write-Host "❌ pip not found" -ForegroundColor Red
        return $false
    }
    return $false
}

# Function to install dependencies
function Install-Dependencies {
    Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
    try {
        pip install -r requirements.txt
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "❌ Error installing dependencies: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to check if .env file exists
function Test-EnvironmentFile {
    if (Test-Path ".env") {
        Write-Host "✅ .env file found" -ForegroundColor Green
        return $true
    } else {
        Write-Host "⚠️ .env file not found" -ForegroundColor Yellow
        Write-Host "📝 Creating .env file from template..." -ForegroundColor Yellow
        
        if (Test-Path "env_example.txt") {
            Copy-Item "env_example.txt" ".env"
            Write-Host "✅ .env file created from template" -ForegroundColor Green
            Write-Host "⚠️ Please edit .env file with your actual credentials" -ForegroundColor Yellow
            return $true
        } else {
            Write-Host "❌ env_example.txt not found" -ForegroundColor Red
            return $false
        }
    }
}

# Function to show help
function Show-Help {
    Write-Host @"
🤖 Confluence Scraper Agent System - PowerShell Runner
=======================================================

Usage: .\run.ps1 [Mode] [Argument]

Modes:
  interactive  - Run in interactive mode (default)
  test         - Run system tests
  scrape       - Scrape a Confluence space
  query        - Query scraped content
  generate     - Generate document from content
  status       - Show system status
  llama        - Test LLaMA model directly
  help         - Show this help message

Examples:
  .\run.ps1                           # Interactive mode
  .\run.ps1 test                     # Run tests
  .\run.ps1 scrape SPACE_KEY         # Scrape specific space
  .\run.ps1 query "your question"    # Query content
  .\run.ps1 llama                    # Test LLaMA model
  .\run.ps1 status                   # Show system status

Features:
  - Uses Crew AI framework with local LLaMA model
  - Scrapes Confluence data via API
  - Generates intelligent responses using LLaMA
  - Creates professional documents
  - Works entirely offline for privacy

"@ -ForegroundColor Cyan
}

# Function to run the system
function Start-System {
    param(
        [string]$Mode,
        [string]$Argument = ""
    )
    
    Write-Host "🚀 Starting Confluence Scraper Agent System..." -ForegroundColor Green
    Write-Host "🤖 Mode: $Mode" -ForegroundColor Yellow
    
    $command = "python main.py"
    
    switch ($Mode) {
        "interactive" { $command += " --interactive" }
        "test" { $command += " --test" }
        "scrape" { 
            if ($Argument) {
                $command += " --scrape-space $Argument"
            } else {
                Write-Host "❌ Space key required for scrape mode" -ForegroundColor Red
                Write-Host "Usage: .\run.ps1 scrape SPACE_KEY" -ForegroundColor Yellow
                return
            }
        }
        "query" { 
            if ($Argument) {
                $command += " --query `"$Argument`""
            } else {
                Write-Host "❌ Query required for query mode" -ForegroundColor Red
                Write-Host "Usage: .\run.ps1 query `"your question`"" -ForegroundColor Yellow
                return
            }
        }
        "generate" { 
            if ($Argument) {
                $command += " --generate-doc `"$Argument`""
            } else {
                Write-Host "❌ Content required for generate mode" -ForegroundColor Red
                Write-Host "Usage: .\run.ps1 generate `"content summary`"" -ForegroundColor Yellow
                return
            }
        }
        "status" { $command += " --status" }
        "llama" { 
            Write-Host "🧪 Testing LLaMA model directly..." -ForegroundColor Yellow
            $command = "python example_llama_usage.py"
        }
        default { 
            Write-Host "❌ Unknown mode: $Mode" -ForegroundColor Red
            Show-Help
            return
        }
    }
    
    Write-Host "🔧 Executing: $command" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Gray
    
    try {
        Invoke-Expression $command
    }
    catch {
        Write-Host "❌ Error executing command: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Main execution
Write-Host "🤖 Confluence Scraper Agent System - PowerShell Runner" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Gray

# Check if help is requested
if ($Mode -eq "help") {
    Show-Help
    exit 0
}

# Check Python installation
Write-Host "🔍 Checking Python installation..." -ForegroundColor Yellow
if (-not (Test-Python)) {
    Write-Host "❌ Python is required but not found" -ForegroundColor Red
    Write-Host "💡 Please install Python 3.8+ from https://python.org" -ForegroundColor Yellow
    exit 1
}

# Check pip installation
Write-Host "🔍 Checking pip installation..." -ForegroundColor Yellow
if (-not (Test-Pip)) {
    Write-Host "❌ pip is required but not found" -ForegroundColor Red
    Write-Host "💡 Please ensure pip is installed with Python" -ForegroundColor Yellow
    exit 1
}

# Check if requirements.txt exists
if (-not (Test-Path "requirements.txt")) {
    Write-Host "❌ requirements.txt not found" -ForegroundColor Red
    Write-Host "💡 Please ensure you're in the correct directory" -ForegroundColor Yellow
    exit 1
}

# Check if main.py exists
if (-not (Test-Path "main.py")) {
    Write-Host "❌ main.py not found" -ForegroundColor Red
    Write-Host "💡 Please ensure you're in the correct directory" -ForegroundColor Yellow
    exit 1
}

# Check environment file
Write-Host "🔍 Checking environment configuration..." -ForegroundColor Yellow
if (-not (Test-EnvironmentFile)) {
    Write-Host "❌ Environment configuration failed" -ForegroundColor Red
    exit 1
}

# Install dependencies if needed
Write-Host "🔍 Checking dependencies..." -ForegroundColor Yellow
try {
    $testImport = python -c "import crewai, torch, transformers" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️ Some dependencies missing, installing..." -ForegroundColor Yellow
        if (-not (Install-Dependencies)) {
            Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "✅ All dependencies are available" -ForegroundColor Green
    }
}
catch {
    Write-Host "⚠️ Dependency check failed, installing..." -ForegroundColor Yellow
    if (-not (Install-Dependencies)) {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
}

# Start the system
Write-Host "✅ All checks passed!" -ForegroundColor Green
Start-System -Mode $Mode -Argument $Argument

Write-Host "`n👋 Script completed" -ForegroundColor Cyan
