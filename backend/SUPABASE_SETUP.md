# Supabase Setup Guide for Attendance Management System

## Step 1: Create Supabase Project

1. Go to [Supabase](https://supabase.com)
2. Sign up or log in
3. Click "New Project"
4. Fill in the details:
   - **Project Name**: attendance-management
   - **Database Password**: (create a strong password and save it)
   - **Region**: Choose closest to you
5. Click "Create new project"
6. Wait for the project to be created (2-3 minutes)

## Step 2: Get Your Supabase Credentials

1. Once your project is ready, go to **Settings** (gear icon on left sidebar)
2. Click on **API** section
3. You'll see:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **Project API keys**:
     - `anon` `public` key (this is your SUPABASE_KEY)

4. Copy these values

## Step 3: Setup Database Schema

1. Go to **SQL Editor** (in left sidebar)
2. Click **New Query**
3. Copy the entire content from `supabase_schema.sql` file
4. Paste it in the SQL Editor
5. Click **Run** (or press Ctrl+Enter)
6. You should see "Success. No rows returned" message

## Step 4: Configure Backend

1. Create a `.env` file in the `backend` folder
2. Copy content from `.env.example`
3. Replace with your actual Supabase credentials:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-public-key-here
SECRET_KEY=your-random-secret-key-here
FLASK_ENV=development
THRESHOLD=0.6
```

## Step 5: Install Dependencies

```bash
cd backend
pip install supabase python-dotenv
```

## Step 6: Verify Setup

1. Go to Supabase **Table Editor**
2. You should see these tables:
   - `users`
   - `students`
   - `attendance_sessions`
   - `attendance_records`

## Step 7: Test Connection

Run the Flask backend:
```bash
python app.py
```

You should see:
```
✅ Supabase client initialized successfully
```

## Database Structure

### Tables Overview:

**1. users** - Authentication and user roles
- `id`, `email`, `password_hash`, `role` (student/teacher/admin)

**2. students** - Student information and face embeddings
- `id`, `student_id`, `student_name`, `email`, `department`, `year`, `division`, `semester`
- `embeddings` (JSONB) - Stores 5 face embeddings

**3. attendance_sessions** - Attendance session details
- `id`, `session_id`, `teacher_id`, `subject`, `department`, `year`, `division`
- `start_time`, `end_time`, `status`

**4. attendance_records** - Individual attendance marks
- `id`, `session_id`, `student_id`, `student_enrollment`, `student_name`
- `marked_at`, `status`, `confidence`

## Benefits of Supabase over MongoDB:

✅ **Free tier includes**:
- 500 MB database
- 1 GB file storage
- 2 GB bandwidth
- Auto-generated REST APIs
- Real-time subscriptions
- Row Level Security

✅ **No local installation needed** - Cloud-hosted PostgreSQL

✅ **Built-in authentication** - Ready to use auth system

✅ **Dashboard** - Easy data viewing and management

✅ **Automatic backups** - On paid plans

## Troubleshooting

**Issue**: "Supabase credentials not found"
- **Solution**: Make sure `.env` file exists in `backend` folder with correct credentials

**Issue**: "Connection refused"
- **Solution**: Check your SUPABASE_URL - should be `https://xxxxx.supabase.co`

**Issue**: "Invalid API key"
- **Solution**: Use the `anon` `public` key from Supabase API settings, not the `service_role` key

## Security Notes

⚠️ **Never commit `.env` file to Git**
⚠️ **Never share your `service_role` key publicly**
✅ **Use `anon` key for client-side applications**
✅ **Keep your database password secure**

## Next Steps

After setup:
1. Test student registration
2. Test face recognition
3. Test attendance marking
4. View data in Supabase Table Editor
