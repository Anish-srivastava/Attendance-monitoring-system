#!/bin/bash
# Build script for Render deployment

set -e  # Exit on any error

echo "🔧 Starting build process..."

# Upgrade pip first
python -m pip install --upgrade pip

# Install requirements
echo "📦 Installing Python packages..."
python -m pip install -r requirements.txt

# Verify gunicorn installation
echo "✅ Verifying gunicorn installation..."
python -c "import gunicorn; print(f'Gunicorn version: {gunicorn.__version__}')"

echo "🎉 Build completed successfully!"