from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, LargeBinary, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    registration_number = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    department = Column(String)
    year = Column(String)
    
    # Auth Fields
    email = Column(String, unique=True, index=True, nullable=True)
    phone_number = Column(String, nullable=True)
    password_hash = Column(String, nullable=True)
    
    # OTP Fields
    otp_code = Column(String, nullable=True)
    otp_expiry = Column(DateTime, nullable=True)
    is_verified = Column(Integer, default=0) # 0=False, 1=True using Integer for SQLite comp
    
    # Store face encoding as JSON list of floats
    face_encoding = Column(JSON, nullable=True) 
    face_image_path = Column(String, nullable=True)
    
    # Secure QR token
    qr_token = Column(String, unique=True, index=True)
    qr_payload = Column(String) # The actual content in the QR code
    
    created_at = Column(DateTime, default=datetime.now)

    attendances = relationship("Attendance", back_populates="student")

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    
    method = Column(String) # FACE, QR, EXCEL
    timestamp = Column(DateTime, default=datetime.now, index=True)
    date = Column(String, index=True) # YYYY-MM-DD for easy querying
    status = Column(String, default="PRESENT")
    
    proof_image_path = Column(String, nullable=True)

    student = relationship("Student", back_populates="attendances")
