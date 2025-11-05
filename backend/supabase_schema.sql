-- Supabase Database Schema for Attendance Management System
-- Run this SQL in your Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users/Auth table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('student', 'teacher', 'admin')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Students table
CREATE TABLE IF NOT EXISTS students (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id VARCHAR(50) UNIQUE NOT NULL,
    student_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(20),
    department VARCHAR(100),
    year VARCHAR(50),
    division VARCHAR(10),
    semester VARCHAR(10),
    embeddings JSONB, -- Store face embeddings as JSON array
    registration_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Attendance sessions table
CREATE TABLE IF NOT EXISTS attendance_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(100) UNIQUE NOT NULL,
    teacher_id UUID REFERENCES users(id),
    subject VARCHAR(255),
    department VARCHAR(100),
    year VARCHAR(50),
    division VARCHAR(10),
    semester VARCHAR(10),
    date DATE NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    end_time TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'ended')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Attendance records table
CREATE TABLE IF NOT EXISTS attendance_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES attendance_sessions(id) ON DELETE CASCADE,
    student_id UUID REFERENCES students(id),
    student_enrollment VARCHAR(50),
    student_name VARCHAR(255),
    marked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'present' CHECK (status IN ('present', 'absent', 'late')),
    confidence FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_students_student_id ON students(student_id);
CREATE INDEX IF NOT EXISTS idx_students_email ON students(email);
CREATE INDEX IF NOT EXISTS idx_attendance_sessions_date ON attendance_sessions(date);
CREATE INDEX IF NOT EXISTS idx_attendance_records_session_id ON attendance_records(session_id);
CREATE INDEX IF NOT EXISTS idx_attendance_records_student_id ON attendance_records(student_id);

-- Enable Row Level Security (RLS) - But allow service role access
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE students ENABLE ROW LEVEL SECURITY;
ALTER TABLE attendance_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE attendance_records ENABLE ROW LEVEL SECURITY;

-- RLS Policies - Allow backend API access with anon key

-- Users table policies - Allow all operations for API
CREATE POLICY "Allow all operations on users" ON users
    FOR ALL USING (true) WITH CHECK (true);

-- Students table policies - Allow all operations
CREATE POLICY "Allow all operations on students" ON students
    FOR ALL USING (true) WITH CHECK (true);

-- Attendance sessions policies - Allow all operations
CREATE POLICY "Allow all operations on attendance_sessions" ON attendance_sessions
    FOR ALL USING (true) WITH CHECK (true);

-- Attendance records policies - Allow all operations
CREATE POLICY "Allow all operations on attendance_records" ON attendance_records
    FOR ALL USING (true) WITH CHECK (true);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_students_updated_at BEFORE UPDATE ON students
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_attendance_sessions_updated_at BEFORE UPDATE ON attendance_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
