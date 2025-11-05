# teacher/attendance_records.py - OPTIMIZED VERSION

import io
import base64
import numpy as np
from flask import Blueprint, request, jsonify, current_app
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from PIL import Image
from scipy.spatial.distance import cosine
from deepface import DeepFace
import logging
import time
import threading
from server_stability import stable_endpoint, safe_memory_operation, ManagedResource

logger = logging.getLogger(__name__)

# Auto-close session function
def auto_close_session(session_id, supabase):
    """Automatically close session after timeout"""
    try:
        logger.info(f"Auto-closing session {session_id} due to timeout")
        
        # Update session status to 'ended'
        supabase.table('attendance_sessions').update({
            'status': 'ended',
            'ended_at': datetime.now().isoformat()
        }).eq('session_id', session_id).execute()
        
        logger.info(f"Session {session_id} successfully auto-closed")
        
    except Exception as e:
        logger.error(f"Error auto-closing session {session_id}: {str(e)}")

# Attendance Blueprint with URL prefix
attendance_session_bp = Blueprint(
    "attendance_session",
    __name__,
    url_prefix="/api/attendance"
)

# ----------------- OPTIMIZED Helper Functions ----------------- #

def read_image_from_base64_optimized(image_b64: str, target_size=(640, 480)):
    """Convert base64 image to RGB numpy array with optimization"""
    if image_b64.startswith("data:"):
        image_b64 = image_b64.split(",", 1)[1]
    
    image_bytes = base64.b64decode(image_b64)
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    
    # Resize large images to reduce processing time
    if img.width > target_size[0] or img.height > target_size[1]:
        img.thumbnail(target_size, Image.Resampling.LANCZOS)
    
    return np.array(img)

def detect_faces_optimized(rgb_image, detector):
    """Detect faces using preloaded MTCNN detector"""
    # Skip detection if image is too small
    if rgb_image.shape[0] < 50 or rgb_image.shape[1] < 50:
        return []
    
    detections = detector.detect_faces(rgb_image)
    faces = []
    
    for d in detections:
        if d["confidence"] > 0.85:  # Slightly lower threshold for better detection
            x, y, w, h = d["box"]
            x, y = max(0, x), max(0, y)
            if w > 40 and h > 40:  # Lower minimum size for better detection
                face_rgb = rgb_image[y:y+h, x:x+w]
                faces.append({
                    "box": (x, y, w, h), 
                    "face": face_rgb, 
                    "confidence": d["confidence"]
                })
    
    return faces

def extract_embedding_optimized(face_rgb):
    """Extract embedding using preloaded DeepFace model"""
    try:
        if face_rgb.shape[0] < 40 or face_rgb.shape[1] < 40:
            return None
            
        # Resize face to standard size
        face_pil = Image.fromarray(face_rgb.astype("uint8")).resize((160, 160))
        face_array = np.array(face_pil)
        
        # Use DeepFace with optimized parameters
        rep = DeepFace.represent(
            face_array, 
            model_name="Facenet512", 
            detector_backend="skip",
            enforce_detection=False  # Skip additional detection for speed
        )
        return np.array(rep[0]["embedding"], dtype=np.float32)  # Use float32 for speed
        
    except Exception as e:
        logger.error(f"Embedding extraction error: {e}")
        return None

def get_attendance_collection():
    """Get the attendance collection from app config"""
    return current_app.config.get("ATTENDANCE_COLLECTION")

# Enhanced embedding cache for attendance sessions
class AttendanceEmbeddingCache:
    def __init__(self):
        self.cached_embeddings = {}
        self.last_update = {}
        self.cache_duration = 600  # 10 minutes for attendance sessions
    
    def get_session_embeddings(self, students_col, session_filter):
        """Get cached embeddings for specific session filters"""
        cache_key = str(sorted(session_filter.items()))
        current_time = time.time()
        
        if (cache_key not in self.cached_embeddings or 
            current_time - self.last_update.get(cache_key, 0) > self.cache_duration):
            
            logger.info(f"Refreshing attendance embedding cache for {session_filter}")
            
            # Fetch students matching the session filter
            students = list(students_col.find(session_filter))
            
            # Process embeddings - handle both old and new embedding formats
            session_embeddings = []
            for student in students:
                # Handle multiple embedding formats
                embeddings = student.get('embeddings') or student.get('embedding')
                if embeddings:
                    if isinstance(embeddings, list) and len(embeddings) > 0:
                        # Multiple embeddings - average them
                        if isinstance(embeddings[0], list):
                            avg_embedding = np.mean(embeddings, axis=0).astype(np.float32)
                        else:
                            avg_embedding = np.array(embeddings, dtype=np.float32)
                    else:
                        # Single embedding
                        avg_embedding = np.array(embeddings, dtype=np.float32)
                    
                    session_embeddings.append({
                        'embedding': avg_embedding,
                        'studentId': student.get('studentId'),
                        'studentName': student.get('studentName'),
                        'department': student.get('department'),
                        'year': student.get('year'),
                        'division': student.get('division')
                    })
            
            self.cached_embeddings[cache_key] = session_embeddings
            self.last_update[cache_key] = current_time
            logger.info(f"Cached {len(session_embeddings)} student embeddings for session")
        
        return self.cached_embeddings[cache_key]

# Global cache instance for attendance
attendance_cache = AttendanceEmbeddingCache()

def find_best_match_optimized_attendance(query_embedding, students_col, session_doc, threshold=0.6):
    """Optimized student matching for attendance with session-specific filtering"""
    # Build filter for students in this session's class
    student_filter = {"embeddings": {"$exists": True, "$ne": None}}
    
    # Add session-specific filters
    if session_doc.get("department"):
        student_filter["department"] = session_doc.get("department")
    if session_doc.get("year"):
        student_filter["year"] = session_doc.get("year")
    if session_doc.get("division"):
        student_filter["division"] = session_doc.get("division")
    
    # Get cached embeddings for this session
    cached_embeddings = attendance_cache.get_session_embeddings(students_col, student_filter)
    
    if not cached_embeddings:
        return None, float('inf')
    
    best_match = None
    min_distance = float('inf')
    
    # Vectorized comparison for speed
    for student_data in cached_embeddings:
        stored_embedding = student_data['embedding']
        distance = cosine(query_embedding, stored_embedding)
        
        if distance < min_distance:
            min_distance = distance
            best_match = student_data
    
    return best_match if min_distance < threshold else None, min_distance

# ----------------- OPTIMIZED Routes ----------------- #

@attendance_session_bp.route("/create_session", methods=["POST"])
@stable_endpoint
def create_session():
    """Create a new attendance session with auto-timeout"""
    data = request.json
    
    # Use Supabase instead of MongoDB
    supabase = current_app.config.get("SUPABASE")
    if not supabase:
        return jsonify({"success": False, "error": "Database connection error"}), 500

    # Get session duration (default 20 minutes)
    duration_minutes = int(data.get("duration_minutes", 20))
    if duration_minutes < 5 or duration_minutes > 120:
        return jsonify({"success": False, "error": "Duration must be between 5-120 minutes"}), 400

    # Calculate end time
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=duration_minutes)

    # Build base session document
    session_doc = {
        "date": data.get("date"),
        "subject": data.get("subject"),
        "department": data.get("department"),
        "year": data.get("year"),
        "division": data.get("division"),
        "duration_minutes": duration_minutes,  # Keep in session doc for frontend
        "created_at": start_time.isoformat(),
        "scheduled_end_time": end_time.isoformat(),  # Keep in session doc for frontend
        "finalized": False,
        "ended_at": None,
        "students": []
    }

    # Prepopulate session with all students in that class
    student_filter = {}
    if data.get("department"): student_filter["department"] = data.get("department")
    if data.get("year"): student_filter["year"] = data.get("year")
    if data.get("division"): student_filter["division"] = data.get("division")

    try:
        # Get students from Supabase
        if student_filter:
            query = supabase.table('students').select('student_id, student_name, department, year, division')
            
            # Apply filters
            if student_filter.get("department"):
                query = query.eq('department', student_filter["department"])
            if student_filter.get("year"):
                query = query.eq('year', student_filter["year"])
            if student_filter.get("division"):
                query = query.eq('division', student_filter["division"])
                
            result = query.execute()
            students = result.data if result.data else []
        else:
            students = []

        for s in students:
            sid = s.get("student_id")
            name = s.get("student_name")
            session_doc["students"].append({
                "student_id": sid,
                "student_name": name,
                "present": False,
                "marked_at": None
            })
        
        logger.info(f"Created session with {len(students)} students preloaded")
        
        # Save session to Supabase attendance_sessions table
        session_id = f"session_{int(datetime.now().timestamp())}"
        
        # Create session record in Supabase (matching existing schema)
        session_data = {
            "session_id": session_id,
            "subject": data.get("subject")[:50] if data.get("subject") else "",  # Limit length
            "department": data.get("department")[:50] if data.get("department") else "",
            "year": data.get("year")[:20] if data.get("year") else "",
            "division": data.get("division")[:10] if data.get("division") else "",
            "date": data.get("date"),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),  # Use existing end_time column
            "status": "active"
        }
        
        try:
            # Insert session into Supabase
            logger.info(f"Attempting to insert session data: {session_data}")
            result = supabase.table('attendance_sessions').insert(session_data).execute()
            logger.info(f"Supabase insert result: {result}")
            
            if not result.data:
                raise Exception("Failed to create session in database")
                
            session_doc["session_id"] = session_id
            
            # Start automatic session timeout timer
            timer = threading.Timer(duration_minutes * 60, auto_close_session, args=[session_id, supabase])
            timer.daemon = True
            timer.start()
            
            logger.info(f"Session {session_id} scheduled to auto-close in {duration_minutes} minutes")
            
            return jsonify({
                "success": True,
                "session": session_doc,
                "message": f"Session created with {len(students)} students, auto-close in {duration_minutes} minutes"
            })
            
        except Exception as db_error:
            logger.error(f"Error saving session to database: {db_error}")
            logger.error(f"Session data that failed: {session_data}")
            return jsonify({"success": False, "error": f"Failed to save session: {str(db_error)}"}), 500
        
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        logger.error(f"Request data: {data}")
        return jsonify({"success": False, "error": f"Failed to create session: {str(e)}"}), 500

@attendance_session_bp.route("/active_sessions", methods=["GET"])
def get_active_sessions():
    """Get all active attendance sessions for students to join"""
    supabase = current_app.config.get("SUPABASE")
    if not supabase:
        return jsonify({"success": False, "error": "Database connection error"}), 500
    
    try:
        # Get active sessions from Supabase
        result = supabase.table('attendance_sessions').select('*').eq('status', 'active').execute()
        sessions = result.data if result.data else []
        
        # Filter sessions by student's department/year/division if provided
        department = request.args.get('department')
        year = request.args.get('year')
        division = request.args.get('division')
        
        filtered_sessions = []
        for session in sessions:
            # Apply filters if provided
            if department and session.get('department') != department:
                continue
            if year and session.get('year') != year:
                continue
            if division and session.get('division') != division:
                continue
            filtered_sessions.append(session)
        
        return jsonify({
            "success": True,
            "sessions": filtered_sessions,
            "count": len(filtered_sessions)
        })
        
    except Exception as e:
        logger.error(f"Error fetching active sessions: {e}")
        return jsonify({"success": False, "error": f"Failed to fetch sessions: {str(e)}"}), 500

@attendance_session_bp.route("/session_status/<session_id>", methods=["GET"])
@stable_endpoint
def get_session_status(session_id):
    """Get session status and remaining time"""
    supabase = current_app.config.get("SUPABASE")
    if not supabase:
        return jsonify({"success": False, "error": "Database connection error"}), 500

    try:
        # Get session from Supabase
        result = supabase.table('attendance_sessions').select('*').eq('session_id', session_id).execute()
        
        if not result.data:
            return jsonify({"success": False, "error": "Session not found"}), 404
            
        session = result.data[0]
        
        # Calculate remaining time using existing end_time column
        if session.get('end_time'):
            # Parse the end_time (handle timezone if present)
            end_time_str = session['end_time']
            if '+' in end_time_str:
                end_time_str = end_time_str.split('+')[0]  # Remove timezone
            scheduled_end_time = datetime.fromisoformat(end_time_str)
            current_time = datetime.now()
            
            if current_time >= scheduled_end_time and session['status'] == 'active':
                # Session should be expired, update status
                supabase.table('attendance_sessions').update({
                    'status': 'ended'
                }).eq('session_id', session_id).execute()
                
                remaining_minutes = 0
                session['status'] = 'ended'
            else:
                remaining_time = scheduled_end_time - current_time
                remaining_minutes = max(0, int(remaining_time.total_seconds() / 60))
        else:
            # No end time set, default to 20 minutes from start
            start_time_str = session.get('start_time', session.get('created_at'))
            if start_time_str:
                if '+' in start_time_str:
                    start_time_str = start_time_str.split('+')[0]
                start_time = datetime.fromisoformat(start_time_str)
                default_end_time = start_time + timedelta(minutes=20)
                current_time = datetime.now()
                
                if current_time >= default_end_time and session['status'] == 'active':
                    supabase.table('attendance_sessions').update({
                        'status': 'ended'
                    }).eq('session_id', session_id).execute()
                    remaining_minutes = 0
                    session['status'] = 'ended'
                else:
                    remaining_time = default_end_time - current_time
                    remaining_minutes = max(0, int(remaining_time.total_seconds() / 60))
            else:
                remaining_minutes = 0
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "status": session['status'],
            "remaining_minutes": remaining_minutes,
            "total_duration": 20,  # Default duration since we don't store it
            "scheduled_end_time": session.get('end_time', 'Not set')
        })
        
    except Exception as e:
        logger.error(f"Error getting session status: {e}")
        return jsonify({"success": False, "error": f"Failed to get session status: {str(e)}"}), 500

@attendance_session_bp.route("/end_session", methods=["POST"])
def end_session():
    """End an attendance session"""
    data = request.get_json()
    session_id = data.get("session_id")
    if not session_id:
        return jsonify({"success": False, "error": "Missing session_id"}), 400

    supabase = current_app.config.get("SUPABASE")
    if not supabase:
        return jsonify({"success": False, "error": "Database connection error"}), 500

    try:
        # Update session status to 'ended'
        result = supabase.table('attendance_sessions').update({
            'status': 'ended',
            'end_time': datetime.now().isoformat()
        }).eq('session_id', session_id).execute()
        
        if not result.data:
            return jsonify({"success": False, "error": "Session not found"}), 404
            
        return jsonify({
            "success": True,
            "message": "Session ended successfully"
        })
        
    except Exception as e:
        logger.error(f"Error ending session: {e}")
        return jsonify({"success": False, "error": f"Failed to end session: {str(e)}"}), 500

@attendance_session_bp.route("/real-mark", methods=["POST"])
@stable_endpoint
@safe_memory_operation
def mark_attendance_with_duplicate_prevention():
    """Enhanced attendance marking with strict duplicate prevention using Supabase"""
    
    with ManagedResource("attendance_marking"):
        start_time = time.time()
        
        # Check if models are ready
        model_manager = current_app.config.get("MODEL_MANAGER")
        if not model_manager or not model_manager.is_ready():
            return jsonify({"error": "Face recognition models not initialized"}), 503
        
        detector = model_manager.get_detector()
        supabase = current_app.config.get("SUPABASE")
        if not supabase:
            return jsonify({"error": "Database connection error"}), 500
        
        data = request.get_json()
        session_id = data.get("session_id")
        image_b64 = data.get("image")

        if not session_id or not image_b64:
            return jsonify({"error": "Missing session_id or image"}), 400

        try:
            # Use same image processing as demo
            rgb = read_image_from_base64_optimized(image_b64)
            faces = detect_faces_optimized(rgb, detector)

            if len(faces) == 0:
                return jsonify({
                    "success": True, 
                    "message": "No faces detected", 
                    "faces": [],
                    "processing_time": round(time.time() - start_time, 3)
                })

            # Validate session exists and is active
            session_result = supabase.table('attendance_sessions').select('*').eq('session_id', session_id).execute()
            if not session_result.data:
                return jsonify({"error": "Session not found"}), 404
            
            session_doc = session_result.data[0]
            if session_doc.get("status") != "active":
                return jsonify({"error": "Session is not active"}), 400

            # Get already marked students for this session with comprehensive check
            marked_result = supabase.table('attendance_records')\
                .select('student_enrollment, student_name, marked_at')\
                .eq('session_id', session_doc['id'])\
                .execute()
            
            already_present_students = {}
            for record in marked_result.data:
                student_id = record['student_enrollment']
                already_present_students[student_id] = {
                    'name': record['student_name'],
                    'marked_at': record.get('marked_at')
                }
            
            logger.info(f"Session {session_id} already has {len(already_present_students)} students marked present")

            # Get all students with embeddings for recognition
            students_result = supabase.table('students').select('*').not_.is_('embeddings', 'null').execute()
            students = students_result.data
            
            threshold = float(current_app.config.get("THRESHOLD", 0.6))
            results = []

            for f in faces:
                emb = extract_embedding_optimized(f["face"])
                if emb is None:
                    results.append({
                        "match": None, 
                        "distance": None, 
                        "box": f["box"],
                        "error": "Failed to extract embedding",
                        "status": "error"
                    })
                    continue

                # Find best matching student
                best, min_d = None, float("inf")
                for student in students:
                    stored_embeddings = student.get("embeddings", [])
                    if not stored_embeddings:
                        continue
                    
                    # Average multiple embeddings
                    if isinstance(stored_embeddings, list) and len(stored_embeddings) > 0:
                        avg_embedding = np.mean(stored_embeddings, axis=0)
                    else:
                        avg_embedding = np.array(stored_embeddings)
                    
                    d = cosine(emb, avg_embedding)
                    if d < min_d:
                        min_d = d
                        best = student

                if min_d < threshold and best:
                    student_id = best.get("student_id")
                    student_name = best.get("student_name")

                    # ENHANCED DUPLICATE CHECK
                    if student_id in already_present_students:
                        existing_record = already_present_students[student_id]
                        results.append({
                            "match": {"user_id": student_id, "name": student_name},
                            "distance": round(float(min_d), 4),
                            "confidence": round((1 - min_d) * 100, 1),
                            "box": f["box"],
                            "already_marked": True,
                            "status": "duplicate",
                            "message": f"{student_name} is already marked present in this session",
                            "marked_at": existing_record.get('marked_at'),
                            "duplicate_detection": True
                        })
                        logger.info(f"Duplicate detection: {student_name} ({student_id}) already present")
                        continue

                    # DOUBLE-CHECK: Query database again to prevent race conditions
                    final_check = supabase.table('attendance_records')\
                        .select('id')\
                        .eq('session_id', session_doc['id'])\
                        .eq('student_enrollment', student_id)\
                        .execute()
                    
                    if final_check.data:
                        results.append({
                            "match": {"user_id": student_id, "name": student_name},
                            "distance": round(float(min_d), 4),
                            "confidence": round((1 - min_d) * 100, 1),
                            "box": f["box"],
                            "already_marked": True,
                            "status": "duplicate",
                            "message": f"{student_name} is already marked present (race condition prevented)",
                            "race_condition_prevented": True
                        })
                        logger.warning(f"Race condition prevented: {student_name} ({student_id}) was marked between checks")
                        continue

                    # MARK ATTENDANCE (Student not yet marked)
                    attendance_record = {
                        'session_id': session_doc['id'],  # Use the UUID from sessions table
                        'student_id': best.get('id'),    # Student UUID
                        'student_enrollment': student_id,
                        'student_name': student_name,
                        'status': 'present',
                        'confidence': round((1 - min_d) * 100, 1),
                        'marked_at': datetime.now().isoformat()
                    }
                    
                    try:
                        insert_result = supabase.table('attendance_records').insert(attendance_record).execute()
                        
                        if insert_result.data:
                            # Successfully marked present
                            already_present_students[student_id] = {
                                'name': student_name,
                                'marked_at': attendance_record['marked_at']
                            }
                            results.append({
                                "match": {"user_id": student_id, "name": student_name},
                                "distance": round(float(min_d), 4),
                                "confidence": round((1 - min_d) * 100, 1),
                                "box": f["box"],
                                "already_marked": False,
                                "status": "marked_present",
                                "message": f"✅ {student_name} marked present successfully",
                                "marked_at": attendance_record['marked_at'],
                                "first_time_marking": True
                            })
                            logger.info(f"✅ Marked {student_name} ({student_id}) as present")
                        else:
                            results.append({
                                "match": {"user_id": student_id, "name": student_name},
                                "distance": round(float(min_d), 4),
                                "confidence": round((1 - min_d) * 100, 1),
                                "box": f["box"],
                                "already_marked": False,
                                "status": "error",
                                "message": f"❌ Database error: Failed to mark {student_name} as present"
                            })
                            logger.error(f"Database insertion failed for {student_name} ({student_id})")
                            
                    except Exception as db_error:
                        # Handle database constraint violations (unique constraint errors)
                        if "duplicate key" in str(db_error).lower() or "unique constraint" in str(db_error).lower():
                            results.append({
                                "match": {"user_id": student_id, "name": student_name},
                                "distance": round(float(min_d), 4),
                                "confidence": round((1 - min_d) * 100, 1),
                                "box": f["box"],
                                "already_marked": True,
                                "status": "duplicate",
                                "message": f"{student_name} is already marked present (database constraint)",
                                "constraint_violation": True
                            })
                            logger.warning(f"Database constraint prevented duplicate: {student_name} ({student_id})")
                        else:
                            results.append({
                                "match": {"user_id": student_id, "name": student_name},
                                "distance": round(float(min_d), 4),
                                "confidence": round((1 - min_d) * 100, 1),
                                "box": f["box"],
                                "already_marked": False,
                                "status": "error",
                                "message": f"❌ Database error: {str(db_error)}"
                            })
                            logger.error(f"Database error for {student_name}: {db_error}")

                else:
                    # No match found
                    results.append({
                        "match": None, 
                        "distance": round(float(min_d), 4) if min_d != float('inf') else None,
                        "confidence": round((1 - min_d) * 100, 1) if min_d != float('inf') else None,
                        "box": f["box"],
                        "status": "no_match",
                        "message": "Face not recognized - please ensure you are registered"
                    })

            processing_time = time.time() - start_time
            
            # Count successful markings vs duplicates
            successful_markings = len([r for r in results if r.get("status") == "marked_present"])
            duplicate_attempts = len([r for r in results if r.get("status") == "duplicate"])
            
            return jsonify({
                "success": True,
                "faces": results,
                "processing_time": round(processing_time, 3),
                "session_id": session_id,
                "summary": {
                    "total_faces": len(faces),
                    "successful_markings": successful_markings,
                    "duplicate_attempts": duplicate_attempts,
                    "no_matches": len(faces) - successful_markings - duplicate_attempts
                }
            })

        except Exception as e:
            logger.error(f"Attendance error: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return jsonify({
                "error": f"Attendance marking failed: {str(e)}",
                "success": False
            }), 500

@attendance_session_bp.route("/session/<session_id>/attendance", methods=["GET"])
def get_session_attendance(session_id):
    """Get attendance records for a specific session"""
    supabase = current_app.config.get("SUPABASE")
    if not supabase:
        return jsonify({"success": False, "error": "Database connection error"}), 500
    
    try:
        # First, verify the session exists and get its database ID
        session_result = supabase.table('attendance_sessions').select('*').eq('session_id', session_id).execute()
        if not session_result.data:
            return jsonify({"success": False, "error": "Session not found"}), 404
        
        session = session_result.data[0]
        session_db_id = session['id']  # UUID from database
        
        # Get attendance records for this session
        attendance_result = supabase.table('attendance_records')\
            .select('*')\
            .eq('session_id', session_db_id)\
            .order('marked_at', desc=True)\
            .execute()
        
        attendance_records = attendance_result.data if attendance_result.data else []
        
        # Format the response for frontend
        formatted_records = []
        for record in attendance_records:
            formatted_records.append({
                "id": record.get('id'),
                "student_id": record.get('student_enrollment'),
                "student_name": record.get('student_name'),
                "marked_at": record.get('marked_at'),
                "status": record.get('status', 'present'),
                "confidence": record.get('confidence'),
                "created_at": record.get('created_at')
            })
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "session_info": {
                "subject": session.get('subject'),
                "department": session.get('department'),
                "year": session.get('year'),
                "division": session.get('division'),
                "date": session.get('date'),
                "status": session.get('status'),
                "start_time": session.get('start_time'),
                "end_time": session.get('end_time')
            },
            "attendance_records": formatted_records,
            "total_present": len(formatted_records),
            "last_updated": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error fetching session attendance: {e}")
        return jsonify({
            "success": False, 
            "error": f"Failed to fetch attendance: {str(e)}"
        }), 500

@attendance_session_bp.route("/models/status", methods=["GET"])
def get_models_status():
    """Check if the AI models are ready for attendance marking"""
    model_manager = current_app.config.get("MODEL_MANAGER")
    if not model_manager:
        return jsonify({"ready": False, "error": "Model manager not initialized"})
    
    return jsonify({
        "ready": model_manager.is_ready(),
        "detector_loaded": hasattr(model_manager, 'detector') and model_manager.detector is not None,
        "status": "ready" if model_manager.is_ready() else "loading"
    })
