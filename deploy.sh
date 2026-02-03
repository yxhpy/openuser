#!/bin/bash

# OpenUser Docker Deployment Script
# This script helps you deploy OpenUser using Docker Compose

set -e

echo "🚀 OpenUser Docker Deployment"
echo "=============================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed"
    echo "Please install Docker from https://www.docker.com/get-started"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed"
    echo "Please install Docker Compose"
    exit 1
fi

# Check if .env file exists, if not copy from .env.docker
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.docker..."
    cp .env.docker .env
    echo "⚠️  Please edit .env file and update the following:"
    echo "   - POSTGRES_PASSWORD (change from default)"
    echo "   - JWT_SECRET_KEY (generate a secure random key)"
    echo ""
    read -p "Press Enter to continue after updating .env file..."
fi

# Create required directories
echo "📁 Creating required directories..."
mkdir -p data models cache uploads

# Build and start services
echo ""
echo "🔨 Building Docker images..."
docker-compose build

echo ""
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service status
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📍 Access Points:"
echo "   - API Server: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Health Check: http://localhost:8000/health"
echo ""
echo "📝 Useful Commands:"
echo "   - View logs: docker-compose logs -f"
echo "   - Stop services: docker-compose stop"
echo "   - Restart services: docker-compose restart"
echo "   - Remove services: docker-compose down"
echo "   - Remove with data: docker-compose down -v"
echo ""
