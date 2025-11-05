#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase_client import init_supabase
import json

def test_field_lengths():
    """Test different field lengths to find the limit"""
    print("🔍 Testing field length limits...")
    
    try:
        # Initialize Supabase client
        supabase = init_supabase()
        print("✅ Supabase client created successfully")
        
        # Test with shorter values
        test_cases = [
            {
                "name": "Very short values",
                "data": {
                    "session_id": "test1",
                    "subject": "CS",
                    "department": "CS",
                    "year": "3rd",
                    "division": "A",
                    "date": "2025-11-06",
                    "status": "active"
                }
            },
            {
                "name": "Medium length values", 
                "data": {
                    "session_id": "test2",
                    "subject": "Math101",
                    "department": "CompSci",
                    "year": "3rd Year",
                    "division": "A",
                    "date": "2025-11-06",
                    "status": "active"
                }
            }
        ]
        
        for test_case in test_cases:
            print(f"\n🧪 Testing: {test_case['name']}")
            print(f"📋 Data: {json.dumps(test_case['data'], indent=2)}")
            
            try:
                result = supabase.table('attendance_sessions').insert(test_case['data']).execute()
                
                if result.data:
                    print("✅ Success!")
                    # Clean up
                    supabase.table('attendance_sessions').delete().eq('session_id', test_case['data']['session_id']).execute()
                else:
                    print("❌ Failed - no data returned")
                    
            except Exception as e:
                print(f"❌ Failed: {str(e)}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_field_lengths()