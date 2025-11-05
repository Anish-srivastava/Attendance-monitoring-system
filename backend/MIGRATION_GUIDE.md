# 🔄 MongoDB se Supabase Migration - Complete Guide

## ✅ Kya-kya change hua hai?

### 1. **Database**: MongoDB → Supabase (PostgreSQL)
- ❌ Local MongoDB installation ki zarurat nahi
- ✅ Cloud-based Supabase database
- ✅ Free tier available (500MB database)
- ✅ Auto-generated REST APIs
- ✅ Real-time capabilities

### 2. **Changed Files**:
- `backend/app.py` - Supabase client integration
- `backend/auth/routes.py` - Supabase queries
- `backend/requirements.txt` - Updated dependencies
- `backend/supabase_client.py` - NEW: Supabase connection
- `backend/supabase_helper.py` - NEW: Database helper functions
- `backend/supabase_schema.sql` - NEW: Database schema
- `backend/.env` - NEW: Environment variables

---

## 🚀 Setup Instructions (Step by Step)

### **Step 1: Supabase Account Banao**

1. Visit: https://supabase.com
2. "Start your project" button click karo
3. GitHub ya email se sign up karo
4. New project create karo:
   - **Project name**: `attendance-management`
   - **Database Password**: Strong password banao (save kar lo!)
   - **Region**: Asia Pacific (Mumbai) ya nearest region select karo
5. "Create new project" click karo
6. Wait karo 2-3 minutes (project create ho raha hai)

### **Step 2: Database Schema Setup**

1. Supabase dashboard mein **SQL Editor** open karo (left sidebar)
2. **New Query** button click karo
3. `backend/supabase_schema.sql` file open karo
4. Saara SQL code copy karo aur SQL Editor mein paste karo
5. **RUN** button click karo (ya Ctrl+Enter press karo)
6. Success message aana chahiye

### **Step 3: API Keys Copy Karo**

1. Supabase dashboard mein **Settings** (gear icon) click karo
2. **API** section mein jao
3. Yeh do values copy karo:
   - **Project URL**: `https://xxxxxxxxxxxxx.supabase.co`
   - **anon public** key (bahut lamba key hoga)

### **Step 4: Backend Configuration**

1. `backend/.env` file open karo
2. Apne Supabase credentials paste karo:

```env
SUPABASE_URL=https://your-actual-project-id.supabase.co
SUPABASE_KEY=your-actual-anon-key-paste-here
SECRET_KEY=some-random-secret-key-12345
FLASK_ENV=development
THRESHOLD=0.6
```

### **Step 5: Dependencies Install Karo**

```powershell
cd backend
pip install -r requirements.txt
```

Yeh packages install honge:
- `supabase` - Supabase Python client
- `postgrest` - PostgreSQL REST client
- Existing packages (flask, deepface, mtcnn, etc.)

### **Step 6: Backend Start Karo**

```powershell
cd backend
python app.py
```

✅ Success message:
```
✅ Supabase client initialized successfully
🤖 Starting model initialization...
✅ MTCNN detector loaded successfully
✅ DeepFace Facenet512 model warmed up successfully
🎯 All systems ready! Server starting on http://0.0.0.0:5000
```

---

## 📊 Database Tables

### **1. users** (Authentication)
```sql
- id (UUID)
- email (VARCHAR)
- password_hash (VARCHAR)
- role (student/teacher/admin)
- created_at, updated_at
```

### **2. students** (Student Records)
```sql
- id (UUID)
- student_id (VARCHAR) - Enrollment number
- student_name (VARCHAR)
- email (VARCHAR)
- phone_number (VARCHAR)
- department, year, division, semester
- embeddings (JSONB) - Face embeddings array
- registration_date, created_at, updated_at
```

### **3. attendance_sessions** (Attendance Sessions)
```sql
- id (UUID)
- session_id (VARCHAR)
- teacher_id (UUID)
- subject, department, year, division, semester
- date, start_time, end_time
- status (active/ended)
```

### **4. attendance_records** (Attendance Marks)
```sql
- id (UUID)
- session_id (UUID)
- student_id (UUID)
- student_enrollment (VARCHAR)
- student_name (VARCHAR)
- marked_at (TIMESTAMP)
- status (present/absent/late)
- confidence (FLOAT)
```

---

## 🔍 How to Verify Setup

### **1. Check Supabase Tables**
- Supabase dashboard → **Table Editor**
- 4 tables dikhnecahiye: `users`, `students`, `attendance_sessions`, `attendance_records`

### **2. Test API**
```powershell
# Health check
curl http://localhost:5000/health

# Expected response:
{
  "status": "healthy",
  "models_ready": true,
  "models_healthy": true
}
```

### **3. Test Signup**
```powershell
curl -X POST http://localhost:5000/api/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test",
    "email": "test@example.com",
    "password": "test123",
    "userType": "student"
  }'
```

### **4. Check Data in Supabase**
- Supabase → **Table Editor** → **users table**
- Newly created user dikhn chahiye

---

## 🆚 MongoDB vs Supabase Comparison

| Feature | MongoDB | Supabase |
|---------|---------|----------|
| **Setup** | Local installation required | Cloud-based, no installation |
| **Cost** | Free (self-hosted) | Free tier: 500MB DB, 1GB storage |
| **Database Type** | NoSQL (Document) | SQL (PostgreSQL) |
| **Queries** | `find()`, `insert_one()` | REST API, SQL queries |
| **Real-time** | Change Streams | Built-in real-time |
| **Dashboard** | Compass (separate) | Built-in web dashboard |
| **Auth** | Custom implementation | Built-in auth system |
| **Backup** | Manual | Automatic (paid plans) |

---

## 🔧 Helper Functions (supabase_helper.py)

```python
from supabase_helper import SupabaseHelper

# Initialize
helper = SupabaseHelper(supabase_client)

# Student operations
student = helper.get_student_by_id("12345")
all_students = helper.get_all_students()
helper.create_student(student_data)
helper.update_student("12345", update_data)

# Attendance operations
session = helper.create_attendance_session(session_data)
helper.mark_attendance(attendance_data)
records = helper.get_attendance_by_session(session_id)
```

---

## ⚠️ Important Notes

1. **`.env` file ko Git mein commit mat karo**
   - Already `.gitignore` mein add hai

2. **`service_role` key use mat karo client-side**
   - Sirf `anon public` key use karo

3. **Free tier limits**:
   - 500MB database
   - 1GB file storage
   - 2GB bandwidth per month
   - 50,000 monthly active users

4. **Row Level Security (RLS)**:
   - Already enabled in schema
   - Adjust policies according to your needs

---

## 🐛 Troubleshooting

### Error: "Supabase credentials not found"
**Solution**: Check `.env` file exists and has correct values

### Error: "Connection refused"
**Solution**: Verify `SUPABASE_URL` is correct (starts with `https://`)

### Error: "relation 'students' does not exist"
**Solution**: Run `supabase_schema.sql` again in SQL Editor

### Error: "Invalid API key"
**Solution**: Use `anon public` key, not `service_role` key

---

## 📞 Support

Issues ho to:
1. Check Supabase dashboard logs
2. Check Flask backend terminal output
3. Verify all environment variables
4. Check database schema is created properly

---

## ✅ Migration Checklist

- [ ] Supabase account created
- [ ] Project created
- [ ] Database schema executed
- [ ] API credentials copied
- [ ] `.env` file configured
- [ ] Dependencies installed
- [ ] Backend running successfully
- [ ] Test user created
- [ ] Data visible in Supabase dashboard

---

**Happy Coding! 🚀**
