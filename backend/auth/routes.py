from flask import Blueprint, request, jsonify, current_app
from flask_bcrypt import Bcrypt
import time
from datetime import datetime

auth_bp = Blueprint("auth", __name__)
bcrypt = Bcrypt()

@auth_bp.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    user_type = data.get('userType', 'student')  # Default to student

    if not all([username, email, password]):
        return jsonify({"success": False, "error": "All fields required"}), 400

    supabase = current_app.config.get("SUPABASE")
    
    if not supabase:
        return jsonify({"success": False, "error": "Database connection error"}), 500
    
    # Check if email already exists
    try:
        existing_user = supabase.table('users').select('*').eq('email', email).execute()
        
        if existing_user.data and len(existing_user.data) > 0:
            return jsonify({
                "success": False, 
                "error": f"Email already registered"
            }), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"Database error: {str(e)}"}), 500

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

    # Prepare user document for Supabase
    user_data = {
        "email": email,
        "password_hash": hashed_pw,
        "role": user_type,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    # Insert user into Supabase
    try:
        result = supabase.table('users').insert(user_data).execute()
        
        return jsonify({
            "success": True, 
            "message": f"{user_type.capitalize()} registered successfully",
            "user_id": result.data[0]['id'] if result.data else None
        })
    except Exception as e:
        return jsonify({"success": False, "error": f"Registration failed: {str(e)}"}), 500

@auth_bp.route('/api/signin', methods=['POST'])
def api_signin():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user_type = data.get('userType', 'student')  # Default to student

    if not all([email, password]):
        return jsonify({"success": False, "error": "Email and password required"}), 400

    supabase = current_app.config.get("SUPABASE")
    
    if not supabase:
        return jsonify({"success": False, "error": "Database connection error"}), 500
    
    # Find user in Supabase
    try:
        user_response = supabase.table('users').select('*').eq('email', email).eq('role', user_type).execute()
        
        if not user_response.data or len(user_response.data) == 0:
            return jsonify({
                "success": False, 
                "error": f"No {user_type} account found with this email"
            }), 401
        
        user = user_response.data[0]
    except Exception as e:
        return jsonify({"success": False, "error": f"Login error: {str(e)}"}), 500
    
    # Check password
    if not bcrypt.check_password_hash(user['password_hash'], password):
        return jsonify({
            "success": False, 
            "error": "Invalid password"
        }), 401

    # Prepare response based on user type
    user_info = {
        "id": str(user['id']),
        "email": user['email'],
        "userType": user_type,
        "role": user.get('role', user_type)
    }
    
    # Try to get additional student info if exists
    if user_type == 'student':
        try:
            student_response = supabase.table('students').select('*').eq('email', email).execute()
            if student_response.data and len(student_response.data) > 0:
                student = student_response.data[0]
                user_info.update({
                    "studentId": student.get('student_id'),
                    "studentName": student.get('student_name'),
                    "department": student.get('department'),
                    "hasStudentRecord": True
                })
        except Exception:
            pass  # Student record not required for login

    return jsonify({
        "success": True, 
        "message": f"Signed in successfully as {user_type}",
        "user": user_info,
        "userType": user_type
    })

@auth_bp.route('/api/logout', methods=['POST'])
def api_logout():
    # You can add logout logic here if needed (e.g., invalidate tokens)
    return jsonify({"success": True, "message": "Logged out successfully"})

@auth_bp.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    """Get current user's profile information"""
    user_email = request.headers.get('X-User-Email')
    user_type = request.headers.get('X-User-Type', 'student')
    
    if not user_email:
        return jsonify({"success": False, "error": "Authentication required"}), 401
    
    supabase = current_app.config.get("SUPABASE")
    
    if not supabase:
        return jsonify({"success": False, "error": "Database connection error"}), 500
    
    try:
        # Get user from Supabase
        user_response = supabase.table('users').select('*').eq('email', user_email).eq('role', user_type).execute()
        
        if not user_response.data or len(user_response.data) == 0:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        user = user_response.data[0]
        # Remove password_hash from response
        user.pop('password_hash', None)
        
        return jsonify({
            "success": True,
            "user": user
        })
    except Exception as e:
        return jsonify({"success": False, "error": f"Error fetching profile: {str(e)}"}), 500

# Route to switch user type (if user has both teacher and student accounts)
@auth_bp.route('/api/switch-role', methods=['POST'])
def switch_user_role():
    """Allow users to switch between teacher and student roles if they have both"""
    data = request.get_json()
    user_email = data.get('email')
    target_type = data.get('targetType')  # 'teacher' or 'student'
    
    if not all([user_email, target_type]):
        return jsonify({"success": False, "error": "Email and target type required"}), 400
    
    supabase = current_app.config.get("SUPABASE")
    
    if not supabase:
        return jsonify({"success": False, "error": "Database connection error"}), 500
    
    try:
        # Check if user exists with target role
        target_response = supabase.table('users').select('*').eq('email', user_email).eq('role', target_type).execute()
        
        if not target_response.data or len(target_response.data) == 0:
            return jsonify({
                "success": False, 
                "error": f"No {target_type} account found for this email"
            }), 404
        
        target_user = target_response.data[0]
        
        # Return user info for the target role
        user_info = {
            "id": str(target_user['id']),
            "email": target_user['email'],
            "userType": target_type,
            "role": target_user.get('role', target_type)
        }
        
        return jsonify({
            "success": True,
            "message": f"Switched to {target_type} role",
            "user": user_info,
            "userType": target_type
        })
    except Exception as e:
        return jsonify({"success": False, "error": f"Error switching role: {str(e)}"}), 500
