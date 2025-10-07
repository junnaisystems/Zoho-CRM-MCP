# Run Zoho CRM MCP Server with your personal configuration

Write-Host "Starting Zoho CRM MCP Server with your personal configuration..." -ForegroundColor Cyan

# Copy personal config to .env for this run
if (Test-Path ".env.personal") {
    Copy-Item ".env.personal" ".env" -Force
    Write-Host "✓ Personal configuration loaded" -ForegroundColor Green
} else {
    Write-Host "✗ .env.personal file not found!" -ForegroundColor Red
    Write-Host "Please make sure .env.personal exists with your credentials." -ForegroundColor Yellow
    exit 1
}

# Run the server
Write-Host "Starting MCP server..." -ForegroundColor Blue
python src/server.py