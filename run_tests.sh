#!/bin/bash

# Test runner script for PG IP Whitelister
set -e

echo "🧪 Running tests for PG IP Whitelister..."

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Warning: Not in a virtual environment"
fi

# Install test dependencies if needed
echo "📦 Installing test dependencies..."
uv pip install -e ".[dev]"

# Run tests with different options
case "${1:-all}" in
    "unit")
        echo "🔬 Running unit tests..."
        uv run pytest tests/ -m "not integration" -v
        ;;
    "integration")
        echo "🔗 Running integration tests..."
        uv run pytest tests/ -m "integration" -v
        ;;
    "coverage")
        echo "📊 Running tests with coverage..."
        uv run pytest tests/ --cov=app --cov-report=html --cov-report=term-missing
        ;;
    "fast")
        echo "⚡ Running fast tests..."
        uv run pytest tests/ -m "not slow" -v
        ;;
    "all")
        echo "🎯 Running all tests..."
        uv run pytest tests/ -v
        ;;
    "lint")
        echo "🔍 Running linting..."
        uv run flake8 app/ tests/
        uv run black --check app/ tests/
        uv run mypy app/
        ;;
    "format")
        echo "🎨 Formatting code..."
        uv run black app/ tests/
        ;;
    *)
        echo "Usage: $0 {unit|integration|coverage|fast|all|lint|format}"
        echo ""
        echo "Options:"
        echo "  unit       - Run unit tests only"
        echo "  integration - Run integration tests only"
        echo "  coverage   - Run tests with coverage report"
        echo "  fast       - Run fast tests (exclude slow ones)"
        echo "  all        - Run all tests (default)"
        echo "  lint       - Run linting and type checking"
        echo "  format     - Format code with black"
        exit 1
        ;;
esac

echo "✅ Tests completed!"
