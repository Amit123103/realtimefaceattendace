# Student Attendance System (FastAPI Version)

This is the new, modern version of the Attendance System using FastAPI, SQLite, and **OpenCV SFace** (State-of-the-art Face Recognition).

## Architecture
- **Backend**: FastAPI (Python)
- **Database**: SQLite (`attendance.db`)
- **Face Recognition**: `opencv-python` (SFace + YuNet)
  - Uses ONNX models (Downloaded automatically or via script).
  - No complex compilation required (Works on any Windows machine).
- **Frontend**: HTML5, Vanilla JS, CSS Glassmorphism.

## Prerequisites
- Python 3.8+
- No special Visual Studio Build Tools required anymore!

## Installation

1. Navigate to the backend folder:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements_fastapi.txt
   ```

3. Download Face Models (Only needed once, usually auto-downloaded by the setup, but good to run manually if needed):
   ```bash
   python download_models.py
   ```

## Running the Application

1. Start the server (from `backend` folder):
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. Open the frontend:
   - **Recommended**: Serve frontend with a local server (Webcam requires secure context or localhost):
     ```bash
     cd ../frontend
     python -m http.server 3000
     ```
     Then visit `http://localhost:3000`.

## Features / How to Test

1. **Registration**:
   - Go to "Register Student".
   - Fill form, capture face with webcam (ensure good lighting).
   - "Complete Registration".
   - Check `backend/data/images/students` to see the saved image.

2. **Face Attendance**:
   - Go to "Mark Attendance" -> "Face Scan".
   - Allow camera.
   - Look at the camera.
   - Result will show "Welcome, [Name] (Confidence%)".
   - Re-scanning immediately should say "Duplicate".

3. **QR Attendance**:
   - Generate a QR for a student (Currently generated during registration).
   - Use the API: `GET http://localhost:8000/api/students/{reg_no}/qr` to download it.
   - Show this QR to the "QR Scan" camera.

4. **Excel Upload**:
   - Go to "Admin & Reports".
   - Create a simple CSV with a column `registration_number`.
   - Upload it.
   - See results.

## Troubleshooting

- **"Models not initialized"**: Ensure you ran `python download_models.py`.
- **"Face not detected"**: Ensure good lighting. The system strictly enforces finding ONE face.
- **"Face not match"**:
  - The threshold is set to 0.5 (Cosine Distance).
  - To make it stricter, lower the value in `backend/main.py`.
  - To make it looser, increase the value (max 0.6 recommended).
