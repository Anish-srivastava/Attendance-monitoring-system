"use client";

import { useState, useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Camera, ArrowLeft, Play, Square, User, BarChart3, Clock, Users } from "lucide-react";
import CameraCapture, { FaceData } from "../../components/CameraCapture";
import { API_ENDPOINTS } from "../../../config/api";

interface RecognizeResult {
  match: { user_id: string; name: string } | null;
  distance: number | null;
  confidence?: number;
  box?: [number, number, number, number];
}

interface ActiveSession {
  id: string;
  session_id: string;
  subject: string;
  department: string;
  year: string;
  division: string;
  date: string;
  start_time: string;
  status: string;
}

export default function DemoSession() {
  const router = useRouter();
  const [isLiveActive, setIsLiveActive] = useState(false);
  const [lastResult, setLastResult] = useState<RecognizeResult | null>(null);
  const [processedImage, setProcessedImage] = useState<string | null>(null);
  const [activeSessions, setActiveSessions] = useState<ActiveSession[]>([]);
  const [selectedSession, setSelectedSession] = useState<ActiveSession | null>(null);
  const [loadingSessions, setLoadingSessions] = useState(false);
  const [attendanceStatus, setAttendanceStatus] = useState<'idle' | 'marking' | 'success' | 'error'>('idle');
  const [attendanceMessage, setAttendanceMessage] = useState<string>('');
  const [studentAttendanceStatus, setStudentAttendanceStatus] = useState<{[sessionId: string]: boolean}>({});
  const [isAttendanceMarked, setIsAttendanceMarked] = useState(false);
  const [remainingTime, setRemainingTime] = useState<number | null>(null);
  const [sessionTimer, setSessionTimer] = useState<NodeJS.Timeout | null>(null);

  // Fetch active sessions
  const fetchActiveSessions = useCallback(async () => {
    setLoadingSessions(true);
    try {
      const res = await fetch(API_ENDPOINTS.ATTENDANCE_ACTIVE_SESSIONS);
      const data = await res.json();
      
      if (data.success) {
        setActiveSessions(data.sessions || []);
      } else {
        console.error("Failed to fetch sessions:", data.error);
      }
    } catch (err) {
      console.error("Error fetching sessions:", err);
    } finally {
      setLoadingSessions(false);
    }
  }, []);

  // Start session timer to track remaining time
  const startSessionTimer = useCallback((sessionId: string) => {
    // Clear existing timer
    if (sessionTimer) {
      clearInterval(sessionTimer);
    }

    const timer = setInterval(async () => {
      try {
        const res = await fetch(API_ENDPOINTS.ATTENDANCE_SESSION_STATUS(sessionId));
        const data = await res.json();
        
        if (data.success) {
          setRemainingTime(data.remaining_minutes);
          
          if (data.status === 'ended' || data.remaining_minutes <= 0) {
            setSelectedSession(null);
            setIsLiveActive(false);
            setAttendanceMessage('Session has ended');
            clearInterval(timer);
            setSessionTimer(null);
            fetchActiveSessions(); // Refresh session list
          }
        }
      } catch (error) {
        console.error("Error checking session status:", error);
      }
    }, 30000); // Check every 30 seconds

    setSessionTimer(timer);
  }, [sessionTimer, fetchActiveSessions]);

  // Auto-refresh sessions every 10 seconds
  useEffect(() => {
    fetchActiveSessions();
    const interval = setInterval(fetchActiveSessions, 10000);
    
    // Cleanup function
    return () => {
      clearInterval(interval);
      if (sessionTimer) {
        clearInterval(sessionTimer);
      }
    };
  }, [fetchActiveSessions]);

  const handleRecognize = useCallback(async (dataUrl: string) => {
    if (!isLiveActive) return;

    // Skip if attendance is already marked for this session
    if (selectedSession && isAttendanceMarked) {
      return;
    }

    try {
      // If a session is selected, use attendance marking endpoint
      const endpoint = selectedSession 
        ? API_ENDPOINTS.ATTENDANCE_REAL_MARK
        : API_ENDPOINTS.DEMO_RECOGNIZE;
      
      const payload = selectedSession 
        ? { image: dataUrl, session_id: selectedSession.session_id }
        : { image: dataUrl };

      // Set marking status for attendance
      if (selectedSession && !isAttendanceMarked) {
        setAttendanceStatus('marking');
        setAttendanceMessage('Processing your attendance...');
      }

      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();

      if (data.success && data.faces && data.faces.length > 0) {
        const face = data.faces[0];
        setLastResult(face);
        setProcessedImage(data.processed_image || null);

        // Handle attendance marking success
        if (selectedSession && face.match) {
          if (face.already_marked || face.status === 'duplicate') {
            // Student already marked - stop further attempts
            setIsAttendanceMarked(true);
            setAttendanceStatus('error');
            setAttendanceMessage(face.message || `${face.match.name} is already marked present for this session`);
            
            // Stop live capture for this session
            setIsLiveActive(false);
            
            // Update session tracking
            setStudentAttendanceStatus(prev => ({
              ...prev,
              [selectedSession.session_id]: true
            }));
            
          } else if (face.status === 'marked_present') {
            // Successfully marked attendance - stop further attempts
            setIsAttendanceMarked(true);
            setAttendanceStatus('success');
            setAttendanceMessage(face.message || `Attendance marked successfully for ${face.match.name}!`);
            
            // Stop live capture after successful marking
            setIsLiveActive(false);
            
            // Update session tracking
            setStudentAttendanceStatus(prev => ({
              ...prev,
              [selectedSession.session_id]: true
            }));
            
          } else {
            setAttendanceStatus('error');
            setAttendanceMessage(face.message || 'Failed to mark attendance. Please try again.');
          }
          
          // Clear status message after 8 seconds
          setTimeout(() => {
            setAttendanceStatus('idle');
            setAttendanceMessage('');
          }, 8000);
        }
      } else {
        setLastResult(null);
        setProcessedImage(null);

        // Handle attendance marking failure
        if (selectedSession && !isAttendanceMarked) {
          setAttendanceStatus('error');
          if (data.error && data.error.includes('already marked')) {
            setIsAttendanceMarked(true);
            setIsLiveActive(false);
            setAttendanceMessage('You have already marked attendance for this session.');
            
            // Update session tracking
            setStudentAttendanceStatus(prev => ({
              ...prev,
              [selectedSession.session_id]: true
            }));
          } else {
            setAttendanceMessage(data.error || 'Failed to mark attendance. Please try again.');
          }
          
          // Clear error message after 8 seconds
          setTimeout(() => {
            setAttendanceStatus('idle');
            setAttendanceMessage('');
          }, 8000);
        }
      }
    } catch (err) {
      console.error(err);
      
      // Handle network errors for attendance
      if (selectedSession && !isAttendanceMarked) {
        setAttendanceStatus('error');
        setAttendanceMessage('Network error. Please check your connection and try again.');
        
        setTimeout(() => {
          setAttendanceStatus('idle');
          setAttendanceMessage('');
        }, 8000);
      }
    }
  }, [isLiveActive, selectedSession, isAttendanceMarked]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-lg border-b border-slate-200 shadow-sm">
        <div className="px-4 sm:px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Left Section */}
            <div className="flex items-center gap-4">
              <button
                onClick={() => router.push("/dashboard")}
                className="p-2 rounded-lg bg-slate-100 hover:bg-slate-200 transition-colors group"
              >
                <ArrowLeft className="w-6 h-6 text-slate-600 group-hover:text-slate-800 transition-colors" />
              </button>
              
              <div className="flex items-center gap-3">
                <div className="p-3 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl shadow-lg">
                  <Camera className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl sm:text-2xl font-bold text-slate-800 tracking-tight">
                    {selectedSession ? "Attendance Marking" : "Face Recognition Demo"}
                  </h1>
                  <p className="text-slate-600 text-sm font-medium">
                    {selectedSession 
                      ? `Attending: ${selectedSession.subject} - ${selectedSession.department}`
                      : "Live demonstration and testing"
                    }
                  </p>
                </div>
              </div>
            </div>

            {/* Status Indicator */}
            <div className="flex items-center gap-3">
              <div className={`flex items-center gap-2 px-4 py-2 rounded-xl border-2 transition-all ${
                isLiveActive 
                  ? "bg-emerald-50 border-emerald-200 shadow-sm" 
                  : "bg-slate-100 border-slate-200"
              }`}>
                <div className={`w-2 h-2 rounded-full ${
                  isLiveActive ? "bg-emerald-500 animate-pulse" : "bg-slate-400"
                }`} />
                <span className={`text-sm font-semibold ${
                  isLiveActive ? "text-emerald-700" : "text-slate-600"
                }`}>
                  {isLiveActive ? "LIVE" : "STANDBY"}
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Active Sessions Section */}
      <div className="px-4 sm:px-6 py-4 bg-white/70 border-b border-slate-200">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <Clock className="w-5 h-5 text-slate-600" />
              <h2 className="text-lg font-semibold text-slate-800">Active Attendance Sessions</h2>
              {loadingSessions && (
                <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
              )}
            </div>
            <button
              onClick={fetchActiveSessions}
              className="px-3 py-2 text-sm bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
            >
              Refresh
            </button>
          </div>

          {activeSessions.length === 0 ? (
            <div className="text-center py-8 text-slate-500">
              <Users className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p>No active attendance sessions found</p>
              <p className="text-sm">Teachers haven't started any sessions yet</p>
            </div>
          ) : (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {activeSessions.map((session) => (
                <div
                  key={session.session_id}
                  onClick={() => {
                    setSelectedSession(session);
                    // Reset attendance status when changing sessions
                    setIsAttendanceMarked(studentAttendanceStatus[session.session_id] || false);
                    setAttendanceStatus('idle');
                    setAttendanceMessage('');
                    startSessionTimer(session.session_id);
                  }}
                  className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${
                    selectedSession?.session_id === session.session_id
                      ? "border-blue-500 bg-blue-50 shadow-md"
                      : "border-slate-200 bg-white hover:border-slate-300 hover:shadow-sm"
                  }`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-semibold text-slate-800">{session.subject}</h3>
                    <span className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded-full">
                      Active
                    </span>
                  </div>
                  <div className="space-y-1 text-sm text-slate-600">
                    <p><span className="font-medium">Department:</span> {session.department}</p>
                    <p><span className="font-medium">Year:</span> {session.year}</p>
                    <p><span className="font-medium">Division:</span> {session.division}</p>
                    <p><span className="font-medium">Date:</span> {session.date}</p>
                    {selectedSession?.session_id === session.session_id && remainingTime !== null && (
                      <p>
                        <span className="font-medium">Time Left:</span> 
                        <span className={`ml-1 ${
                          remainingTime <= 5 ? "text-red-600 font-bold" : 
                          remainingTime <= 10 ? "text-amber-600 font-semibold" : 
                          "text-green-600"
                        }`}>
                          {remainingTime} minutes
                        </span>
                      </p>
                    )}
                  </div>
                  {selectedSession?.session_id === session.session_id && (
                    <div className="mt-3 text-sm text-blue-600 font-medium">
                      ✓ Selected for attendance
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Attendance Interface - Show when session is selected */}
          {selectedSession && (
            <div className="mt-6 p-4 bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl border-2 border-blue-200 shadow-md">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-blue-500 rounded-lg">
                  <User className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-slate-800">
                    {isAttendanceMarked ? "Attendance Completed" : "Attendance Mode Active"}
                  </h3>
                  <p className="text-slate-600 text-sm">
                    {isAttendanceMarked 
                      ? `You are already marked present for ${selectedSession.subject}`
                      : `Ready to mark attendance for ${selectedSession.subject}`
                    }
                  </p>
                </div>
              </div>

              {/* Attendance Status Messages */}
              {attendanceMessage && (
                <div className={`p-3 rounded-lg mb-4 ${
                  attendanceStatus === 'success' 
                    ? 'bg-green-100 border border-green-200 text-green-800'
                    : attendanceStatus === 'error'
                    ? 'bg-red-100 border border-red-200 text-red-800'
                    : 'bg-blue-100 border border-blue-200 text-blue-800'
                }`}>
                  <div className="flex items-center gap-2">
                    {attendanceStatus === 'marking' && (
                      <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                    )}
                    <span className="font-medium">{attendanceMessage}</span>
                  </div>
                </div>
              )}

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-slate-600 font-medium">Session:</span>
                  <p className="text-slate-800">{selectedSession.subject}</p>
                </div>
                <div>
                  <span className="text-slate-600 font-medium">Department:</span>
                  <p className="text-slate-800">{selectedSession.department} - {selectedSession.year} {selectedSession.division}</p>
                </div>
                <div>
                  <span className="text-slate-600 font-medium">Date:</span>
                  <p className="text-slate-800">{selectedSession.date}</p>
                </div>
                <div>
                  <span className="text-slate-600 font-medium">Time:</span>
                  <p className="text-slate-800">{selectedSession.start_time}</p>
                </div>
              </div>

              <div className="mt-4 p-3 bg-white rounded-lg border border-slate-200">
                <h4 className="font-semibold text-slate-800 mb-2">📋 How to mark attendance:</h4>
                <ol className="text-slate-600 text-sm space-y-1">
                  <li>1. Click "Start Demo" if not already active</li>
                  <li>2. Position your face clearly in the camera</li>
                  <li>3. Wait for face recognition to identify you</li>
                  <li>4. Your attendance will be automatically marked</li>
                </ol>
              </div>

              <div className="mt-4 flex gap-3">
                <button
                  onClick={() => {
                    setSelectedSession(null);
                    setAttendanceStatus('idle');
                    setAttendanceMessage('');
                    setIsAttendanceMarked(false);
                  }}
                  className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg transition-colors"
                >
                  Cancel Selection
                </button>
                {isAttendanceMarked ? (
                  <div className="px-4 py-2 bg-green-100 text-green-800 rounded-lg font-medium flex items-center gap-2">
                    <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                    Attendance Marked
                  </div>
                ) : !isLiveActive ? (
                  <button
                    onClick={() => setIsLiveActive(true)}
                    className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors flex items-center gap-2"
                  >
                    <Play className="w-4 h-4" />
                    Start Attendance
                  </button>
                ) : (
                  <button
                    onClick={() => setIsLiveActive(false)}
                    className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors flex items-center gap-2"
                  >
                    <Square className="w-4 h-4" />
                    Stop Capture
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Controls - Moved Above */}
      <div className="px-4 sm:px-6 py-4 bg-white/50 border-b border-slate-200">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
            {/* Left Controls */}
            <div className="flex flex-wrap gap-3">
              <button
                onClick={() => setIsLiveActive(!isLiveActive)}
                className={`px-6 py-3 rounded-xl font-semibold transition-all duration-300 flex items-center justify-center gap-3 border-2 ${
                  isLiveActive 
                    ? "bg-red-50 hover:bg-red-100 text-red-600 border-red-200 hover:border-red-300 shadow-sm" 
                    : "bg-emerald-50 hover:bg-emerald-100 text-emerald-600 border-emerald-200 hover:border-emerald-300 shadow-sm"
                }`}
              >
                {isLiveActive ? (
                  <>
                    <Square className="w-5 h-5" />
                    Stop Demo
                  </>
                ) : (
                  <>
                    <Play className="w-5 h-5" />
                    Start Demo
                  </>
                )}
              </button>

              <button
                onClick={() => router.push("/dashboard")}
                className="px-6 py-3 rounded-xl font-semibold bg-blue-50 hover:bg-blue-100 text-blue-600 border-2 border-blue-200 hover:border-blue-300 transition-all duration-300 flex items-center justify-center gap-3 shadow-sm"
              >
                <ArrowLeft className="w-5 h-5" />
                Back to Dashboard
              </button>
            </div>

            {/* Right Stats */}
            <div className="flex flex-wrap gap-4 text-sm">
              <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white border border-slate-200 shadow-sm">
                <span className="text-slate-600 font-medium">Status:</span>
                <span className={`font-semibold ${
                  isLiveActive ? "text-emerald-600" : "text-amber-600"
                }`}>
                  {isLiveActive ? "Active" : "Inactive"}
                </span>
              </div>
              
              <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white border border-slate-200 shadow-sm">
                <span className="text-slate-600 font-medium">Last Result:</span>
                <span className={`font-semibold ${
                  lastResult?.match ? "text-emerald-600" : "text-slate-600"
                }`}>
                  {lastResult?.match ? "Match Found" : "No Match"}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="p-4 sm:p-6">
        <div className="max-w-7xl mx-auto">
          {/* Camera and Results Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 sm:gap-8 mb-8">
            {/* Camera Feed */}
            <div className="bg-white rounded-2xl border-2 border-purple-200 p-6 shadow-lg">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-3 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl shadow-lg">
                  <Camera className="w-5 h-5 text-white" />
                </div>
                <h2 className="text-xl font-bold text-slate-800">Camera Feed</h2>
              </div>
              
              <div className="relative rounded-xl overflow-hidden bg-slate-100 border-2 border-slate-200">
                <CameraCapture
                  isLiveMode={isLiveActive}
                  captureIntervalMs={1000}
                  onCapture={handleRecognize}
                  facesData={
                    lastResult && lastResult.box
                      ? [{
                          ...lastResult,
                          box: lastResult.box
                        }]
                      : []
                  }
                />
                
                {/* Overlay Status */}
                {!isLiveActive && (
                  <div className="absolute inset-0 bg-slate-900/70 flex items-center justify-center backdrop-blur-sm">
                    <div className="text-center">
                      <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mx-auto mb-4 shadow-lg">
                        <Play className="w-8 h-8 text-slate-600" />
                      </div>
                      <p className="text-white font-semibold">Click Start Demo to begin</p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Results Panel */}
            <div className="bg-white rounded-2xl border-2 border-blue-200 p-6 shadow-lg">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-3 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg">
                  <BarChart3 className="w-5 h-5 text-white" />
                </div>
                <h2 className="text-xl font-bold text-slate-800">Recognition Results</h2>
              </div>

              {/* Results Content */}
              <div className="space-y-6">
                {/* Status Card */}
                <div className={`p-4 rounded-xl border-2 transition-all ${
                  lastResult?.match 
                    ? "bg-emerald-50 border-emerald-200 shadow-sm" 
                    : "bg-slate-50 border-slate-200"
                }`}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-slate-600 text-sm font-medium">Status</span>
                    <div className={`px-3 py-1 rounded-full text-xs font-semibold ${
                      lastResult?.match 
                        ? "bg-emerald-100 text-emerald-700 border border-emerald-200" 
                        : "bg-slate-100 text-slate-600 border border-slate-200"
                    }`}>
                      {lastResult?.match ? "MATCH FOUND" : "NO MATCH"}
                    </div>
                  </div>
                  <p className="text-slate-800 font-bold">
                    {lastResult?.match 
                      ? `Identified: ${lastResult.match.name}` 
                      : "No face recognized"}
                  </p>
                </div>

                {/* User Info - Only shown when match is found */}
                {lastResult?.match && (
                  <div className="p-4 rounded-xl bg-blue-50 border-2 border-blue-200 shadow-sm">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="p-2 bg-blue-500 rounded-lg">
                        <User className="w-5 h-5 text-white" />
                      </div>
                      <h3 className="text-lg font-bold text-slate-800">User Information</h3>
                    </div>
                    <div className="space-y-3">
                      <div>
                        <span className="text-slate-600 text-sm font-medium">Name:</span>
                        <p className="text-slate-800 font-semibold">{lastResult.match.name}</p>
                      </div>
                      <div>
                        <span className="text-slate-600 text-sm font-medium">User ID:</span>
                        <p className="text-slate-800 font-mono text-sm bg-slate-100 px-2 py-1 rounded">{lastResult.match.user_id}</p>
                      </div>
                    </div>
                  </div>
                )}

                {/* No Match State */}
                {!lastResult?.match && isLiveActive && (
                  <div className="p-6 rounded-xl bg-slate-50 border-2 border-slate-200">
                    <div className="text-center">
                      <div className="w-12 h-12 bg-slate-200 rounded-full flex items-center justify-center mx-auto mb-3">
                        <User className="w-6 h-6 text-slate-500" />
                      </div>
                      <p className="text-slate-700 font-semibold">No face recognized</p>
                      <p className="text-slate-500 text-sm mt-1">Ensure face is clearly visible in camera</p>
                    </div>
                  </div>
                )}

                {/* Instructions */}
                <div className="p-4 rounded-xl bg-gradient-to-br from-slate-50 to-blue-50 border-2 border-slate-200">
                  <h4 className="text-slate-800 font-bold mb-3">
                    {selectedSession ? "Attendance Instructions:" : "How it works:"}
                  </h4>
                  <ul className="text-slate-600 text-sm space-y-2">
                    <li className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 bg-blue-500 rounded-full"></span>
                      {selectedSession ? "Click 'Start Demo' to begin attendance marking" : "Click 'Start Demo' to begin face recognition"}
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 bg-blue-500 rounded-full"></span>
                      Position your face clearly in the camera view
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 bg-blue-500 rounded-full"></span>
                      {selectedSession ? "Your attendance will be automatically marked" : "Results will appear here in real-time"}
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 bg-blue-500 rounded-full"></span>
                      {selectedSession ? "Wait for confirmation message" : "Click 'Stop Demo' to end the session"}
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Processed Image Section */}
          {processedImage && (
            <div className="bg-white rounded-2xl border-2 border-cyan-200 p-6 shadow-lg">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-3 bg-gradient-to-br from-cyan-500 to-cyan-600 rounded-xl shadow-lg">
                  <Camera className="w-5 h-5 text-white" />
                </div>
                <h3 className="text-xl font-bold text-slate-800">Processed Image</h3>
              </div>
              
              <div className="flex justify-center">
                <div className="rounded-xl overflow-hidden bg-slate-100 border-2 border-slate-200 max-w-2xl shadow-lg">
                  <img 
                    src={processedImage} 
                    alt="Processed" 
                    className="w-full h-auto max-h-96 object-contain"
                  />
                </div>
              </div>
              
              <p className="text-slate-600 text-sm mt-4 text-center">
                AI-processed image with face detection and recognition overlay
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}