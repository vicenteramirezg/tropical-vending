# Tropical Vending - Docker Deployment Guide

This guide explains how the application is now configured for automatic frontend building and deployment on Railway.

## Overview

The application now uses a single Docker container that:
1. Builds the Vue.js frontend during the Docker build process
2. Serves the built frontend through Django's static file serving
3. Runs the Django backend API
4. Handles database migrations automatically

## Files Created/Modified

### New Files:
- `Dockerfile` - Multi-stage build that installs dependencies, builds frontend, and sets up the backend
- `railway.json` - Railway configuration for Docker-based deployment
- `entrypoint.sh` - Script that runs migrations and starts the server
- `post-deploy.sh` - Additional post-deployment tasks (if needed)
- `Procfile` - Backup deployment method for Railway
- `.dockerignore` - Optimizes Docker build by excluding unnecessary files
- `test-docker-build.ps1` - Local testing script for the Docker build

### Modified Files:
- `backend/templates/index.html` - Updated to work with the built Vue.js assets

## How It Works

### Build Process:
1. **Base Image**: Uses Python 3.9 slim with Node.js and npm installed
2. **Python Dependencies**: Installs requirements.txt
3. **Frontend Build**: 
   - Runs `npm install` in the frontend directory
   - Runs `npm run build` which builds to `backend/static/` (configured in vite.config.js)
   - Copies the built index.html to Django templates
4. **Static Files**: Runs Django's `collectstatic` to prepare all static files
5. **Server Start**: Uses gunicorn to serve the Django application

### Runtime Process:
1. **Migrations**: Automatically applies database migrations
2. **Server**: Starts gunicorn server bound to Railway's PORT
3. **Static Serving**: Django serves the built Vue.js app and API endpoints

## Deployment to Railway

### First-time Setup:
1. Push all files to your repository
2. In Railway, create a new project from your GitHub repository
3. Railway will automatically detect the `railway.json` and use the Dockerfile
4. Set environment variables in Railway dashboard:
   - `SECRET_KEY` - Django secret key
   - `DATABASE_URL` - Will be automatically provided by Railway if you add a database
   - `ALLOWED_HOSTS` - Your Railway domain
   - Any other environment variables from your `.env` file

### Subsequent Deployments:
1. Make your changes to frontend or backend
2. Commit and push to your repository
3. Railway will automatically build and deploy the new version
4. The frontend will be built fresh each time, so no need to build locally

## Local Testing

To test the Docker build locally:

```powershell
# Run the test script
.\test-docker-build.ps1

# Or manually:
docker build -t tropical-vending-test .
docker run -p 8000:8000 -e PORT=8000 tropical-vending-test
```

## Key Benefits

1. **Simplified Deployment**: No need to build frontend locally
2. **Consistent Environment**: Same environment in development and production
3. **Automatic Builds**: Frontend is built fresh on each deployment
4. **Single Service**: Everything runs in one container, reducing complexity
5. **Static File Optimization**: Whitenoise handles static file serving efficiently

## Troubleshooting

### Build Issues:
- Check that all dependencies are in `requirements.txt`
- Ensure `frontend/package.json` has correct build scripts
- Verify `vite.config.js` builds to the correct directory

### Runtime Issues:
- Check Railway logs for detailed error messages
- Ensure environment variables are set correctly
- Verify database connection if using external database

### Frontend Issues:
- Check that `backend/static/` contains the built Vue.js files
- Verify that `backend/templates/index.html` is being served correctly
- Check browser network tab for 404 errors on static assets

## Environment Variables

Required environment variables for production:
- `SECRET_KEY` - Django secret key
- `DATABASE_URL` - Database connection string (optional, defaults to SQLite)
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts
- `PORT` - Server port (automatically set by Railway)

Optional environment variables:
- `DEBUG` - Set to False for production (defaults to True)
- `CORS_ALLOWED_ORIGINS` - Comma-separated list of allowed CORS origins 