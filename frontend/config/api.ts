// API Configuration for different environments
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000';

// API endpoints
export const API_ENDPOINTS = {
  // Auth endpoints
  SIGNUP: `${API_BASE_URL}/api/signup`,
  SIGNIN: `${API_BASE_URL}/api/signin`,
  LOGOUT: `${API_BASE_URL}/api/logout`,
  USER_PROFILE: `${API_BASE_URL}/api/user/profile`,
  SWITCH_ROLE: `${API_BASE_URL}/api/switch-role`,

  // Student endpoints
  REGISTER_STUDENT: `${API_BASE_URL}/api/register-student`,
  STUDENTS: `${API_BASE_URL}/api/students`,
  STUDENTS_COUNT: `${API_BASE_URL}/api/students/count`,
  STUDENTS_DEPARTMENTS: `${API_BASE_URL}/api/students/departments`,
  STUDENTS_SEARCH: `${API_BASE_URL}/api/students/search`,
  STUDENTS_STATS: `${API_BASE_URL}/api/students/stats`,
  UPDATE_STUDENT: (id: string) => `${API_BASE_URL}/api/update-student/${id}`,
  DELETE_STUDENT: (id: string) => `${API_BASE_URL}/api/delete-student/${id}`,

  // Teacher endpoints
  TEACHER_STUDENTS_SEARCH: `${API_BASE_URL}/api/teacher/students/search`,
  TEACHER_STUDENT: (id: string) => `${API_BASE_URL}/api/teacher/student/${id}`,

  // Attendance endpoints
  ATTENDANCE: `${API_BASE_URL}/api/attendance`,
  ATTENDANCE_EXPORT: `${API_BASE_URL}/api/attendance/export`,
  ATTENDANCE_CREATE_SESSION: `${API_BASE_URL}/api/attendance/create_session`,
  ATTENDANCE_ACTIVE_SESSIONS: `${API_BASE_URL}/api/attendance/active_sessions`,
  ATTENDANCE_SESSION_STATUS: (sessionId: string) => `${API_BASE_URL}/api/attendance/session_status/${sessionId}`,
  ATTENDANCE_END_SESSION: `${API_BASE_URL}/api/attendance/end_session`,
  ATTENDANCE_REAL_MARK: `${API_BASE_URL}/api/attendance/real-mark`,
  ATTENDANCE_SESSION_ATTENDANCE: (sessionId: string) => `${API_BASE_URL}/api/attendance/session/${sessionId}/attendance`,
  ATTENDANCE_MODELS_STATUS: `${API_BASE_URL}/api/attendance/models/status`,

  // Demo endpoints
  DEMO_RECOGNIZE: `${API_BASE_URL}/api/demo/recognize`,
  DEMO_SESSION: `${API_BASE_URL}/api/demo/session`,
  DEMO_SESSION_LOG: (sessionId: string) => `${API_BASE_URL}/api/demo/session/${sessionId}/log`,
  DEMO_MODELS_STATUS: `${API_BASE_URL}/api/demo/models/status`,

  // Health endpoint
  HEALTH: `${API_BASE_URL}/health`,
};

export default API_ENDPOINTS;