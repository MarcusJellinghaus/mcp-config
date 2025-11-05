#!/bin/bash
# Format all code with black and isort

set -e  # Exit on error

echo "======================================"
echo "Running code formatters..."
echo "======================================"

# Run black
echo ""
echo "Running black..."
black src tests
echo "black formatting complete."

# Run isort
echo ""
echo "Running isort..."
isort . --profile black --line-length 88
echo "isort formatting complete."

echo ""
echo "======================================"
echo "All formatting complete!"
echo "======================================"
