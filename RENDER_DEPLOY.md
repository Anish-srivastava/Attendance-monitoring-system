# Attendance Management System

A full-stack face recognition attendance system built with Flask (backend) and Next.js (frontend).

## 🚀 Render Deployment

This repository contains both frontend and backend services that can be deployed separately on Render.

### Backend Service (Flask)
- **Service Type**: Web Service
- **Runtime**: Python 3.11+
- **Root Directory**: `backend`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python app.py`

### Frontend Service (Next.js)
- **Service Type**: Web Service
- **Runtime**: Node.js 18+
- **Root Directory**: `frontend`
- **Build Command**: `npm install && npm run build`
- **Start Command**: `npm start`

## Environment Variables

### Backend (.env)
```
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
FLASK_ENV=production
PORT=5000
```

### Frontend (.env)
```
NEXT_PUBLIC_API_URL=https://your-backend-service.onrender.com
NODE_ENV=production
```

## 📁 Project Structure

```
├── backend/           # Flask API server
│   ├── app.py        # Main Flask application
│   ├── requirements.txt
│   └── ...
├── frontend/         # Next.js web app
│   ├── package.json
│   ├── next.config.ts
│   └── ...
└── README.md         # This file
```

## Deployment Steps

1. Deploy Backend first to get the API URL
2. Deploy Frontend with the backend URL in environment variables
3. Both services will run independently but communicate via API calls

## Features

- Face recognition attendance tracking
- Real-time session management
- Student registration and management
- Attendance reports and analytics
- Teacher dashboard
- Auto-refresh capabilities