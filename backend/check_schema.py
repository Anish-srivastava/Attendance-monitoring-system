#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase_client import init_supabase
import json

def check_table_schema():
    """Check the current attendance_sessions table structure"""
    print("🔍 Checking attendance_sessions table schema...")
    
    try:
        # Initialize Supabase client
        supabase = init_supabase()
        print("✅ Supabase client created successfully")
        
        # Try to get existing records to see current schema
        result = supabase.table('attendance_sessions').select('*').limit(1).execute()
        
        if result.data:
            print("📋 Current table schema (based on existing record):")
            sample_record = result.data[0]
            for key, value in sample_record.items():
                print(f"  - {key}: {type(value).__name__} = {value}")
        else:
            print("📋 No existing records found in attendance_sessions table")
            
        # Try a simple insert without the new columns
        print("\n🧪 Testing basic insert without new columns...")
        basic_session_data = {
            "session_id": "test_session_basic",
            "subject": "Test Subject",
            "department": "Test Department",
            "year": "Test Year",
            "division": "Test Division",
            "date": "2025-11-06",
            "status": "active"
        }
        
        print(f"🔄 Inserting: {json.dumps(basic_session_data, indent=2)}")
        
        basic_result = supabase.table('attendance_sessions').insert(basic_session_data).execute()
        
        if basic_result.data:
            print("✅ Basic insert successful!")
            print(f"📊 Result: {json.dumps(basic_result.data, indent=2)}")
            
            # Clean up test record
            supabase.table('attendance_sessions').delete().eq('session_id', 'test_session_basic').execute()
            print("🧹 Test record cleaned up")
            
        else:
            print("❌ Basic insert failed!")
            print(f"Error: {basic_result}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_table_schema()