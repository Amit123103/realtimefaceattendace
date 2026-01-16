from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import os
from datetime import datetime, date
from pathlib import Path
import json
import secrets
import io

from database import engine, get_db, Base
from models import Student, Attendance, Admin
import face_utils
import qr_utils
import excel_utils
from passlib.context import CryptContext
from pydantic import BaseModel

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

class LoginRequest(BaseModel):
    username: str
    password: str

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Student Attendance System")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://localhost:5000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:5000",
        "https://amit123103.github.io",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
DATA_DIR = Path("../data")
IMAGES_DIR = DATA_DIR / "images"
STUDENT_IMAGES_DIR = IMAGES_DIR / "students"
ATTENDANCE_IMAGES_DIR = IMAGES_DIR / "attendance"

for d in [STUDENT_IMAGES_DIR, ATTENDANCE_IMAGES_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Mount static files for images
app.mount("/images", StaticFiles(directory=str(IMAGES_DIR)), name="images")

from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

# Secret key for JWT (in prod use env var)
SECRET_KEY = "super-secret-attendance-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/admin/login")

def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_admin(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    return username

# --- Auth & Setup ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

@app.on_event("startup")
def create_default_admin():
    db = next(get_db())
    admin = db.query(Admin).filter(Admin.username == "Amitkumar").first()
    if not admin:
        default_admin = Admin(
            username="Amitkumar", 
            password_hash=get_password_hash("Amitkumar1231@")
        )
        db.add(default_admin)
        db.commit()
        print("✅ Default Admin Created: Amitkumar")

@app.post("/api/admin/login")
def login_admin(creds: LoginRequest, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.username == creds.username).first()
    if not admin or not verify_password(creds.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create JWT
    access_token = create_access_token(data={"sub": admin.username})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "username": admin.username
    }

# --- Student Auth Endpoints ---
class StudentRegisterRequest(BaseModel):
    registration_number: str
    name: str
    password: str
    email: str = None
    phone: str = None
    department: str = "General"
    year: str = "1"

class StudentLoginRequest(BaseModel):
    registration_number: str
    password: str

class ForgotPasswordRequest(BaseModel):
    email: str
    new_password: str

def rotate_student_qr(student: Student, db: Session):
    """Generates a NEW QR token for the student"""
    new_token = qr_utils.generate_qr_token()
    new_payload = f"ATTENDANCE:{student.registration_number}:{new_token}"
    student.qr_token = new_token
    student.qr_payload = new_payload
    db.commit()
    return new_payload

@app.post("/api/auth/student/register")
def register_student_account(req: StudentRegisterRequest, db: Session = Depends(get_db)):
    # Check if exists
    existing = db.query(Student).filter(Student.registration_number == req.registration_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Student ID already registered")
    
    # Check email uniqueness
    if req.email:
        if db.query(Student).filter(Student.email == req.email).first():
            raise HTTPException(status_code=400, detail="Email already used")

    # Create Student
    qr_token = qr_utils.generate_qr_token()
    
    student = Student(
        registration_number=req.registration_number,
        name=req.name,
        email=req.email,
        phone_number=req.phone,
        password_hash=get_password_hash(req.password),
        department=req.department,
        year=req.year,
        qr_token=qr_token,
        qr_payload=f"ATTENDANCE:{req.registration_number}:{qr_token}",
        is_verified=1 # Auto verified since no logic requested
    )
    
    db.add(student)
    db.commit()
    
    return {"message": "Account created successfully. Please login.", "reg_no": req.registration_number}

@app.post("/api/auth/student/login")
def login_student(req: StudentLoginRequest, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.registration_number == req.registration_number).first()
    if not student:
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    if not verify_password(req.password, student.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    # ROTATE QR CODE ON LOGIN (Security Feature)
    rotate_student_qr(student, db)
    
    # Create Token
    access_token = create_access_token(data={"sub": student.registration_number, "role": "student"})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "name": student.name,
        "reg_no": student.registration_number
    }

@app.post("/api/auth/student/reset-password")
def reset_student_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    # Find student by email
    student = db.query(Student).filter(Student.email == req.email).first()
    if not student:
        raise HTTPException(status_code=404, detail="Email not found")
        
    # Update password
    student.password_hash = get_password_hash(req.new_password)
    db.commit()
    
    return {"message": "Password reset successfully. Please login with new password."}

@app.get("/api/student/me")
def get_current_student_profile(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        reg_no = payload.get("sub")
        # Ensure it's a student token if distinguishing roles
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    student = db.query(Student).filter(Student.registration_number == reg_no).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    return student


@app.post("/api/students/register")
async def register_student(
    registration_number: str = Form(...),
    name: str = Form(...),
    department: str = Form(...),
    year: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Check if exists
    existing = db.query(Student).filter(Student.registration_number == registration_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Student already registered")

    # Process Image
    content = await image.read()
    image_array = face_utils.decode_image(io.BytesIO(content))
    if image_array is None:
        raise HTTPException(status_code=400, detail="Invalid image file")

    # Face Detection & Encoding
    encoding, error = face_utils.get_face_embedding(image_array)
    if error:
        raise HTTPException(status_code=400, detail=error)

    # Save Image
    filename = f"{registration_number}_{int(datetime.now().timestamp())}.jpg"
    image_path = STUDENT_IMAGES_DIR / filename
    face_utils.save_image_to_disk(image_array, image_path)
    
    # Generate QR
    qr_token = qr_utils.generate_qr_token()
    qr_payload = f"ATTENDANCE:{registration_number}:{qr_token}"

    student = Student(
        registration_number=registration_number,
        name=name,
        department=department,
        year=year,
        face_encoding=encoding, # JSON list
        face_image_path=f"/images/students/{filename}",
        qr_token=qr_token,
        qr_payload=qr_payload
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    
    return {"message": "Student registered successfully", "student_id": student.id}

@app.get("/api/students/{reg_no}/qr")
def get_student_qr(reg_no: str, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.registration_number == reg_no).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    img_bytes = qr_utils.create_qr_code(student.qr_payload)
    return StreamingResponse(img_bytes, media_type="image/png")

@app.get("/api/students/{reg_no}")
def get_student_details(reg_no: str, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.registration_number == reg_no).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

# --- Attendance ---

@app.post("/api/attendance/face")
async def mark_face_attendance(
    image: UploadFile = File(None), 
    db: Session = Depends(get_db)
):
    if not image:
        raise HTTPException(status_code=400, detail="No image provided")
        
    content = await image.read()
    input_image = face_utils.decode_image(io.BytesIO(content))
    
    if input_image is None:
        raise HTTPException(status_code=400, detail="Invalid image")
        
    start_time = datetime.now()
    
    # Get encoding of input face
    unknown_encoding, error = face_utils.get_face_embedding(input_image)
    if error:
        # If no face or multiple faces
        raise HTTPException(status_code=400, detail=error)
    
    # Compare with all students (Basic approach - can be optimized with FAISS for millions)
    students = db.query(Student).filter(Student.face_encoding.isnot(None)).all()
    
    best_match = None
    best_distance = 1.0
    threshold = 0.5 # Strict threshold
    
    for student in students:
        if not student.face_encoding: continue
        
        is_match, dist = face_utils.compare_faces(student.face_encoding, unknown_encoding, threshold)
        if is_match and dist < best_distance:
            best_distance = dist
            best_match = student
            
    if best_match:
        # Check duplicate for today
        today_str = date.today().isoformat()
        exists = db.query(Attendance).filter(
            Attendance.student_id == best_match.id,
            Attendance.date == today_str,
            Attendance.method == "FACE"
        ).first()
        
        confidence = int((1 - best_distance) * 100)
        
        if exists:
             return {
                "status": "duplicate",
                "message": f"Already marked for {best_match.name}",
                "student": best_match,
                "confidence": confidence
            }
            
        # Save proof image
        timestamp_val = int(datetime.now().timestamp())
        filename = f"attend_{best_match.registration_number}_{timestamp_val}.jpg"
        face_utils.save_image_to_disk(input_image, ATTENDANCE_IMAGES_DIR / filename)

        # Mark Attendance
        att = Attendance(
            student_id=best_match.id,
            method="FACE",
            date=today_str,
            status="PRESENT",
            proof_image_path=f"/images/attendance/{filename}"
        )
        db.add(att)
        db.commit()
        
        return {
            "status": "success",
            "message": f"Welcome, {best_match.name}!",
            "student": best_match,
            "confidence": confidence
        }
    
    raise HTTPException(status_code=400, detail="Face not recognized")

@app.post("/api/attendance/qr")
def mark_qr_attendance(qr_payload: str = Form(...), db: Session = Depends(get_db)):
    # Payload format: ATTENDANCE:REG_NO:TOKEN
    try:
        parts = qr_payload.split(":")
        if len(parts) != 3 or parts[0] != "ATTENDANCE":
            raise HTTPException(status_code=400, detail="Invalid QR Format")
            
        reg_no = parts[1]
        token = parts[2]
        
        student = db.query(Student).filter(Student.registration_number == reg_no).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
            
        if student.qr_token != token:
            raise HTTPException(status_code=400, detail="Invalid QR Token")
            
        # Mark
        today_str = date.today().isoformat()
        exists = db.query(Attendance).filter(
            Attendance.student_id == student.id,
            Attendance.date == today_str
        ).first() # Any method counts
        
        if exists:
             return {"status": "duplicate", "message": f"Already marked for {student.name}", "student": student}
             
        att = Attendance(
            student_id=student.id,
            method="QR",
            date=today_str,
            status="PRESENT"
        )
        db.add(att)
        db.commit()
        
        return {"status": "success", "message": "Attendance Marked via QR", "student": student}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/attendance/excel")
async def offset_excel_attendance(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    admin: str = Depends(get_current_admin)
):
    content = await file.read()
    reg_numbers, error = excel_utils.process_attendance_excel(content)
    
    if error:
        raise HTTPException(status_code=400, detail=error)
        
    results = {"marked": [], "not_found": [], "duplicates": []}
    today_str = date.today().isoformat()
    
    for reg_no in reg_numbers:
        student = db.query(Student).filter(Student.registration_number == str(reg_no)).first()
        if not student:
            results["not_found"].append(reg_no)
            continue
            
        exists = db.query(Attendance).filter(
            Attendance.student_id == student.id,
            Attendance.date == today_str
        ).first()
        
        if exists:
            results["duplicates"].append(reg_no)
        else:
            att = Attendance(
                student_id=student.id,
                method="EXCEL",
                date=today_str,
                status="PRESENT"
            )
            db.add(att)
            results["marked"].append(reg_no)
            
    db.commit()
    return results

@app.get("/api/reports")
def get_report(
    date_str: str = None, 
    db: Session = Depends(get_db),
    admin: str = Depends(get_current_admin)
):
    if not date_str:
        date_str = date.today().isoformat()
        
    attendances = db.query(Attendance).filter(Attendance.date == date_str).all()
    
    data = []
    for att in attendances:
        data.append({
            "Registration No": att.student.registration_number,
            "Name": att.student.name,
            "Dept": att.student.department,
            "Date": att.date,
            "Time": att.timestamp.strftime("%H:%M:%S"),
            "Method": att.method
        })
        
    return data

@app.get("/api/reports/download")
def download_report(date_str: str = None, db: Session = Depends(get_db)):
    data = get_report(date_str, db)
    excel_io = excel_utils.generate_report_excel(data)
    
    return StreamingResponse(
        excel_io,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=attendance_{date_str}.xlsx"}
    )

import zipfile
import shutil

@app.post("/api/students/bulk-register")
async def bulk_register_students(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: str = Depends(get_current_admin)
):
    """
    Upload a ZIP file containing student images.
    Filename should be: REGISTRATION_NUMBER.jpg (or png/jpeg)
    Example: S101.jpg -> Registers student with ID S101.
    """
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only .zip files allowed")

    temp_dir = DATA_DIR / "temp_upload"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True)

    try:
        content = await file.read()
        zip_path = temp_dir / "upload.zip"
        with open(zip_path, "wb") as f:
            f.write(content)

        results = {"success": [], "failed": [], "skipped": []}

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Process each image in the temp folder
        for img_file in temp_dir.glob("**/*"):
            if img_file.is_file() and img_file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                reg_no = img_file.stem  # Filename without extension
                
                # Check if student exists
                if db.query(Student).filter(Student.registration_number == reg_no).first():
                    results["skipped"].append(reg_no)
                    continue

                # Process Image
                image_array = face_utils.decode_image(open(img_file, "rb"))
                if image_array is None:
                    results["failed"].append(f"{reg_no} (Invalid Image)")
                    continue

                encoding, error = face_utils.get_face_embedding(image_array)
                if error:
                    results["failed"].append(f"{reg_no} ({error})")
                    continue

                # Save Release Image
                save_filename = f"{reg_no}_{int(datetime.now().timestamp())}.jpg"
                final_path = STUDENT_IMAGES_DIR / save_filename
                face_utils.save_image_to_disk(image_array, final_path)

                # Generate QR
                qr_token = qr_utils.generate_qr_token()
                qr_payload = f"ATTENDANCE:{reg_no}:{qr_token}"

                # Create Student Record (Default Name = Reg No, Dept = General)
                student = Student(
                    registration_number=reg_no,
                    name=reg_no, # Default name is ID, admin can update later
                    department="General",
                    year="1",
                    face_encoding=encoding,
                    face_image_path=f"/images/students/{save_filename}",
                    password_hash=get_password_hash(reg_no), # Default pwd = ID
                    qr_token=qr_token,
                    qr_payload=qr_payload,
                    is_verified=1
                )
                db.add(student)
                results["success"].append(reg_no)

        db.commit()
        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


# --- Frontend Static Files (Must be last) ---
FRONTEND_DIR = Path("../frontend")
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
else:
    print("⚠️ Frontend directory not found. Static files will not be served.")
