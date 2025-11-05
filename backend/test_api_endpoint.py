import requests
import json

def test_session_creation_api():
    """Test the actual API endpoint"""
    print("🧪 Testing /api/attendance/create_session endpoint...")
    
    url = "http://localhost:5000/api/attendance/create_session"
    
    test_data = {
        "date": "2025-11-06",
        "subject": "Computer Science",
        "department": "Computer Science",
        "year": "3rd Year",
        "division": "A",
        "duration_minutes": 20
    }
    
    print(f"📋 Sending POST request to {url}")
    print(f"📋 Data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(url, json=test_data, timeout=30)
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"📊 Response Data: {json.dumps(response_data, indent=2)}")
        except:
            print(f"📊 Response Text: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_session_creation_api()