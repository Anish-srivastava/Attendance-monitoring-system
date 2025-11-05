import requests
import json

def test_minimal_server():
    """Test the minimal server"""
    print("🧪 Testing minimal server...")
    
    url = "http://localhost:5001/test_create_session"
    
    test_data = {
        "date": "2025-11-06",
        "subject": "Computer Science",
        "department": "Computer Science",
        "year": "3rd Year",
        "division": "A",
        "duration_minutes": 20
    }
    
    try:
        response = requests.post(url, json=test_data, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_minimal_server()