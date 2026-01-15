# Quick Start Guide - Face Recognition Attendance System

## Important Note About face_recognition Library

The `face_recognition` library requires `dlib`, which can be challenging to install on Windows. Here are your options:

### Option 1: Install Pre-built Wheels (Recommended for Windows)

1. Download pre-built `dlib` wheel from: https://github.com/z-mahmud22/Dlib_Windows_Python3.x
2. Install it: `pip install dlib-19.24.1-cp311-cp311-win_amd64.whl` (adjust version for your Python)
3. Then install: `pip install face-recognition`

### Option 2: Use OpenCV Face Detection (Simpler Alternative)

I can create a simplified version using only OpenCV's face detection (no recognition). This will:
- ✅ Detect faces in images
- ✅ Capture and store student photos
- ✅ Work without complex dependencies
- ❌ Won't recognize faces automatically (manual verification needed)

### Option 3: Docker (Cross-platform)

Run the entire system in Docker to avoid dependency issues.

## Current Installation Status

The system is attempting to install `face_recognition` which may take 5-10 minutes on Windows as it builds `dlib` from source.

**If installation fails**, I recommend Option 2 (OpenCV-only version) which will work immediately.

## Running the Project (Once Dependencies are Installed)

```bash
# Navigate to backend folder
cd face-attendance-system/backend

# Start the server
python app.py
```

The server will run on `http://localhost:5000`

Then open `frontend/index.html` in your browser.

## Default Admin Credentials

- Username: `admin`
- Password: `admin123`

## Troubleshooting

### face_recognition won't install?
- Try the pre-built wheels (Option 1)
- Or use the simplified OpenCV version (Option 2)

### Server won't start?
- Check if port 5000 is available
- Verify all dependencies are installed
- Check Python version (3.8+)

### Camera not working?
- Grant browser camera permissions
- Use HTTPS or localhost
- Check if another app is using the camera

---

**Need help?** Let me know if you want me to create the simplified OpenCV-only version!
