#!/bin/bash

echo "🚀 Starting Model Dashboard..."

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    echo "Please install Docker and make sure it's running"
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed or not in PATH"
    echo "Please install docker-compose"
    exit 1
fi

# Create necessary directories
mkdir -p models data

echo "📦 Building and starting containers..."
docker-compose up --build

echo "✅ Model Dashboard should be available at:"
echo "   🌐 Web Dashboard: http://localhost:8000"
echo "   🤖 OpenAI API: http://localhost:8000/v1"