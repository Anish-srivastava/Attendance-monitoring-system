#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase_client import init_supabase
from datetime import datetime, timedelta
import json

def test_session_creation():
    """Test session creation with Supabase"""
    print("🧪 Testing session creation...")
    
    try:
        # Initialize Supabase client
        supabase = init_supabase()
        print("✅ Supabase client created successfully")
        
        # Test data
        test_data = {
            "date": "2025-11-06",
            "subject": "Computer Science",
            "department": "Computer Science", 
            "year": "3rd Year",
            "division": "A",
            "duration_minutes": 20
        }
        
        print(f"📋 Test data: {json.dumps(test_data, indent=2)}")
        
        # Calculate times
        duration_minutes = int(test_data.get("duration_minutes", 20))
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Generate session ID
        session_id = f"session_{int(start_time.timestamp())}"
        
        # Create session record for Supabase (matching existing schema)
        session_data = {
            "session_id": session_id,
            "subject": test_data.get("subject"),
            "department": test_data.get("department"),
            "year": test_data.get("year"),
            "division": test_data.get("division"),
            "date": test_data.get("date"),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "status": "active"
        }
        
        print(f"🔄 Attempting to insert session: {json.dumps(session_data, indent=2)}")
        
        # Try to insert into Supabase
        result = supabase.table('attendance_sessions').insert(session_data).execute()
        
        if result.data:
            print("✅ Session created successfully!")
            print(f"📊 Result: {json.dumps(result.data, indent=2)}")
            
            # Test session status endpoint data structure
            print("\n🔍 Testing session status query...")
            status_result = supabase.table('attendance_sessions').select('*').eq('session_id', session_id).execute()
            
            if status_result.data:
                session = status_result.data[0]
                print(f"📋 Session data retrieved: {json.dumps(session, indent=2)}")
                
                # Calculate remaining time using end_time
                if session.get('end_time'):
                    end_time_str = session['end_time']
                    if '+' in end_time_str:
                        end_time_str = end_time_str.split('+')[0]
                    scheduled_end_time = datetime.fromisoformat(end_time_str)
                    current_time = datetime.now()
                    remaining_time = scheduled_end_time - current_time
                    remaining_minutes = max(0, int(remaining_time.total_seconds() / 60))
                    
                    print(f"⏰ Remaining minutes: {remaining_minutes}")
                    print("✅ Session status check successful!")
                else:
                    print("⚠️ No end_time found in session")
                
            else:
                print("❌ Could not retrieve session for status check")
                
        else:
            print("❌ Session creation failed!")
            print(f"Error details: {result}")
            
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_session_creation()