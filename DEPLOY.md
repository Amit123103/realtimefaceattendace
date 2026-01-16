# Deployment Guide

This project is a centralized Face Attendance System combining a FastAPI backend and a static HTML/JS frontend.

## Deployment Options

### 1. Render / Railway / Heroku (PaaS)

This project is ready for Platform-as-a-Service deployment.
The `Procfile` is already configured.

**Steps:**
1.  Push this code to a GitHub repository.
2.  Connect the repository to your PaaS provider (e.g. Render).
3.  **Build Command:** `pip install -r backend/requirements_fastapi.txt`
4.  **Start Command:** `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
    *   *Note: The `Procfile` already contains this.*
5.  **Environment Variables:**
    *   Set `PYTHON_VERSION` if needed (e.g. 3.10+).

### 📋 Deployment "Cheat Sheet" (Copy & Paste these values)

When you create a new **Web Service** on Render/Railway, fill in these details:

| Field | Value |
| :--- | :--- |
| **Name** | `face-attendance` (or any name) |
| **Region** | Singapore (or closest to you) |
| **Repository** | `https://github.com/Amit123103/realtimefaceattendace` |
| **Branch** | `main` |
| **Root Directory** | `.` (Leave empty / default) |
| **Build Command** | `pip install -r backend/requirements_fastapi.txt` |
| **Start Command** | `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Environment Variables** | Key: `PYTHON_VERSION`, Value: `3.10.0` |

---

**⚠️ CRITICAL WARNING FOR FREE TIER:**
Services like Render Free Tier or Heroku are "Ephemeral". This means **every time you deploy or the app restarts, your Database and Images will be DELETED.**
To keep your data, you MUST:
1.  Use a paid plan with "Persistent Disks" (Render/Railway).
2.  OR use a Cloud Database (PostgreSQL) and Cloud Storage (AWS S3) for images.
3.  OR use a **VPS** (Option 2 below), which keeps files forever.

**Recommended Platforms:**
*   [Render](https://render.com) (Easiest, has persistent disk option)
*   [Railway](https://railway.app) (Great developer experience)
*   [PythonAnywhere](https://www.pythonanywhere.com) (Good for Python, persistent by default)

### 2. VPS (Ubuntu/Debian)

1.  Clone the repository.
2.  Install Python 3.10+ and pip.
3.  Install dependencies:
    ```bash
    pip install -r backend/requirements_fastapi.txt
    ```
4.  Run the server:
    ```bash
    cd backend
    python -m uvicorn main:app --host 0.0.0.0 --port 80
    ```
5.  Use `supervisor` or `systemd` to keep it running.

## Configuration

*   **API URL**: The frontend is configured to use relative paths (`/api`), so it will automatically work with the backend serving it.
*   **Static Files**: The backend automatically serves the `frontend` folder at the root URL `/`.
*   **Database**: Uses `sqlite` by default (`attendance.db`). For production, consider switching to PostgreSQL if data persistence across re-deployments is critical (SQLite files on some PaaS are ephemeral).

## Folder Structure

*   `backend/`: FastAPI application.
*   `frontend/`: Static HTML/CSS/JS files.
*   `data/`: Stores images and SQLite DB (Ensure this persists if possible).
