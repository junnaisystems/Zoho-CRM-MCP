# Run Zoho CRM MCP Server
# Note: Make sure you have configured your .env file with your Zoho credentials

Write-Host "Starting Zoho CRM MCP Server..." -ForegroundColor Cyan
Write-Host "Server location: $(Get-Location)" -ForegroundColor Gray

# Check if .env file exists with credentials
if (Test-Path ".env") {
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "your_client_id_here" -or $envContent -match "your_client_secret_here") {
        Write-Host "⚠ Please configure your .env file with your actual Zoho credentials" -ForegroundColor Yellow
        Write-Host "Edit .env and replace:" -ForegroundColor Yellow
        Write-Host "  - your_client_id_here with your actual Client ID" -ForegroundColor Yellow
        Write-Host "  - your_client_secret_here with your actual Client Secret" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Press any key to continue anyway, or Ctrl+C to cancel..." -ForegroundColor Cyan
        Read-Host
    } else {
        Write-Host "✓ Configuration file found" -ForegroundColor Green
    }
} else {
    Write-Host "✗ .env file not found!" -ForegroundColor Red
    Write-Host "Please copy .env.example to .env and configure your credentials." -ForegroundColor Yellow
    exit 1
}

# Run the server
Write-Host "Starting MCP server..." -ForegroundColor Blue
python src/server.py
