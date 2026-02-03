#!/bin/bash
# OpenUser Docker Deployment Script

set -e

echo "🚀 OpenUser Docker Deployment"
echo "=============================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.docker .env
    echo "⚠️  Please edit .env file and update the configuration values."
    echo "   Especially change the passwords and secret keys!"
    read -p "Press Enter to continue after editing .env file..."
fi

# Create required directories
echo "📁 Creating required directories..."
mkdir -p data models cache uploads

# Build Docker images
echo "🔨 Building Docker images..."
docker-compose build

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service health
echo "🏥 Checking service health..."
docker-compose ps

# Run database migrations
echo "📊 Running database migrations..."
docker-compose exec -T api alembic upgrade head

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Services:"
echo "  - API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - PostgreSQL: localhost:5432"
echo "  - Redis: localhost:6379"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop services:"
echo "  docker-compose down"
echo ""
