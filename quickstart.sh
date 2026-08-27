#!/bin/bash
# Quick Start Script for Sprout

echo "🌱 Sprout - Quick Start Setup"
echo "=============================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -q rich pydantic python-dotenv

echo "✓ Core dependencies installed"
echo ""
echo "Note: Voice features (Phase 2) dependencies skipped for now"
echo "      Install them later with: pip install -r requirements.txt"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your GEMINI_API_KEY (required for Phase 3)"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "=============================="
echo "✓ Setup Complete!"
echo ""
echo "Quick commands:"
echo "  python agent.py      - Start Sprout (interactive mode)"
echo "  python demo.py       - Run automated demo"
echo "  python test_sprout.py - Run test suite"
echo ""
echo "To use Sprout:"
echo "  source venv/bin/activate"
echo "  python agent.py"
echo ""
