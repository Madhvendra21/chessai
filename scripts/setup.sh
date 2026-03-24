#!/bin/bash

set -e

echo "🚀 Setting up ChessVision AI..."

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
if (( $(echo "$PYTHON_VERSION < 3.9" | bc -l) )); then
    echo "❌ Python 3.9+ required, found $PYTHON_VERSION"
    exit 1
fi

echo "✓ Python version OK"

# Create directories
mkdir -p data/{uploads,frames,models}
echo "✓ Created data directories"

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Check Stockfish
if command -v stockfish &> /dev/null; then
    echo "✓ Stockfish found"
else
    echo "⚠️  Stockfish not found. Please install it:"
    echo "   Mac: brew install stockfish"
    echo "   Ubuntu: sudo apt-get install stockfish"
    echo "   Or download from: https://stockfishchess.org/download/"
fi

# Setup frontend
echo "📦 Setting up frontend..."
cd frontend
if ! command -v npm &> /dev/null; then
    echo "❌ Node.js/npm not found. Please install Node.js 18+"
    exit 1
fi
npm install
cd ..

# Copy environment file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created .env file from template"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Start PostgreSQL and Redis (or use Docker: docker-compose up -d postgres redis)"
echo "2. Start backend: cd backend && python -m uvicorn api.main:app --reload"
echo "3. Start worker: cd backend && celery -A workers.tasks worker --loglevel=info"
echo "4. Start frontend: cd frontend && npm run dev"
echo ""
echo "Or use Docker Compose: docker-compose up --build"