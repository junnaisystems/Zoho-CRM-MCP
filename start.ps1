# Zoho CRM MCP Server Startup Script
# This script sets up and starts the Zoho CRM MCP server

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    Zoho CRM MCP Server Startup" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.9 or higher." -ForegroundColor Red
    exit 1
}

# Check if .env file exists
if (!(Test-Path ".env")) {
    Write-Host "⚠ .env file not found!" -ForegroundColor Yellow
    Write-Host "Please copy .env.example to .env and configure your Zoho credentials." -ForegroundColor Yellow
    
    if (Test-Path ".env.example") {
        Write-Host ""
        Write-Host "Running: Copy-Item .env.example .env" -ForegroundColor Blue
        Copy-Item .env.example .env
        Write-Host "✓ Created .env file from template" -ForegroundColor Green
        Write-Host ""
        Write-Host "Please edit .env file with your Zoho CRM credentials:" -ForegroundColor Yellow
        Write-Host "- ZOHO_CLIENT_ID=your_client_id" -ForegroundColor Yellow
        Write-Host "- ZOHO_CLIENT_SECRET=your_client_secret" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Press any key to open .env file for editing..." -ForegroundColor Cyan
        Read-Host
        notepad .env
        Write-Host ""
        Write-Host "After editing .env, press any key to continue..." -ForegroundColor Cyan
        Read-Host
    } else {
        Write-Host "✗ .env.example file not found either!" -ForegroundColor Red
        exit 1
    }
}

# Check if virtual environment should be created
if (!(Test-Path "venv") -and !(Test-Path ".venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Blue
    python -m venv venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Virtual environment created" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}

# Activate virtual environment
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Blue
    & "venv\Scripts\Activate.ps1"
    Write-Host "✓ Virtual environment activated" -ForegroundColor Green
} elseif (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Blue
    & ".venv\Scripts\Activate.ps1"
    Write-Host "✓ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "⚠ No virtual environment activation script found, continuing..." -ForegroundColor Yellow
}

# Install dependencies
if (Test-Path "requirements.txt") {
    Write-Host "Installing dependencies..." -ForegroundColor Blue
    pip install -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "⚠ requirements.txt not found, skipping dependency installation" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    Starting Zoho CRM MCP Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start the server
try {
    python src/server.py
} catch {
    Write-Host ""
    Write-Host "✗ Server failed to start" -ForegroundColor Red
    Write-Host "Check the error messages above for details." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "1. Missing or incorrect .env configuration" -ForegroundColor Yellow
    Write-Host "2. Network connectivity issues" -ForegroundColor Yellow
    Write-Host "3. Invalid Zoho CRM credentials" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press any key to exit..." -ForegroundColor Cyan
    Read-Host
    exit 1
}