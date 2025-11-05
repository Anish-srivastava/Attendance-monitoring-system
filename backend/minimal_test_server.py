from flask import Flask, request, jsonify
from supabase_client import init_supabase
from datetime import datetime, timedelta
import logging

app = Flask(__name__)
logger = logging.getLogger(__name__)

@app.route("/test_create_session", methods=["POST"])
def test_create_session():
    """Minimal session creation test"""
    try:
        data = request.json
        print(f"Received data: {data}")
        
        # Initialize Supabase
        supabase = init_supabase()
        if not supabase:
            return jsonify({"error": "Supabase connection failed"}), 500
        
        # Calculate times
        duration_minutes = int(data.get("duration_minutes", 20))
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Generate session ID
        session_id = f"session_{int(start_time.timestamp())}"
        
        # Create minimal session data
        session_data = {
            "session_id": session_id,
            "subject": (data.get("subject") or "")[:50],
            "department": (data.get("department") or "")[:50],
            "year": (data.get("year") or "")[:20],
            "division": (data.get("division") or "")[:10],
            "date": data.get("date"),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "status": "active"
        }
        
        print(f"Inserting session data: {session_data}")
        
        # Insert into Supabase
        result = supabase.table('attendance_sessions').insert(session_data).execute()
        
        if result.data:
            return jsonify({
                "success": True,
                "session_id": session_id,
                "data": result.data[0]
            })
        else:
            return jsonify({"success": False, "error": "No data returned"}), 500
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    print("Starting minimal test server...")
    app.run(host="0.0.0.0", port=5001, debug=True)