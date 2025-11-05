// config/api.ts - Centralized API configuration
const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "https://attendance-monitoring-system-g96f.onrender.com";

export const API_ENDPOINTS = {
  // Base URL
  BASE_URL,
  
  // Authentication
  SIGNUP: `${BASE_URL}/api/signup`,
  SIGNIN: `${BASE_URL}/api/signin`,
  LOGOUT: `${BASE_URL}/api/logout`,
  USER_PROFILE: `${BASE_URL}/api/user/profile`,
  SWITCH_ROLE: `${BASE_URL}/api/switch-role`,

  // Student Management
  REGISTER_STUDENT: `${BASE_URL}/api/register-student`,
  STUDENTS: `${BASE_URL}/api/students`,
  STUDENTS_COUNT: `${BASE_URL}/api/students/count`,
  STUDENTS_DEPARTMENTS: `${BASE_URL}/api/students/departments`,
  STUDENTS_SEARCH: `${BASE_URL}/api/students/search`,
  STUDENTS_STATS: `${BASE_URL}/api/students/stats`,
  UPDATE_STUDENT: (id: string) => `${BASE_URL}/api/update-student/${id}`,
  DELETE_STUDENT: (id: string) => `${BASE_URL}/api/delete-student/${id}`,

  // Teacher Endpoints
  TEACHER_STUDENTS_SEARCH: `${BASE_URL}/api/teacher/students/search`,
  TEACHER_STUDENT: (id: string) => `${BASE_URL}/api/teacher/student/${id}`,

  // Attendance Management
  ATTENDANCE: `${BASE_URL}/api/attendance`,
  ATTENDANCE_EXPORT: `${BASE_URL}/api/attendance/export`,
  ATTENDANCE_CREATE_SESSION: `${BASE_URL}/api/attendance/create_session`,
  ATTENDANCE_ACTIVE_SESSIONS: `${BASE_URL}/api/attendance/active_sessions`,
  ATTENDANCE_SESSION_STATUS: (sessionId: string) => `${BASE_URL}/api/attendance/session_status/${sessionId}`,
  ATTENDANCE_END_SESSION: `${BASE_URL}/api/attendance/end_session`,
  ATTENDANCE_REAL_MARK: `${BASE_URL}/api/attendance/real-mark`,
  ATTENDANCE_SESSION_ATTENDANCE: (sessionId: string) => `${BASE_URL}/api/attendance/session/${sessionId}/attendance`,
  ATTENDANCE_MODELS_STATUS: `${BASE_URL}/api/attendance/models/status`,

  // Demo Session
  DEMO_RECOGNIZE: `${BASE_URL}/api/demo/recognize`,
  DEMO_SESSION: `${BASE_URL}/api/demo/session`,
  DEMO_SESSION_LOG: (sessionId: string) => `${BASE_URL}/api/demo/session/${sessionId}/log`,
  DEMO_MODELS_STATUS: `${BASE_URL}/api/demo/models/status`,

  // Health Check
  HEALTH: `${BASE_URL}/health`,
};

export default API_ENDPOINTS;