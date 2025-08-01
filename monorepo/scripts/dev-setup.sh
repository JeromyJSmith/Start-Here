#!/bin/bash
# Development setup script for Claude Code Monorepo

set -e

echo "🚀 Claude Code Monorepo Development Setup"
echo "=========================================="

# Check dependencies
echo "📋 Checking dependencies..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is required but not installed."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is required but not installed."  
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "⚠️  Node.js not found. Installing via Docker..."
else
    NODE_VERSION=$(node -v)
    echo "✅ Node.js found: $NODE_VERSION"
fi

if ! command -v pnpm &> /dev/null; then
    echo "⚠️  pnpm not found. Installing..."
    npm i -g pnpm
else
    PNPM_VERSION=$(pnpm -v)
    echo "✅ pnpm found: $PNPM_VERSION"
fi

if ! command -v python3 &> /dev/null; then
    echo "⚠️  Python not found. Using Docker..."
else
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Python found: $PYTHON_VERSION"
fi

# Setup environment
echo ""
echo "🔧 Setting up environment..."

if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file"
else
    echo "ℹ️  .env file already exists"
fi

# Create directories
echo "📁 Creating directories..."
mkdir -p volumes/{postgres,redis,ollama,logs}
mkdir -p docker/ssl
echo "✅ Directories created"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."

if command -v pnpm &> /dev/null; then
    echo "Installing Node.js dependencies..."
    pnpm install
    echo "✅ Node.js dependencies installed"
fi

# Build and start services
echo ""
echo "🏗️ Building and starting services..."
docker-compose build
docker-compose up -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 15

# Check service health
echo ""
echo "🏥 Checking service health..."
docker-compose ps

echo ""
echo "🎉 Setup complete!"
echo ""
echo "🌐 Service URLs:"
echo "  Frontend:     http://localhost:5173"
echo "  Backend:      http://localhost:3000"  
echo "  SuperClaude:  http://localhost:8001"
echo "  GenAI Stack:  http://localhost:8003"
echo "  CLI Tool:     http://localhost:3001"
echo "  n8n:          http://localhost:5678"
echo "  Ollama:       http://localhost:11434"
echo ""
echo "🔧 Useful commands:"
echo "  make logs        - View all logs"
echo "  make health      - Check service health"
echo "  make stop        - Stop all services"
echo "  make shell-*     - Access service shells"
echo ""
echo "📚 See README.md for detailed documentation"