#!/usr/bin/env python3
"""
app.py - Root level startup script for Render
This file redirects to the actual app in the backend/ directory
"""

import os
import sys

# Add backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Change working directory to backend
os.chdir(backend_path)

# Import and run the actual app from backend directory
try:
    # Import the Flask app from the backend.app module
    import importlib.util
    spec = importlib.util.spec_from_file_location("backend_app", os.path.join(backend_path, "app.py"))
    backend_app = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(backend_app)
    
    app = backend_app.app
    
    if __name__ == "__main__":
        # Get port from environment (Render sets this)
        port = int(os.environ.get("PORT", 10000))
        print(f"🚀 Starting Attendance Management Backend on port {port}")
        
        # Run the app
        app.run(host="0.0.0.0", port=port, debug=False)
        
except ImportError as e:
    print(f"❌ Error importing app from backend directory: {e}")
    print("🔍 Current working directory:", os.getcwd())
    print("📁 Directory contents:", os.listdir('.'))
    sys.exit(1)
except (RuntimeError, OSError, ValueError) as e:
    print(f"❌ Error starting application: {e}")
    sys.exit(1)