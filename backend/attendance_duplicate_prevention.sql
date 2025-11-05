-- Enhanced Supabase Schema Update for Attendance Duplicate Prevention
-- Run this SQL in your Supabase SQL Editor

-- Add unique constraint to prevent duplicate attendance records
-- This ensures that a student can only be marked present once per session
ALTER TABLE attendance_records 
ADD CONSTRAINT unique_student_session_attendance 
UNIQUE (session_id, student_enrollment);

-- Add additional indexes for performance
CREATE INDEX IF NOT EXISTS idx_attendance_records_student_enrollment ON attendance_records(student_enrollment);
CREATE INDEX IF NOT EXISTS idx_attendance_records_marked_at ON attendance_records(marked_at);
CREATE INDEX IF NOT EXISTS idx_attendance_records_status ON attendance_records(status);

-- Create a composite index for the unique constraint
CREATE INDEX IF NOT EXISTS idx_attendance_records_session_student ON attendance_records(session_id, student_enrollment);

-- Add a function to check for existing attendance before insert
CREATE OR REPLACE FUNCTION check_duplicate_attendance()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if student is already marked for this session
    IF EXISTS (
        SELECT 1 FROM attendance_records 
        WHERE session_id = NEW.session_id 
        AND student_enrollment = NEW.student_enrollment
        AND id != COALESCE(NEW.id, '00000000-0000-0000-0000-000000000000'::uuid)
    ) THEN
        RAISE EXCEPTION 'Student % is already marked present for this session', NEW.student_name;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to prevent duplicates
DROP TRIGGER IF EXISTS prevent_duplicate_attendance ON attendance_records;
CREATE TRIGGER prevent_duplicate_attendance
    BEFORE INSERT OR UPDATE ON attendance_records
    FOR EACH ROW
    EXECUTE FUNCTION check_duplicate_attendance();

-- Create a view for attendance statistics
CREATE OR REPLACE VIEW attendance_summary AS
SELECT 
    s.id as session_id,
    s.session_id as session_code,
    s.subject,
    s.department,
    s.year,
    s.division,
    s.date,
    s.start_time,
    s.status as session_status,
    COUNT(ar.id) as total_present,
    COUNT(DISTINCT ar.student_enrollment) as unique_students_present,
    MAX(ar.marked_at) as last_attendance_time
FROM attendance_sessions s
LEFT JOIN attendance_records ar ON s.id = ar.session_id AND ar.status = 'present'
GROUP BY s.id, s.session_id, s.subject, s.department, s.year, s.division, s.date, s.start_time, s.status;

-- Create function to get session attendance stats
CREATE OR REPLACE FUNCTION get_session_attendance_stats(session_uuid UUID)
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'session_id', s.session_id,
        'total_present', COUNT(ar.id),
        'unique_students', COUNT(DISTINCT ar.student_enrollment),
        'attendance_list', json_agg(
            json_build_object(
                'student_id', ar.student_enrollment,
                'student_name', ar.student_name,
                'marked_at', ar.marked_at,
                'confidence', ar.confidence
            ) ORDER BY ar.marked_at
        )
    ) INTO result
    FROM attendance_sessions s
    LEFT JOIN attendance_records ar ON s.id = ar.session_id
    WHERE s.id = session_uuid
    GROUP BY s.id, s.session_id;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Add comments for documentation
COMMENT ON CONSTRAINT unique_student_session_attendance ON attendance_records IS 
'Prevents duplicate attendance records for the same student in the same session';

COMMENT ON FUNCTION check_duplicate_attendance() IS 
'Trigger function to prevent duplicate attendance entries before database insert/update';

COMMENT ON VIEW attendance_summary IS 
'Aggregated view showing attendance statistics for each session';

COMMENT ON FUNCTION get_session_attendance_stats(UUID) IS 
'Returns detailed attendance statistics for a specific session';