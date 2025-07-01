FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    nodejs \
    npm \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

# Build frontend
WORKDIR /app/frontend
RUN npm install
RUN npm run build

# Go back to main directory
WORKDIR /app

# Create necessary directories
RUN mkdir -p backend/staticfiles
RUN mkdir -p backend/static

# The Vue.js build output is already in backend/static due to vite.config.js
# Copy the built index.html to templates directory so Django can serve it
RUN cp backend/static/index.html backend/templates/index.html

# Collect static files
WORKDIR /app/backend
RUN python manage.py collectstatic --noinput

# Go back to main directory
WORKDIR /app

# Expose port
EXPOSE 8000

# Use entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"] 