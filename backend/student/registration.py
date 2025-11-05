from flask import Blueprint, request, jsonify, current_app
import time
import base64
import numpy as np
from PIL import Image
import io
from deepface import DeepFace
from mtcnn import MTCNN
import logging
from datetime import datetime

student_registration_bp = Blueprint("student_registration", __name__)
detector = MTCNN()
logger = logging.getLogger(__name__)

def read_image_from_bytes(b):
    img = Image.open(io.BytesIO(b)).convert('RGB')
    return np.array(img)

def detect_faces_rgb(rgb_image):
    detections = detector.detect_faces(rgb_image)
    faces = []
    for d in detections:
        if d['confidence'] > 0.9:
            x, y, w, h = d['box']
            x, y = max(0, x), max(0, y)
            if w > 50 and h > 50:
                face_rgb = rgb_image[y:y+h, x:x+w]
                faces.append({'box': (x, y, w, h), 'face': face_rgb, 'confidence': d['confidence']})
    return faces

def extract_embedding(face_rgb):
    try:
        face_pil = Image.fromarray(face_rgb.astype('uint8')).resize((160, 160))
        face_array = np.array(face_pil)
        rep = DeepFace.represent(face_array, model_name='Facenet512', detector_backend='skip')
        return np.array(rep[0]['embedding'], dtype=float)
    except Exception as e:
        print(f"Embedding error: {e}")
        return None

@student_registration_bp.route('/api/register-student', methods=['POST'])
def register_student():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "Invalid JSON data"}), 400

    # Get Supabase client from app config
    supabase = current_app.config.get("SUPABASE")
    if not supabase:
        logger.error("Supabase client is not available")
        return jsonify({"success": False, "error": "Database connection error"}), 500

    # Check required fields
    required_fields = ['studentName', 'studentId', 'department', 'year', 'division', 'semester', 'email', 'phoneNumber', 'images']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"success": False, "error": f"{field} is required"}), 400

    try:
        # Double-check supabase client before using it
        if supabase is None:
            logger.error("Supabase client became None after initial check")
            return jsonify({"success": False, "error": "Database connection error"}), 500
            
        # Check uniqueness of studentId and email
        student_id_check = supabase.table('students').select('student_id').eq('student_id', data['studentId']).execute()
        if student_id_check.data and len(student_id_check.data) > 0:
            return jsonify({"success": False, "error": "Student ID already exists"}), 400

        email_check = supabase.table('students').select('email').eq('email', data['email']).execute()
        if email_check.data and len(email_check.data) > 0:
            return jsonify({"success": False, "error": "Email already registered"}), 400

        # Validate images
        images = data.get('images')
        if not isinstance(images, list) or len(images) != 5:
            return jsonify({"success": False, "error": "Exactly 5 images are required"}), 400

        embeddings = []
        for idx, img_b64 in enumerate(images):
            try:
                if img_b64.startswith("data:"):
                    img_b64 = img_b64.split(",", 1)[1]
                rgb = read_image_from_bytes(base64.b64decode(img_b64))
            except Exception:
                return jsonify({"success": False, "error": f"Invalid image data at index {idx}"}), 400

            faces = detect_faces_rgb(rgb)
            if len(faces) != 1:
                return jsonify({"success": False, "error": f"Ensure exactly one face in each image (failed at image {idx+1})"}), 400

            emb = extract_embedding(faces[0]['face'])
            if emb is None:
                return jsonify({"success": False, "error": f"Failed to extract face features for image {idx+1}"}), 500
            embeddings.append(emb.tolist())

        # Prepare student data for Supabase
        student_data = {
            "student_id": data['studentId'],
            "student_name": data['studentName'],
            "department": data['department'],
            "year": data['year'],
            "division": data['division'],
            "semester": data['semester'],
            "email": data['email'],
            "phone_number": data['phoneNumber'],
            "embeddings": embeddings,  # Supabase will store this as JSONB
            "registration_date": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

        # Insert student into Supabase
        result = supabase.table('students').insert(student_data).execute()
        
        if result.data and len(result.data) > 0:
            return jsonify({
                "success": True, 
                "studentId": data['studentId'], 
                "message": "Student registered successfully",
                "record_id": result.data[0]['id']
            })
        else:
            return jsonify({"success": False, "error": "Failed to insert student record"}), 500

    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({"success": False, "error": f"Registration failed: {str(e)}"}), 500

@student_registration_bp.route('/api/students/count', methods=['GET'])
def get_student_count():
    supabase = current_app.config.get("SUPABASE")
    if not supabase:
        return jsonify({"success": False, "error": "Database connection error"}), 500
    
    try:
        result = supabase.table('students').select('id', count='exact').execute()
        count = result.count if result.count is not None else 0
        return jsonify({"success": True, "count": count})
    except Exception as e:
        logger.error(f"Error getting student count: {e}")
        return jsonify({"success": False, "error": "Failed to get student count"}), 500

@student_registration_bp.route('/api/students/departments', methods=['GET'])
def get_departments():
    supabase = current_app.config.get("SUPABASE")
    if not supabase:
        return jsonify({"success": False, "error": "Database connection error"}), 500
    
    try:
        result = supabase.table('students').select('department').execute()
        departments = list(set([row['department'] for row in result.data if row.get('department')]))
        return jsonify({"success": True, "departments": departments, "count": len(departments)})
    except Exception as e:
        logger.error(f"Error getting departments: {e}")
        return jsonify({"success": False, "error": "Failed to get departments"}), 500
