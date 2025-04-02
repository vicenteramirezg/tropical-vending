# Change to frontend directory
Set-Location -Path "frontend"

# Install dependencies
Write-Host "Installing frontend dependencies..."
npm install

# Start development server
Write-Host "Starting frontend development server..."
npm run dev 