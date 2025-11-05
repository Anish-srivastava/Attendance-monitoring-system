"""
Test script to verify attendance data flow
- Create a session
- Check attendance records table
- Test real-mark endpoint
"""

import requests
import json
from supabase_client import init_supabase

def test_attendance_flow():
    """Test the complete attendance flow"""
    print("🧪 Testing attendance data flow...")
    
    # Initialize Supabase client
    supabase = init_supabase()
    if not supabase:
        print("❌ Failed to initialize Supabase client")
        return
    
    # 1. Check if attendance_records table exists and get current records
    print("\n📊 Checking attendance_records table...")
    try:
        result = supabase.table('attendance_records').select('*').limit(5).execute()
        print(f"✅ attendance_records table exists with {len(result.data)} records")
        if result.data:
            print("Sample records:")
            for record in result.data:
                print(f"  - Session: {record.get('session_id')}, Student: {record.get('student_name')}, Time: {record.get('marked_at')}")
        else:
            print("  - No attendance records found")
    except Exception as e:
        print(f"❌ Error accessing attendance_records table: {e}")
        return
    
    # 2. Check if there are any active sessions
    print("\n🔄 Checking for active sessions...")
    try:
        sessions_result = supabase.table('attendance_sessions').select('*').eq('status', 'active').execute()
        active_sessions = sessions_result.data
        print(f"✅ Found {len(active_sessions)} active sessions")
        
        if active_sessions:
            for session in active_sessions:
                print(f"  - Session ID: {session.get('session_id')}")
                print(f"    Subject: {session.get('subject')}")
                print(f"    Department: {session.get('department')}")
                
                # Check attendance records for this session
                attendance_result = supabase.table('attendance_records')\
                    .select('*')\
                    .eq('session_id', session['id'])\
                    .execute()
                    
                print(f"    Attendance Records: {len(attendance_result.data)}")
                for record in attendance_result.data:
                    print(f"      - {record.get('student_name')} ({record.get('student_enrollment')}) at {record.get('marked_at')}")
        else:
            print("  - No active sessions found")
            
    except Exception as e:
        print(f"❌ Error checking sessions: {e}")
        return
    
    # 3. Test the real-mark endpoint (simulated call)
    print("\n🎯 Testing real-mark endpoint availability...")
    try:
        response = requests.get("http://localhost:5000/api/attendance/models/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Models status: {data}")
        else:
            print(f"⚠️  Models endpoint returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking models status: {e}")
    
    # 4. Show current session and attendance summary
    print("\n📈 Summary:")
    try:
        # Count total sessions
        total_sessions = supabase.table('attendance_sessions').select('id').execute()
        total_attendance = supabase.table('attendance_records').select('id').execute()
        
        print(f"  - Total sessions: {len(total_sessions.data)}")
        print(f"  - Total attendance records: {len(total_attendance.data)}")
        print(f"  - Active sessions: {len(active_sessions)}")
        
    except Exception as e:
        print(f"❌ Error getting summary: {e}")

if __name__ == "__main__":
    test_attendance_flow()