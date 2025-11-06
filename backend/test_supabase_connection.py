#!/usr/bin/env python3
"""
test_supabase_connection.py - Test Supabase connection locally
Run this script to verify your Supabase credentials work
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_supabase_connection():
    """Test Supabase connection with your credentials"""
    
    # Check if credentials exist
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url:
        print("❌ SUPABASE_URL not found in .env file")
        return False
        
    if not supabase_key:
        print("❌ SUPABASE_KEY not found in .env file")
        return False
    
    print(f"🔍 Testing connection to: {supabase_url}")
    
    try:
        from supabase import create_client
        
        # Create client
        supabase = create_client(supabase_url, supabase_key)
        
        # Test connection with a simple query
        response = supabase.table("users").select("*").limit(1).execute()
        
        print("✅ Supabase connection successful!")
        print(f"📊 Response: {response}")
        return True
        
    except ImportError:
        print("❌ Supabase package not installed. Run: pip install supabase")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check if SUPABASE_URL is correct")
        print("2. Check if SUPABASE_KEY is the anon/public key (not service_role)")
        print("3. Verify your Supabase project is active")
        return False

if __name__ == "__main__":
    print("🧪 Testing Supabase Connection...")
    test_supabase_connection()