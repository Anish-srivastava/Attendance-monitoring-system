"""
Test the new session attendance endpoint
"""

import requests
import json

def test_session_attendance_endpoint():
    """Test the new session attendance endpoint"""
    print("🧪 Testing session attendance endpoint...")
    
    # First, let's check what active sessions we have
    try:
        print("\n📋 Getting active sessions...")
        sessions_res = requests.get("http://localhost:5000/api/attendance/active_sessions", timeout=10)
        
        if sessions_res.status_code == 200:
            sessions_data = sessions_res.json()
            if sessions_data.get('success') and sessions_data.get('sessions'):
                sessions = sessions_data['sessions']
                print(f"✅ Found {len(sessions)} active sessions")
                
                for session in sessions:
                    session_id = session.get('session_id')
                    subject = session.get('subject', 'Unknown')
                    print(f"\n🎯 Testing session: {session_id} ({subject})")
                    
                    # Test the new attendance endpoint
                    attendance_res = requests.get(
                        f"http://localhost:5000/api/attendance/session/{session_id}/attendance",
                        timeout=10
                    )
                    
                    print(f"   Status: {attendance_res.status_code}")
                    
                    if attendance_res.status_code == 200:
                        attendance_data = attendance_res.json()
                        print(f"   Response: {json.dumps(attendance_data, indent=2)}")
                        
                        if attendance_data.get('success'):
                            records = attendance_data.get('attendance_records', [])
                            print(f"   ✅ Success! Found {len(records)} attendance records")
                            
                            for record in records:
                                student_name = record.get('student_name')
                                student_id = record.get('student_id') 
                                marked_at = record.get('marked_at')
                                confidence = record.get('confidence')
                                print(f"      - {student_name} ({student_id}) at {marked_at} [{confidence}% confidence]")
                        else:
                            print(f"   ❌ API returned success=false: {attendance_data.get('error')}")
                    else:
                        print(f"   ❌ HTTP Error: {attendance_res.status_code}")
                        try:
                            error_data = attendance_res.json()
                            print(f"   Error: {error_data}")
                        except:
                            print(f"   Raw response: {attendance_res.text}")
            else:
                print("   ❌ No active sessions found")
        else:
            print(f"❌ Failed to get active sessions: {sessions_res.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_session_attendance_endpoint()