# Barclays Laptop Installation Script
# This script handles dependency installation with proper version management

Write-Host "🚀 Barclays Laptop Installation Script" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# Check Python version
Write-Host "🔍 Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python not found or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ and add to PATH" -ForegroundColor Red
    exit 1
}
Write-Host "✅ $pythonVersion" -ForegroundColor Green

# Check pip
Write-Host "🔍 Checking pip..." -ForegroundColor Yellow
$pipVersion = pip --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ pip not found" -ForegroundColor Red
    exit 1
}
Write-Host "✅ $pipVersion" -ForegroundColor Green

# Upgrade pip to latest stable version
Write-Host "📦 Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --user
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ Warning: pip upgrade failed, continuing with current version" -ForegroundColor Yellow
}

# Create virtual environment if it doesn't exist
$venvPath = "venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "🔧 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv $venvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✅ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& "$venvPath\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Virtual environment activated" -ForegroundColor Green

# Install core dependencies first (most stable)
Write-Host "📦 Installing core dependencies..." -ForegroundColor Yellow
$coreDeps = @(
    "python-dotenv==0.21.1",
    "requests==2.28.2",
    "pandas==1.5.3",
    "numpy==1.24.3"
)

foreach ($dep in $coreDeps) {
    Write-Host "Installing $dep..." -ForegroundColor Cyan
    pip install $dep
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️ Warning: Failed to install $dep" -ForegroundColor Yellow
    }
}

# Install PyTorch (CPU-only version for Barclays laptops)
Write-Host "🔥 Installing PyTorch (CPU version)..." -ForegroundColor Yellow
pip install torch==1.13.1+cpu torchvision==0.14.1+cpu torchaudio==0.13.1+cpu -f https://download.pytorch.org/whl/torch_stable.html
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ Warning: PyTorch installation failed, trying alternative..." -ForegroundColor Yellow
    pip install torch==1.13.1
}

# Install transformers and related packages
Write-Host "🤖 Installing LLaMA dependencies..." -ForegroundColor Yellow
$llamaDeps = @(
    "transformers==4.21.3",
    "accelerate==0.20.3",
    "sentencepiece==0.1.99",
    "protobuf==3.20.3"
)

foreach ($dep in $llamaDeps) {
    Write-Host "Installing $dep..." -ForegroundColor Cyan
    pip install $dep
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️ Warning: Failed to install $dep" -ForegroundColor Yellow
    }
}

# Install document processing
Write-Host "📄 Installing document processing..." -ForegroundColor Yellow
$docDeps = @(
    "PyPDF2==3.0.1",
    "python-docx==0.8.11"
)

foreach ($dep in $docDeps) {
    Write-Host "Installing $dep..." -ForegroundColor Cyan
    pip install $dep
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️ Warning: Failed to install $dep" -ForegroundColor Yellow
    }
}

# Install Crew AI framework
Write-Host "🤝 Installing Crew AI framework..." -ForegroundColor Yellow
pip install crewai==0.28.0
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ Warning: Crew AI installation failed" -ForegroundColor Yellow
}

# Install langchain
Write-Host "🔗 Installing LangChain..." -ForegroundColor Yellow
pip install langchain==0.1.0 langchain-openai==0.0.2
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ Warning: LangChain installation failed" -ForegroundColor Yellow
}

# Install remaining utilities
Write-Host "🛠️ Installing utilities..." -ForegroundColor Yellow
$utilDeps = @(
    "tqdm==4.64.1",
    "colorama==0.4.6",
    "scipy==1.10.1"
)

foreach ($dep in $utilDeps) {
    Write-Host "Installing $dep..." -ForegroundColor Cyan
    pip install $dep
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️ Warning: Failed to install $dep" -ForegroundColor Yellow
    }
}

# Install Confluence API
Write-Host "🌐 Installing Confluence API..." -ForegroundColor Yellow
pip install atlassian-python-api==3.41.0
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ Warning: Confluence API installation failed" -ForegroundColor Yellow
}

# Test installation
Write-Host "🧪 Testing installation..." -ForegroundColor Yellow
python -c "import torch; print(f'PyTorch version: {torch.__version__}')"
python -c "import transformers; print(f'Transformers version: {transformers.__version__}')"
python -c "import crewai; print(f'Crew AI version: {crewai.__version__}')"

Write-Host "✅ Installation completed!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Copy your .env file with Confluence credentials" -ForegroundColor White
Write-Host "2. Update LLAMA_MODEL_PATH in .env to point to your model" -ForegroundColor White
Write-Host "3. Run: python test_system.py" -ForegroundColor White
Write-Host "4. Run: python main.py --status" -ForegroundColor White

Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
