#!/usr/bin/env python3
"""
start_server.py - Python-based startup script for Render deployment
Handles gunicorn installation and fallback to Flask dev server
"""

import os
import sys
import subprocess
import importlib.util

def check_and_install_gunicorn():
    """Check if gunicorn is available, install if not"""
    try:
        import gunicorn
        print(f"✅ Gunicorn {gunicorn.__version__} is available")
        return True
    except ImportError:
        print("⚠️ Gunicorn not found, attempting to install...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "gunicorn==20.1.0"])
            import gunicorn
            print(f"✅ Gunicorn {gunicorn.__version__} installed successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to install gunicorn: {e}")
            return False

def start_with_gunicorn():
    """Start the app with gunicorn"""
    port = os.environ.get("PORT", "10000")
    cmd = [
        sys.executable, "-m", "gunicorn", "app:app",
        "--bind", f"0.0.0.0:{port}",
        "--workers", "1",
        "--timeout", "120",
        "--preload",
        "--log-level", "info",
        "--access-logfile", "-",
        "--error-logfile", "-"
    ]
    
    print(f"🚀 Starting with gunicorn on port {port}...")
    print(f"Command: {' '.join(cmd)}")
    subprocess.run(cmd)

def start_with_flask():
    """Fallback: Start with Flask development server"""
    port = int(os.environ.get("PORT", "10000"))
    print(f"🔄 Falling back to Flask development server on port {port}...")
    
    # Import and run the Flask app directly
    from app import app
    app.run(host="0.0.0.0", port=port, debug=False)

def main():
    print("🚀 Starting Attendance Management System Backend...")
    
    # Check if app.py exists
    if not os.path.exists("app.py"):
        print("❌ app.py not found in current directory")
        print("Current directory contents:")
        for item in os.listdir("."):
            print(f"  {item}")
        sys.exit(1)
    
    # Try gunicorn first
    if check_and_install_gunicorn():
        try:
            start_with_gunicorn()
        except Exception as e:
            print(f"❌ Gunicorn failed: {e}")
            print("🔄 Trying Flask fallback...")
            start_with_flask()
    else:
        print("🔄 Using Flask development server...")
        start_with_flask()

if __name__ == "__main__":
    main()