#!/bin/bash
# start.sh - Robust startup script for Render

set -e

echo "🚀 Starting Attendance Management System Backend..."

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ app.py not found in current directory"
    ls -la
    exit 1
fi

# Try to install gunicorn if it's missing
echo "📦 Checking gunicorn installation..."
if ! python -c "import gunicorn" 2>/dev/null; then
    echo "⚠️ Gunicorn not found, installing..."
    pip install gunicorn==20.1.0
fi

# Verify gunicorn is available
python -c "import gunicorn; print(f'✅ Gunicorn {gunicorn.__version__} is available')"

# Start with gunicorn
echo "🌟 Starting with gunicorn..."
exec python -m gunicorn app:app \
    --bind 0.0.0.0:${PORT:-10000} \
    --workers 1 \
    --timeout 120 \
    --preload \
    --log-level info \
    --access-logfile - \
    --error-logfile -