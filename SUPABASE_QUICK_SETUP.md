# 🚀 Supabase Setup Guide for Attendance Management System

## Step 1: Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Click "Start your project"
3. Sign up/Sign in with GitHub
4. Click "New Project"
5. Choose organization
6. Set project name: "attendance-management"
7. Set password (save this!)
8. Choose region (closest to you)
9. Click "Create new project"

## Step 2: Get Your Credentials
After project creation:
1. Go to Settings → API
2. Copy these values:

```
Project URL: https://[your-project-id].supabase.co
anon key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... (long string)
```

## Step 3: Set Up Database Schema
1. Go to SQL Editor in Supabase
2. Copy and run the schema from `backend/supabase_schema.sql`

## Step 4: Configure Render Environment Variables
Add these in Render Environment Variables:

```
SUPABASE_URL=https://[your-project-id].supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... (anon key)
SECRET_KEY=b84de7a101be89c5d5a1648217608583dd9bd7f99f7c760cc6d60e69a66249e0
FLASK_ENV=production
THRESHOLD=0.6
```

## Step 5: Test Connection
After deployment, test these endpoints:
- GET /health - Should show healthy status
- GET / - Should show "Backend running successfully!"

## 🔒 Security Notes
- Never use service_role key in client-side code
- Always use anon/public key for client applications
- Keep your database password secure
- Set up Row Level Security (RLS) for production