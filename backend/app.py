# app.py - OPTIMIZED VERSION WITH SUPABASE AND STABILITY
import os
import time
import logging
import threading
import gc
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
import numpy as np
from supabase_client import init_supabase, get_supabase_client
from server_stability import ServerStabilityManager, stable_endpoint, safe_memory_operation

# Blueprint imports
from auth.routes import auth_bp

# Optional student/teacher blueprints
try:
    from student.registration import student_registration_bp
except ImportError:
    student_registration_bp = None

try:
    from student.updatedetails import student_update_bp
except ImportError:
    student_update_bp = None

try:
    from student.demo_session import demo_session_bp
except ImportError:
    demo_session_bp = None

try:
    from student.view_attendance import attendance_bp
except ImportError:
    attendance_bp = None

try:
    from teacher.attendance_records import attendance_session_bp
except ImportError:
    attendance_session_bp = None

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

# Supabase setup (replaces MongoDB)
THRESHOLD = float(os.getenv("THRESHOLD", "0.6"))

# Initialize Supabase client
supabase = init_supabase()

# OPTIMIZED MODEL MANAGER CLASS
class ModelManager:
    """
    Singleton class to manage face recognition models
    Ensures models are loaded only once and shared across all requests
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize_models()
        return cls._instance

    @safe_memory_operation
    def _initialize_models(self):
        """Initialize all face recognition models with proper error handling"""
        logger.info("🤖 Starting model initialization...")
        start_time = time.time()

        self.models_ready = False
        self.detector = None
        self.deepface_ready = False
        self.cached_embeddings = {}  # Add caching

        try:
            # 1. Initialize MTCNN detector with default parameters
            from mtcnn import MTCNN
            logger.info("Loading MTCNN detector...")
            self.detector = MTCNN()
            logger.info("✅ MTCNN detector loaded successfully")

            # 2. Preload DeepFace model properly with memory management
            from deepface import DeepFace
            logger.info("Warming up DeepFace Facenet512 model...")

            # Force model download and initialization with dummy prediction
            dummy_img = np.zeros((160, 160, 3), dtype=np.uint8)

            # This forces the model to be downloaded and cached
            _ = DeepFace.represent(
                dummy_img, 
                model_name='Facenet512', 
                detector_backend='skip',
                enforce_detection=False
            )

            # Additional warm-up with different image size
            dummy_img_2 = np.ones((224, 224, 3), dtype=np.uint8) * 128
            _ = DeepFace.represent(
                dummy_img_2, 
                model_name='Facenet512', 
                detector_backend='skip',
                enforce_detection=False
            )

            self.deepface_ready = True
            logger.info("✅ DeepFace Facenet512 model warmed up successfully")

            self.models_ready = True

            initialization_time = time.time() - start_time
            logger.info(f"🎉 All models initialized successfully in {initialization_time:.2f} seconds")
            
            # Force garbage collection after model loading
            gc.collect()

        except Exception as e:
            logger.error(f"❌ Model initialization failed: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            self.models_ready = False
            raise e

    def get_detector(self):
        """Get the MTCNN detector instance"""
        if not self.models_ready:
            raise RuntimeError("Models not properly initialized")
        return self.detector

    def is_ready(self):
        """Check if all models are ready"""
        return self.models_ready and self.deepface_ready

    def health_check(self):
        """Perform model health check"""
        try:
            if not self.models_ready:
                return False

            # Test MTCNN
            test_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            _ = self.detector.detect_faces(test_img)

            # Test DeepFace
            from deepface import DeepFace
            test_face = np.random.randint(0, 255, (160, 160, 3), dtype=np.uint8)
            _ = DeepFace.represent(
                test_face, 
                model_name='Facenet512', 
                detector_backend='skip',
                enforce_detection=False
            )

            return True

        except Exception as e:
            logger.error(f"Model health check failed: {e}")
            return False

# Initialize the model manager (singleton)
logger.info("Initializing Model Manager...")
model_manager = ModelManager()

# Flask app
app = Flask(__name__)
CORS(app)

# Configure Flask app with Supabase client and model instances
app.config["SUPABASE"] = supabase
app.config["THRESHOLD"] = THRESHOLD

# CRITICAL: Pass model manager to Flask config so blueprints can access it
app.config["MODEL_MANAGER"] = model_manager
app.config["MTCNN_DETECTOR"] = model_manager.get_detector()

bcrypt = Bcrypt(app)

# Initialize stability manager
stability_manager = ServerStabilityManager(app)

# Enhanced global error handlers to ensure JSON responses
@app.errorhandler(404)
@stable_endpoint
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found",
        "message": f"The requested URL was not found on the server."
    }), 404

@app.errorhandler(405)
@stable_endpoint
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": "Method not allowed",
        "message": f"The method is not allowed for the requested URL."
    }), 405

@app.errorhandler(500)
@stable_endpoint
def internal_error(error):
    stability_manager.log_error(error)
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "message": "An internal server error occurred. Please try again."
    }), 500

@app.errorhandler(503)
@stable_endpoint
def service_unavailable(error):
    return jsonify({
        "success": False,
        "error": "Service temporarily unavailable",
        "message": "Server is experiencing high load. Please try again later."
    }), 503

@app.errorhandler(Exception)
@stable_endpoint
def handle_exception(e):
    # Handle any unhandled exceptions
    stability_manager.log_error(e)
    logger.error(f"Unhandled exception: {e}")
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "message": "An unexpected error occurred."
    }), 500

# Health check endpoint
@app.route('/health', methods=['GET'])
@stable_endpoint
def health_check():
    """Health check endpoint to verify model status"""
    model_status = model_manager.is_ready()
    model_health = model_manager.health_check()

    return {
        "status": "healthy" if model_status and model_health else "unhealthy",
        "models_ready": model_status,
        "models_healthy": model_health,
        "timestamp": time.time()
    }

# Register blueprints
app.register_blueprint(auth_bp)

if student_registration_bp:
    app.register_blueprint(student_registration_bp)
    logger.info("✅ Student registration blueprint registered")

if student_update_bp:
    app.register_blueprint(student_update_bp)
    logger.info("✅ Student update blueprint registered")

if demo_session_bp:
    app.register_blueprint(demo_session_bp)
    logger.info("✅ Demo session blueprint registered")

if attendance_bp:
    app.register_blueprint(attendance_bp)
    logger.info("✅ Attendance blueprint registered")

if attendance_session_bp:
    app.register_blueprint(attendance_session_bp)
    logger.info("✅ Attendance session blueprint registered")

# List all registered routes
logger.info("\nRegistered Flask Routes:")
for rule in app.url_map.iter_rules():
    logger.info(f"  {rule}")

if __name__ == "__main__":
    logger.info("🚀 Starting Flask server...")

    # Final model verification before starting
    if model_manager.is_ready():
        port = int(os.environ.get("PORT", 5000))  # Use Render's PORT or default to 5000
        logger.info(f"🎯 All systems ready! Server starting on http://0.0.0.0:{port}")
        app.run(host="0.0.0.0", port=port, debug=False)  # Set debug=False for production
    else:
        logger.error("❌ Cannot start server - models not ready")
        exit(1)