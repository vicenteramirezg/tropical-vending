#!/bin/bash
# Deployment script for Tropical Vending project

# Stop on errors
set -e

echo -e "\033[32mStarting deployment process...\033[0m"

# Navigate to frontend directory and build
echo -e "\033[36mBuilding frontend...\033[0m"
pushd frontend
npm install || { echo -e "\033[31mnpm install failed!\033[0m"; exit 1; }
npm run build || { echo -e "\033[31mFrontend build failed!\033[0m"; exit 1; }
popd

# Ensure the backend/static directory exists (Vite is configured to output directly here)
echo -e "\033[36mChecking Vite build output...\033[0m"
if [ ! -d "backend/static" ]; then
    echo -e "\033[31mError: backend/static directory not found! Build may have failed.\033[0m"
    exit 1
fi

# Copy and modify the Vite-generated index.html file to use Django template tags
echo -e "\033[36mPreparing Django template for frontend...\033[0m"
if [ -f "backend/static/index.html" ]; then
    # Read index content
    INDEX_CONTENT=$(cat backend/static/index.html)
    
    # Apply replacements (using sed compatible with macOS)
    INDEX_CONTENT=$(echo "$INDEX_CONTENT" | sed 's|src="/assets/|src="{% static '\''assets/|g')
    INDEX_CONTENT=$(echo "$INDEX_CONTENT" | sed 's|href="/assets/|href="{% static '\''assets/|g')
    INDEX_CONTENT=$(echo "$INDEX_CONTENT" | sed 's|src="/\([^"]*\)"|src="{% static '\''\1'\'' %}"|g')
    INDEX_CONTENT=$(echo "$INDEX_CONTENT" | sed 's|href="/\([^"]*\)"|href="{% static '\''\1'\'' %}"|g')
    INDEX_CONTENT=$(echo "$INDEX_CONTENT" | sed 's|\.js"|\.js'\'' %}"|g')
    INDEX_CONTENT=$(echo "$INDEX_CONTENT" | sed 's|\.css"|\.css'\'' %}"|g')
    INDEX_CONTENT="{% load static %}"$'\n'"$INDEX_CONTENT"
    
    # Ensure templates directory exists
    mkdir -p backend/templates
    
    # Write the modified content to the Django template
    echo "$INDEX_CONTENT" > backend/templates/index.html
else
    echo -e "\033[31mError: backend/static/index.html not found! Build may have failed.\033[0m"
    exit 1
fi

# Create a custom index.html file for Railway deployment troubleshooting
mkdir -p backend/templates

cat > backend/templates/debug.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Debug - Tropical Vending</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
    h1 { color: #333; }
    .debug-info { background: #f4f4f4; padding: 15px; border-radius: 5px; }
    pre { background: #eee; padding: 10px; overflow: auto; }
  </style>
</head>
<body>
  <h1>Tropical Vending - Debug Page</h1>
  <div class="debug-info">
    <p>If you're seeing this page, the Django server is working but might be having trouble serving the Vue.js assets.</p>
    <p>Static URL: {{ STATIC_URL }}</p>
    <p>Available static files should be in: <code>/staticfiles/</code></p>
    <p>Try accessing: <a href="/static/assets/index.js">/static/assets/index.js</a></p>
  </div>
</body>
</html>
EOF

# Navigate to backend directory and collect static files
echo -e "\033[36mCollecting static files...\033[0m"
pushd backend
python manage.py collectstatic --noinput || { echo -e "\033[31mCollecting static files failed!\033[0m"; exit 1; }
popd

# Git operations
echo -e "\033[36mCommitting and pushing changes...\033[0m"

# Check git status before proceeding
git status

# Ask for confirmation
read -p "Proceed with committing and pushing these changes? (y/n): " confirm
if [[ $confirm != "y" && $confirm != "Y" ]]; then
    echo -e "\033[33mDeployment aborted by user.\033[0m"
    exit 0
fi

# Get commit message from parameter or use default
COMMIT_MESSAGE=${1:-"Deployment update"}

git add .
git commit -m "$COMMIT_MESSAGE" || { echo -e "\033[31mGit commit failed!\033[0m"; exit 1; }
git push origin main || { 
    echo -e "\033[31mGit push failed! Attempting to pull latest changes first...\033[0m"
    git pull origin main
    git push origin main || { echo -e "\033[31mGit push still failed after pulling. Please resolve conflicts manually.\033[0m"; exit 1; }
}

echo -e "\033[32mDeployment completed successfully!\033[0m" 