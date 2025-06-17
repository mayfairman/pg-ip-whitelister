#!/bin/bash

# PG IP Whitelister Deployment Script
set -e

echo "🚀 Deploying PG IP Whitelister..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file with your configuration:"
    echo ""
    echo "PANGOLIN_API_URL=your-local-ip-of-the-pangolin-api"
    echo "PANGOLIN_API_KEY=your-api-key"
    echo "PANGOLIN_ORG_ID=your-org-id"
    echo "SECRET_KEY=your-secret-key"
    echo "FLASK_ENV=production"
    echo "LOG_LEVEL=INFO"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Build the Docker image
echo "📦 Building Docker image..."
docker build -t pg-ip-whitelister .

# Stop and remove existing container if it exists
echo "🛑 Stopping existing container..."
docker stop pg-ip-whitelister 2>/dev/null || true
docker rm pg-ip-whitelister 2>/dev/null || true

# Run the container
echo "🚀 Starting container..."
docker run -d \
    --name pg-ip-whitelister \
    --env-file .env \
    -p 5000:5000 \
    -v $(pwd)/logs:/app/logs \
    --restart unless-stopped \
    pg-ip-whitelister

# Wait for container to start
echo "⏳ Waiting for container to start..."
sleep 5

# Check container status
if docker ps | grep -q pg-ip-whitelister; then
    echo "✅ Container is running!"
    echo "🌐 Application is available at: http://localhost:5000"
    echo "📊 Container logs: docker logs pg-ip-whitelister"
    echo "🛑 To Stop container: docker stop pg-ip-whitelister"
else
    echo "❌ Container failed to start!"
    echo "📋 Container logs:"
    docker logs pg-ip-whitelister
    exit 1
fi 