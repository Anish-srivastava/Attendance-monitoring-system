"""
Supabase helper functions for database operations
Replaces MongoDB queries with Supabase Postgrest queries
"""
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class SupabaseHelper:
    """Helper class for Supabase database operations"""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
    
    # ==================== STUDENTS TABLE ====================
    
    def get_student_by_id(self, student_id):
        """Get student by student_id"""
        try:
            response = self.supabase.table('students').select('*').eq('student_id', student_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting student: {e}")
            return None
    
    def get_student_by_email(self, email):
        """Get student by email"""
        try:
            response = self.supabase.table('students').select('*').eq('email', email).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting student by email: {e}")
            return None
    
    def get_all_students(self, filters=None):
        """Get all students with optional filters"""
        try:
            query = self.supabase.table('students').select('*')
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            response = query.execute()
            return response.data
        except Exception as e:
            logger.error(f"Error getting students: {e}")
            return []
    
    def create_student(self, student_data):
        """Create a new student record"""
        try:
            # Convert embeddings to JSON if needed
            if 'embeddings' in student_data and isinstance(student_data['embeddings'], list):
                student_data['embeddings'] = json.dumps(student_data['embeddings'])
            
            student_data['created_at'] = datetime.utcnow().isoformat()
            student_data['updated_at'] = datetime.utcnow().isoformat()
            
            response = self.supabase.table('students').insert(student_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating student: {e}")
            raise e
    
    def update_student(self, student_id, update_data):
        """Update student record"""
        try:
            update_data['updated_at'] = datetime.utcnow().isoformat()
            
            response = self.supabase.table('students').update(update_data).eq('student_id', student_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating student: {e}")
            raise e
    
    def delete_student(self, student_id):
        """Delete student record"""
        try:
            response = self.supabase.table('students').delete().eq('student_id', student_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting student: {e}")
            return False
    
    # ==================== ATTENDANCE SESSIONS ====================
    
    def create_attendance_session(self, session_data):
        """Create a new attendance session"""
        try:
            session_data['created_at'] = datetime.utcnow().isoformat()
            session_data['updated_at'] = datetime.utcnow().isoformat()
            
            response = self.supabase.table('attendance_sessions').insert(session_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise e
    
    def get_session_by_id(self, session_id):
        """Get attendance session by ID"""
        try:
            response = self.supabase.table('attendance_sessions').select('*').eq('session_id', session_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting session: {e}")
            return None
    
    def update_session(self, session_id, update_data):
        """Update attendance session"""
        try:
            update_data['updated_at'] = datetime.utcnow().isoformat()
            
            response = self.supabase.table('attendance_sessions').update(update_data).eq('session_id', session_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating session: {e}")
            raise e
    
    # ==================== ATTENDANCE RECORDS ====================
    
    def mark_attendance(self, attendance_data):
        """Mark attendance for a student"""
        try:
            attendance_data['created_at'] = datetime.utcnow().isoformat()
            attendance_data['marked_at'] = datetime.utcnow().isoformat()
            
            response = self.supabase.table('attendance_records').insert(attendance_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error marking attendance: {e}")
            raise e
    
    def get_attendance_by_session(self, session_id):
        """Get all attendance records for a session"""
        try:
            response = self.supabase.table('attendance_records').select('*').eq('session_id', session_id).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error getting attendance records: {e}")
            return []
    
    def get_student_attendance(self, student_id, filters=None):
        """Get attendance records for a specific student"""
        try:
            query = self.supabase.table('attendance_records').select('*').eq('student_enrollment', student_id)
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            response = query.execute()
            return response.data
        except Exception as e:
            logger.error(f"Error getting student attendance: {e}")
            return []
    
    # ==================== USERS TABLE ====================
    
    def get_user_by_email(self, email):
        """Get user by email"""
        try:
            response = self.supabase.table('users').select('*').eq('email', email).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def create_user(self, user_data):
        """Create a new user"""
        try:
            user_data['created_at'] = datetime.utcnow().isoformat()
            user_data['updated_at'] = datetime.utcnow().isoformat()
            
            response = self.supabase.table('users').insert(user_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise e
