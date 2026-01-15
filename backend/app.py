from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import base64
import io
import os
from pathlib import Path
from datetime import datetime
import numpy as np
from PIL import Image
import zipfile
import tempfile

from face_engine import FaceEngine
from excel_handler import ExcelHandler
from admin_auth import AdminAuth
from qr_handler import QRCodeHandler
from pdf_generator import PDFReportGenerator
from email_service import EmailService
from analytics import AnalyticsEngine
from multi_admin import MultiAdminHandler
from support_handler import SupportHandler
from health import register_health_routes

app = Flask(__name__)

# CORS Configuration - Allow frontend from GitHub Pages and localhost
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://amit123103.github.io",
            "http://localhost:*",
            "http://127.0.0.1:*",
            "*"  # Allow all origins for development
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Configuration
UPLOAD_FOLDER = Path('../uploads')
DATA_FOLDER = Path('../data')
IMAGES_FOLDER = DATA_FOLDER / 'images'
STUDENTS_IMAGES = IMAGES_FOLDER / 'students'
ATTENDANCE_IMAGES = IMAGES_FOLDER / 'attendance'

# Ensure directories exist
for folder in [UPLOAD_FOLDER, STUDENTS_IMAGES, ATTENDANCE_IMAGES]:
    folder.mkdir(parents=True, exist_ok=True)

# Initialize components
face_engine = FaceEngine()
excel_handler = ExcelHandler()
admin_auth = AdminAuth()
qr_handler = QRCodeHandler()
pdf_generator = PDFReportGenerator()
email_service = EmailService(app)
analytics_engine = AnalyticsEngine(excel_handler)
multi_admin = MultiAdminHandler()
support_handler = SupportHandler()

# Register health check routes
register_health_routes(app)

# Helper functions
def decode_base64_image(base64_string):
    """Convert base64 string to image array"""
    try:
        # Remove data URL prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # Decode base64
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy array
        return np.array(image)
    except Exception as e:
        print(f"Error decoding image: {e}")
        return None

def save_image(image_array, filename, category='students'):
    """Save image to disk"""
    try:
        folder = STUDENTS_IMAGES if category == 'students' else ATTENDANCE_IMAGES
        filepath = folder / filename
        
        image = Image.fromarray(image_array)
        image.save(filepath)
        
        return str(filepath.relative_to(DATA_FOLDER))
    except Exception as e:
        print(f"Error saving image: {e}")
        return None

# Student Registration Endpoint
@app.route('/api/register-student', methods=['POST'])
def register_student():
    """Register a new student with face"""
    try:
        data = request.json
        
        name = data.get('name')
        registration_no = data.get('registration_no')
        image_base64 = data.get('image')
        
        # Validate inputs
        if not all([name, registration_no, image_base64]):
            return jsonify({
                'success': False,
                'message': 'Missing required fields'
            }), 400
        
        # Check if student already exists
        if excel_handler.student_exists(registration_no):
            return jsonify({
                'success': False,
                'message': 'Student with this registration number already exists'
            }), 400
        
        # Decode image
        image_array = decode_base64_image(image_base64)
        if image_array is None:
            return jsonify({
                'success': False,
                'message': 'Invalid image data'
            }), 400
        
        # Detect face
        has_face, _ = face_engine.detect_face(image_array)
        if not has_face:
            return jsonify({
                'success': False,
                'message': 'No face detected in image. Please try again.'
            }), 400
        
        # Encode face
        face_encoding = face_engine.encode_face(image_array)
        if face_encoding is None:
            return jsonify({
                'success': False,
                'message': 'Could not process face. Please ensure good lighting.'
            }), 400
        
        # Save face encoding
        if not face_engine.save_encoding(face_encoding, registration_no, 'student'):
            return jsonify({
                'success': False,
                'message': 'Error saving face data'
            }), 500
        
        # Save image
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        image_filename = f"{registration_no}_{timestamp}.jpg"
        image_path = save_image(image_array, image_filename, 'students')
        
        if image_path is None:
            return jsonify({
                'success': False,
                'message': 'Error saving image'
            }), 500
        
        # Train model with new image
        face_engine.train_model()
        
        # Add to Excel
        success, message = excel_handler.add_student(name, registration_no, image_path)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Student registered successfully!',
                'data': {
                    'name': name,
                    'registration_no': registration_no
                }
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 500
    
    except Exception as e:
        print(f"Error in register_student: {e}")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

# Mark Attendance Endpoint
@app.route('/api/mark-attendance', methods=['POST'])
def mark_attendance():
    """Mark attendance using face recognition"""
    try:
        data = request.json
        image_base64 = data.get('image')
        
        if not image_base64:
            return jsonify({
                'success': False,
                'message': 'No image provided'
            }), 400
        
        # Decode image
        image_array = decode_base64_image(image_base64)
        if image_array is None:
            return jsonify({
                'success': False,
                'message': 'Invalid image data'
            }), 400
        
        # Recognize face
        success, registration_no, confidence, message = face_engine.recognize_face(image_array, 'student')
        
        if not success:
            return jsonify({
                'success': False,
                'message': message
            }), 400
        
        # Get student details
        student = excel_handler.get_student_by_regno(registration_no)
        if not student:
            return jsonify({
                'success': False,
                'message': 'Student not found in database'
            }), 404
        
        # Save attendance image
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        image_filename = f"{registration_no}_{timestamp}.jpg"
        image_path = save_image(image_array, image_filename, 'attendance')
        
        # Record attendance
        success, message = excel_handler.add_attendance(
            student['Name'],
            registration_no,
            image_path
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Attendance marked successfully!',
                'data': {
                    'name': student['Name'],
                    'registration_no': registration_no,
                    'confidence': round(confidence, 1),
                    'time': datetime.now().strftime('%H:%M:%S')
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
    
    except Exception as e:
        print(f"Error in mark_attendance: {e}")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

# Mark Attendance with QR Code
@app.route('/api/mark-attendance-qr', methods=['POST'])
def mark_attendance_qr():
    """Mark attendance using QR code"""
    try:
        data = request.json
        qr_data = data.get('qr_data')
        
        if not qr_data:
            return jsonify({
                'success': False,
                'message': 'No QR data provided'
            }), 400
            
        # Verify QR
        valid, result = qr_handler.verify_qr_data(qr_data)
        if not valid:
            return jsonify({
                'success': False,
                'message': result
            }), 400
            
        registration_no = result
        
        # Get student details
        student = excel_handler.get_student_by_regno(registration_no)
        if not student:
            return jsonify({
                'success': False,
                'message': 'Student not found in database'
            }), 404
            
        # Record attendance
        # We don't have an image for QR scan, so we pass a placeholder path
        success, message = excel_handler.add_attendance(
            student['Name'],
            registration_no,
            "QR_In_Person"
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Attendance marked successfully via QR!',
                'data': {
                    'name': student['Name'],
                    'registration_no': registration_no,
                    'mode': 'QR Code',
                    'time': datetime.now().strftime('%H:%M:%S')
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        print(f"Error in mark_attendance_qr: {e}")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

# Admin Login Endpoint
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Admin login with password or face"""
    try:
        data = request.json
        login_type = data.get('type', 'password')
        
        if login_type == 'password':
            username = data.get('username')
            password = data.get('password')
            
            if not all([username, password]):
                return jsonify({
                    'success': False,
                    'message': 'Username and password required'
                }), 400
            
            if admin_auth.verify_password(username, password):
                session_token = admin_auth.create_session(username)
                
                return jsonify({
                    'success': True,
                    'message': 'Login successful',
                    'session_token': session_token
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': 'Invalid credentials'
                }), 401
        
        elif login_type == 'face':
            image_base64 = data.get('image')
            
            if not image_base64:
                return jsonify({
                    'success': False,
                    'message': 'No image provided'
                }), 400
            
            # Check if admin has face registered
            if not admin_auth.has_face_registered():
                return jsonify({
                    'success': False,
                    'message': 'Admin face not registered. Please use password login.'
                }), 400
            
            # Decode image
            image_array = decode_base64_image(image_base64)
            if image_array is None:
                return jsonify({
                    'success': False,
                    'message': 'Invalid image data'
                }), 400
            
            # Encode face
            face_encoding = face_engine.encode_face(image_array)
            if face_encoding is None:
                return jsonify({
                    'success': False,
                    'message': 'No face detected'
                }), 400
            
            # Verify face
            if admin_auth.verify_face(face_encoding):
                session_token = admin_auth.create_session('admin')
                
                return jsonify({
                    'success': True,
                    'message': 'Face login successful',
                    'session_token': session_token
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': 'Face not recognized'
                }), 401
        
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid login type'
            }), 400
    
    except Exception as e:
        print(f"Error in admin_login: {e}")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

# Verify Session Endpoint
@app.route('/api/admin/verify-session', methods=['POST'])
def verify_session():
    """Verify admin session token"""
    try:
        data = request.json
        session_token = data.get('session_token')
        
        if not session_token:
            return jsonify({'valid': False}), 401
        
        valid, username = admin_auth.verify_session(session_token)
        
        return jsonify({
            'valid': valid,
            'username': username if valid else None
        }), 200 if valid else 401
    
    except Exception as e:
        print(f"Error in verify_session: {e}")
        return jsonify({'valid': False}), 500

# Get All Students Endpoint
@app.route('/api/admin/students', methods=['GET'])
def get_students():
    """Get all registered students (admin only)"""
    try:
        # Verify session
        session_token = request.headers.get('Authorization')
        if not session_token:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
        valid, _ = admin_auth.verify_session(session_token)
        if not valid:
            return jsonify({'success': False, 'message': 'Invalid session'}), 401
        
        students = excel_handler.get_all_students()
        
        return jsonify({
            'success': True,
            'data': students,
            'count': len(students)
        }), 200
    
    except Exception as e:
        print(f"Error in get_students: {e}")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

# Get Attendance Records Endpoint
@app.route('/api/admin/attendance', methods=['GET'])
def get_attendance():
    """Get attendance records with optional filters (admin only)"""
    try:
        # Verify session
        session_token = request.headers.get('Authorization')
        if not session_token:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
        valid, _ = admin_auth.verify_session(session_token)
        if not valid:
            return jsonify({'success': False, 'message': 'Invalid session'}), 401
        
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        registration_no = request.args.get('registration_no')
        
        records = excel_handler.get_attendance_records(start_date, end_date, registration_no)
        
        return jsonify({
            'success': True,
            'data': records,
            'count': len(records)
        }), 200
    
    except Exception as e:
        print(f"Error in get_attendance: {e}")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

# Export Students to Excel
@app.route('/api/admin/export-students', methods=['GET'])
def export_students():
    """Export students data to Excel file"""
    try:
        # Verify session
        session_token = request.headers.get('Authorization')
        if not session_token:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
        valid, _ = admin_auth.verify_session(session_token)
        if not valid:
            return jsonify({'success': False, 'message': 'Invalid session'}), 401
        
        # Create export file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_filename = f'students_export_{timestamp}.xlsx'
        export_path = UPLOAD_FOLDER / export_filename
        
        success, message = excel_handler.export_students_to_excel(export_path)
        
        if success:
            return send_file(
                export_path,
                as_attachment=True,
                download_name=export_filename,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 500
    
    except Exception as e:
        print(f"Error in export_students: {e}")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

# Export Attendance to Excel
@app.route('/api/admin/export-attendance', methods=['GET'])
def export_attendance():
    """Export attendance records to Excel file"""
    try:
        # Verify session
        session_token = request.headers.get('Authorization')
        if not session_token:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
        valid, _ = admin_auth.verify_session(session_token)
        if not valid:
            return jsonify({'success': False, 'message': 'Invalid session'}), 401
        
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Create export file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_filename = f'attendance_export_{timestamp}.xlsx'
        export_path = UPLOAD_FOLDER / export_filename
        
        success, message = excel_handler.export_attendance_to_excel(export_path, start_date, end_date)
        
        if success:
            return send_file(
                export_path,
                as_attachment=True,
                download_name=export_filename,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 500
    
    except Exception as e:
        print(f"Error in export_attendance: {e}")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

# Bulk Upload Students
@app.route('/api/admin/bulk-upload', methods=['POST'])
def bulk_upload():
    """Process bulk student upload from CSV/Excel with images"""
    try:
        # Verify session
        session_token = request.headers.get('Authorization')
        if not session_token:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
        valid, _ = admin_auth.verify_session(session_token)
        if not valid:
            return jsonify({'success': False, 'message': 'Invalid session'}), 401
        
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No file selected'
            }), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = UPLOAD_FOLDER / filename
        file.save(filepath)
        
        # Process based on file type
        if filename.endswith('.zip'):
            # Extract ZIP file
            with zipfile.ZipFile(filepath, 'r') as zip_ref:
                extract_path = UPLOAD_FOLDER / 'temp_extract'
                zip_ref.extractall(extract_path)
            
            # Find CSV file
            csv_files = list(extract_path.glob('*.csv'))
            if not csv_files:
                return jsonify({
                    'success': False,
                    'message': 'No CSV file found in ZIP'
                }), 400
            
            csv_file = csv_files[0]
            
            # Read CSV
            with open(csv_file, 'r') as f:
                csv_data = f.read()
            
            # Import students
            success, message = excel_handler.bulk_import_students(csv_data)
            
            # Process face encodings for images
            if success:
                images_folder = extract_path / 'images'
                if images_folder.exists():
                    for image_file in images_folder.glob('*'):
                        if image_file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                            # Extract registration number from filename
                            reg_no = image_file.stem.split('_')[0]
                            
                            # Encode face
                            encoding = face_engine.encode_face(str(image_file))
                            if encoding is not None:
                                face_engine.save_encoding(encoding, reg_no, 'student')
                            
                            # Copy image to students folder
                            import shutil
                            dest = STUDENTS_IMAGES / image_file.name
                            shutil.copy(image_file, dest)
            
            # Cleanup
            import shutil
            shutil.rmtree(extract_path)
            
            return jsonify({
                'success': success,
                'message': message
            }), 200 if success else 400
        
        elif filename.endswith('.csv'):
            # Read CSV directly
            with open(filepath, 'r') as f:
                csv_data = f.read()
            
            success, message = excel_handler.bulk_import_students(csv_data)
            
            return jsonify({
                'success': success,
                'message': message
            }), 200 if success else 400
        
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid file type. Please upload CSV or ZIP file.'
            }), 400
    
    except Exception as e:
        print(f"Error in bulk_upload: {e}")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

# Register Admin Face
@app.route('/api/admin/register-face', methods=['POST'])
def register_admin_face():
    """Register admin face for face login"""
    try:
        # Verify session
        session_token = request.headers.get('Authorization')
        if not session_token:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
        valid, _ = admin_auth.verify_session(session_token)
        if not valid:
            return jsonify({'success': False, 'message': 'Invalid session'}), 401
        
        data = request.json
        image_base64 = data.get('image')
        
        if not image_base64:
            return jsonify({
                'success': False,
                'message': 'No image provided'
            }), 400
        
        # Decode image
        image_array = decode_base64_image(image_base64)
        if image_array is None:
            return jsonify({
                'success': False,
                'message': 'Invalid image data'
            }), 400
        
        # Encode face
        face_encoding = face_engine.encode_face(image_array)
        if face_encoding is None:
            return jsonify({
                'success': False,
                'message': 'No face detected. Please try again.'
            }), 400
        
        # Register admin face
        if admin_auth.register_admin_face(face_encoding):
            # Also save to face engine
            face_engine.save_encoding(face_encoding, 'admin', 'admin')
            
            return jsonify({
                'success': True,
                'message': 'Admin face registered successfully!'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Error registering face'
            }), 500
    
    except Exception as e:
        print(f"Error in register_admin_face: {e}")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

# Check Admin Face Status
@app.route('/api/admin/face-status', methods=['GET'])
def admin_face_status():
    """Check if admin has face registered"""
    try:
        has_face = admin_auth.has_face_registered()
        
        return jsonify({
            'success': True,
            'has_face': has_face
        }), 200
    
    except Exception as e:
        print(f"Error in admin_face_status: {e}")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

# Logout Endpoint
@app.route('/api/admin/logout', methods=['POST'])
def logout():
    """Logout admin"""
    try:
        data = request.json
        session_token = data.get('session_token')
        
        if session_token:
            admin_auth.logout(session_token)
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        }), 200
    
    except Exception as e:
        print(f"Error in logout: {e}")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@app.route('/api/admin/analytics/summary', methods=['GET'])
def get_analytics_summary():
    """Get overall analytics summary"""
    try:
        session_token = request.headers.get('Authorization')
        if not session_token:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
        valid, _ = admin_auth.verify_session(session_token)
        if not valid:
            return jsonify({'success': False, 'message': 'Invalid session'}), 401
        
        success, stats = analytics_engine.get_summary_stats()
        
        if success:
            return jsonify({'success': True, 'data': stats}), 200
        else:
            return jsonify({'success': False, 'message': 'Error getting stats'}), 500
    except Exception as e:
        print(f"Error in analytics_summary: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/admin/analytics/daily', methods=['GET'])
def get_daily_analytics():
    """Get daily attendance analytics"""
    try:
        session_token = request.headers.get('Authorization')
        if not session_token:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
        valid, _ = admin_auth.verify_session(session_token)
        if not valid:
            return jsonify({'success': False, 'message': 'Invalid session'}), 401
        
        days = int(request.args.get('days', 7))
        success, data = analytics_engine.get_daily_attendance(days)
        
        if success:
            return jsonify({'success': True, 'data': data}), 200
        else:
            return jsonify({'success': False, 'message': 'Error getting daily data'}), 500
    except Exception as e:
        print(f"Error in daily_analytics: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/admin/analytics/weekly', methods=['GET'])
def get_weekly_analytics():
    """Get weekly attendance trends"""
    try:
        session_token = request.headers.get('Authorization')
        if not session_token:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
        valid, _ = admin_auth.verify_session(session_token)
        if not valid:
            return jsonify({'success': False, 'message': 'Invalid session'}), 401
        
        weeks = int(request.args.get('weeks', 4))
        success, data = analytics_engine.get_weekly_trends(weeks)
        
        if success:
            return jsonify({'success': True, 'data': data}), 200
        else:
            return jsonify({'success': False, 'message': 'Error getting weekly data'}), 500
    except Exception as e:
        print(f"Error in weekly_analytics: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/admin/analytics/monthly', methods=['GET'])
def get_monthly_analytics():
    """Get monthly attendance overview"""
    try:
        session_token = request.headers.get('Authorization')
        if not session_token:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
        valid, _ = admin_auth.verify_session(session_token)
        if not valid:
            return jsonify({'success': False, 'message': 'Invalid session'}), 401
        
        success, data = analytics_engine.get_monthly_overview()
        
        if success:
            return jsonify({'success': True, 'data': data}), 200
        else:
            return jsonify({'success': False, 'message': 'Error getting monthly data'}), 500
    except Exception as e:
        print(f"Error in monthly_analytics: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/admin/analytics/student-percentages', methods=['GET'])
def get_student_percentages():
    """Get attendance percentage for all students"""
    try:
        session_token = request.headers.get('Authorization')
        if not session_token:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
        valid, _ = admin_auth.verify_session(session_token)
        if not valid:
            return jsonify({'success': False, 'message': 'Invalid session'}), 401
        
        success, data = analytics_engine.get_student_attendance_percentage()
        
        if success:
            return jsonify({'success': True, 'data': data}), 200
        else:
            return jsonify({'success': False, 'message': 'Error getting percentages'}), 500
    except Exception as e:
        print(f"Error in student_percentages: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ============================================================================
# QR CODE ENDPOINTS
# ============================================================================

@app.route('/api/admin/generate-qr/<registration_no>', methods=['GET'])
def generate_qr_code(registration_no):
    """Generate QR code for a student"""
    try:
        session_token = request.headers.get('Authorization')
        if not session_token:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
        valid, _ = admin_auth.verify_session(session_token)
        if not valid:
            return jsonify({'success': False, 'message': 'Invalid session'}), 401
        
        # Get student
        student = excel_handler.get_student_by_regno(registration_no)
        if not student:
            return jsonify({'success': False, 'message': 'Student not found'}), 404
        
        # Generate QR code
        qr_bytes = qr_handler.generate_qr_bytes(registration_no, student['Name'])
        
        if qr_bytes:
            return send_file(
                qr_bytes,
                mimetype='image/png',
                as_attachment=True,
                download_name=f'qr_{registration_no}.png'
            )
        else:
            return jsonify({'success': False, 'message': 'Error generating QR code'}), 500
    except Exception as e:
        print(f"Error in generate_qr_code: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/scan-qr-attendance', methods=['POST'])
def scan_qr_attendance():
    """Mark attendance using QR code scan"""
    try:
        data = request.json
        qr_data = data.get('qr_data')
        
        if not qr_data:
            return jsonify({'success': False, 'message': 'No QR data provided'}), 400
        
        # Verify QR data
        valid, registration_no = qr_handler.verify_qr_data(qr_data)
        
        if not valid:
            return jsonify({'success': False, 'message': registration_no}), 400
        
        # Get student
        student = excel_handler.get_student_by_regno(registration_no)
        if not student:
            return jsonify({'success': False, 'message': 'Student not found'}), 404
        
        # Mark attendance
        success, message = excel_handler.add_attendance(
            student['Name'],
            registration_no,
            'qr_scan'
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Attendance marked for {student["Name"]}',
                'data': {
                    'name': student['Name'],
                    'registration_no': registration_no,
                    'time': datetime.now().strftime('%H:%M:%S')
                }
            }), 200
        else:
            return jsonify({'success': False, 'message': message}), 400
    except Exception as e:
        print(f"Error in scan_qr_attendance: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ============================================================================
# PDF REPORT ENDPOINTS
# ============================================================================

@app.route('/api/admin/generate-pdf-report', methods=['GET'])
def generate_pdf_report():
    """Generate PDF attendance report"""
    try:
        session_token = request.headers.get('Authorization')
        if not session_token:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
        valid, _ = admin_auth.verify_session(session_token)
        if not valid:
            return jsonify({'success': False, 'message': 'Invalid session'}), 401
        
        # Get filters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Get attendance data
        attendance = excel_handler.get_attendance_records(start_date, end_date)
        
        # Generate PDF
        success, filepath = pdf_generator.generate_attendance_report(attendance, start_date, end_date)
        
        if success:
            return send_file(
                filepath,
                as_attachment=True,
                download_name=f'attendance_report_{datetime.now().strftime("%Y%m%d")}.pdf',
                mimetype='application/pdf'
            )
        else:
            return jsonify({'success': False, 'message': filepath}), 500
    except Exception as e:
        print(f"Error in generate_pdf_report: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/admin/generate-student-pdf/<registration_no>', methods=['GET'])
def generate_student_pdf(registration_no):
    """Generate PDF report for individual student"""
    try:
        session_token = request.headers.get('Authorization')
        if not session_token:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
        valid, _ = admin_auth.verify_session(session_token)
        if not valid:
            return jsonify({'success': False, 'message': 'Invalid session'}), 401
        
        # Get student
        student = excel_handler.get_student_by_regno(registration_no)
        if not student:
            return jsonify({'success': False, 'message': 'Student not found'}), 404
        
        # Get attendance records
        attendance = excel_handler.get_attendance_records(registration_no=registration_no)
        
        # Generate PDF
        success, filepath = pdf_generator.generate_student_report(student, attendance)
        
        if success:
            return send_file(
                filepath,
                as_attachment=True,
                download_name=f'student_report_{registration_no}.pdf',
                mimetype='application/pdf'
            )
        else:
            return jsonify({'success': False, 'message': filepath}), 500
    except Exception as e:
        print(f"Error in generate_student_pdf: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ============================================================================
# EMAIL NOTIFICATION ENDPOINTS
# ============================================================================

@app.route('/api/admin/send-email-report', methods=['POST'])
def send_email_report():
    """Send attendance report via email"""
    try:
        session_token = request.headers.get('Authorization')
        if not session_token:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
        valid, _ = admin_auth.verify_session(session_token)
        if not valid:
            return jsonify({'success': False, 'message': 'Invalid session'}), 401
        
        data = request.json
        recipient_email = data.get('email')
        
        if not recipient_email:
            return jsonify({'success': False, 'message': 'Email address required'}), 400
        
        # Get today's attendance
        today = datetime.now().strftime('%Y-%m-%d')
        attendance = excel_handler.get_attendance_records(start_date=today, end_date=today)
        
        # Send email
        success, message = email_service.send_attendance_report(recipient_email, attendance)
        
        if success:
            return jsonify({'success': True, 'message': 'Email sent successfully'}), 200
        else:
            return jsonify({'success': False, 'message': message}), 500
    except Exception as e:
        print(f"Error in send_email_report: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ============================================================================
# STUDENT PORTAL ENDPOINTS
# ============================================================================

@app.route('/api/student/login', methods=['POST'])
def student_login():
    """Student login with registration number"""
    try:
        data = request.json
        registration_no = data.get('registration_no')
        
        if not registration_no:
            return jsonify({'success': False, 'message': 'Registration number required'}), 400
        
        # Get student
        student = excel_handler.get_student_by_regno(registration_no)
        if not student:
            return jsonify({'success': False, 'message': 'Student not found'}), 404
        
        # Get attendance records
        attendance = excel_handler.get_attendance_records(registration_no=registration_no)
        
        # Calculate statistics
        unique_dates = set(record.get('Date') for record in excel_handler.get_attendance_records() if record.get('Date'))
        total_days = len(unique_dates) if unique_dates else 1
        attendance_count = len(attendance)
        percentage = (attendance_count / total_days * 100) if total_days > 0 else 0
        
        return jsonify({
            'success': True,
            'student': student,
            'attendance': attendance,
            'statistics': {
                'total_days': total_days,
                'present_days': attendance_count,
                'percentage': round(percentage, 2)
            }
        }), 200
    except Exception as e:
        print(f"Error in student_login: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ============================================================================
# MULTI-ADMIN ENDPOINTS
# ============================================================================

@app.route('/api/admin/manage/add-admin', methods=['POST'])
def add_new_admin():
    """Add new admin account (super_admin only)"""
    try:
        session_token = request.headers.get('Authorization')
        if not session_token:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
        valid, username = admin_auth.verify_session(session_token)
        if not valid:
            return jsonify({'success': False, 'message': 'Invalid session'}), 401
        
        # Check if user has permission
        if not multi_admin.check_permission(username, 'manage_admins'):
            return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
        
        data = request.json
        new_username = data.get('username')
        password = data.get('password')
        role = data.get('role', 'admin')
        email = data.get('email', '')
        
        if not all([new_username, password]):
            return jsonify({'success': False, 'message': 'Username and password required'}), 400
        
        success, message = multi_admin.add_admin(new_username, password, role, email)
        
        if success:
            return jsonify({'success': True, 'message': message}), 201
        else:
            return jsonify({'success': False, 'message': message}), 400
    except Exception as e:
        print(f"Error in add_new_admin: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/admin/manage/list-admins', methods=['GET'])
def list_admins():
    """Get all admin accounts (super_admin only)"""
    try:
        session_token = request.headers.get('Authorization')
        if not session_token:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
        valid, username = admin_auth.verify_session(session_token)
        if not valid:
            return jsonify({'success': False, 'message': 'Invalid session'}), 401
        
        # Check permission
        if not multi_admin.check_permission(username, 'manage_admins'):
            return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
        
        success, admins = multi_admin.get_all_admins()
        
        if success:
            return jsonify({'success': True, 'data': admins}), 200
        else:
            return jsonify({'success': False, 'message': 'Error getting admins'}), 500
    except Exception as e:
        print(f"Error in list_admins: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/admin/manage/update-role', methods=['POST'])
def update_admin_role():
    """Update admin role (super_admin only)"""
    try:
        session_token = request.headers.get('Authorization')
        if not session_token:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
        valid, username = admin_auth.verify_session(session_token)
        if not valid:
            return jsonify({'success': False, 'message': 'Invalid session'}), 401
        
        # Check permission
        if not multi_admin.check_permission(username, 'manage_admins'):
            return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
        
        data = request.json
        target_username = data.get('username')
        new_role = data.get('role')
        
        if not all([target_username, new_role]):
            return jsonify({'success': False, 'message': 'Username and role required'}), 400
        
        success, message = multi_admin.update_admin_role(target_username, new_role)
        
        if success:
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'success': False, 'message': message}), 400
    except Exception as e:
        print(f"Error in update_admin_role: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/admin/manage/deactivate', methods=['POST'])
def deactivate_admin():
    """Deactivate admin account (super_admin only)"""
    try:
        session_token = request.headers.get('Authorization')
        if not session_token:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
        valid, username = admin_auth.verify_session(session_token)
        if not valid:
            return jsonify({'success': False, 'message': 'Invalid session'}), 401
        
        # Check permission
        if not multi_admin.check_permission(username, 'manage_admins'):
            return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
        
        data = request.json
        target_username = data.get('username')
        
        if not target_username:
            return jsonify({'success': False, 'message': 'Username required'}), 400
        
        success, message = multi_admin.deactivate_admin(target_username)
        
        if success:
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'success': False, 'message': message}), 400
    except Exception as e:
        print(f"Error in deactivate_admin: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    print("=" * 50)
    print("Face Recognition Attendance System")
    print("=" * 50)
    print("Server starting on http://localhost:5000")
    print("Default admin credentials:")
    print("  Username: admin")
    print("  Password: admin123")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
# SUPPORT SYSTEM ENDPOINTS - Add to app.py before if __name__ == '__main__':

# ============================================================================
# STUDENT SUPPORT ENDPOINTS
# ============================================================================

@app.route('/api/support/create-ticket', methods=['POST'])
def create_support_ticket():
    """Create a new support ticket from student"""
    try:
        data = request.json
        student_name = data.get('student_name')
        registration_no = data.get('registration_no')
        email = data.get('email', '')
        subject = data.get('subject')
        message = data.get('message')
        
        if not all([student_name, registration_no, subject, message]):
            return jsonify({'success': False, 'message': 'All fields are required'}), 400
        
        success, result = support_handler.create_ticket(
            student_name, registration_no, email, subject, message
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Support ticket created successfully',
                'ticket_id': result
            }), 201
        else:
            return jsonify({'success': False, 'message': result}), 500
    except Exception as e:
        print(f"Error creating support ticket: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/admin/support/tickets', methods=['GET'])
def get_support_tickets():
    """Get all support tickets (admin only)"""
    try:
        session_token = request.headers.get('Authorization')
        if not session_token:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
        valid, _ = admin_auth.verify_session(session_token)
        if not valid:
            return jsonify({'success': False, 'message': 'Invalid session'}), 401
        
        status = request.args.get('status')
        success, tickets = support_handler.get_all_tickets(status)
        
        if success:
            return jsonify({'success': True, 'data': tickets}), 200
        else:
            return jsonify({'success': False, 'message': 'Error getting tickets'}), 500
    except Exception as e:
        print(f"Error getting support tickets: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/admin/support/ticket/<ticket_id>', methods=['GET'])
def get_support_ticket(ticket_id):
    """Get a specific support ticket"""
    try:
        session_token = request.headers.get('Authorization')
        if not session_token:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
        valid, _ = admin_auth.verify_session(session_token)
        if not valid:
            return jsonify({'success': False, 'message': 'Invalid session'}), 401
        
        success, ticket = support_handler.get_ticket_by_id(ticket_id)
        
        if success:
            return jsonify({'success': True, 'data': ticket}), 200
        else:
            return jsonify({'success': False, 'message': ticket}), 404
    except Exception as e:
        print(f"Error getting support ticket: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/admin/support/update-ticket', methods=['POST'])
def update_support_ticket():
    """Update support ticket status and notes"""
    try:
        session_token = request.headers.get('Authorization')
        if not session_token:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
        valid, _ = admin_auth.verify_session(session_token)
        if not valid:
            return jsonify({'success': False, 'message': 'Invalid session'}), 401
        
        data = request.json
        ticket_id = data.get('ticket_id')
        status = data.get('status')
        admin_notes = data.get('admin_notes', '')
        
        if not all([ticket_id, status]):
            return jsonify({'success': False, 'message': 'Ticket ID and status required'}), 400
        
        success, message = support_handler.update_ticket_status(ticket_id, status, admin_notes)
        
        if success:
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'success': False, 'message': message}), 400
    except Exception as e:
        print(f"Error updating support ticket: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/admin/support/stats', methods=['GET'])
def get_support_stats():
    """Get support ticket statistics"""
    try:
        session_token = request.headers.get('Authorization')
        if not session_token:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
        valid, _ = admin_auth.verify_session(session_token)
        if not valid:
            return jsonify({'success': False, 'message': 'Invalid session'}), 401
        
        success, stats = support_handler.get_ticket_stats()
        
        if success:
            return jsonify({'success': True, 'data': stats}), 200
        else:
            return jsonify({'success': False, 'message': 'Error getting stats'}), 500
    except Exception as e:
        print(f"Error getting support stats: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ============================================================================
# ADMIN SUPPORT REQUEST (Email to System Admin)
# ============================================================================

@app.route('/api/admin/support/request-help', methods=['POST'])
def admin_support_request():
    """Admin requests support - sends email to system admin"""
    try:
        session_token = request.headers.get('Authorization')
        if not session_token:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
        valid, username = admin_auth.verify_session(session_token)
        if not valid:
            return jsonify({'success': False, 'message': 'Invalid session'}), 401
        
        data = request.json
        subject = data.get('subject')
        message = data.get('message')
        
        if not all([subject, message]):
            return jsonify({'success': False, 'message': 'Subject and message required'}), 400
        
        # Send email to system admin
        system_admin_email = 'amitsingh6394366374@gmail.com'
        
        email_subject = f"[ADMIN SUPPORT] {subject}"
        email_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #6366f1;">Admin Support Request</h2>
            <div style="background: #f3f4f6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <p><strong>From Admin:</strong> {username}</p>
                <p><strong>Subject:</strong> {subject}</p>
                <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            <div style="background: white; padding: 20px; border-left: 4px solid #6366f1;">
                <h3>Message:</h3>
                <p style="white-space: pre-wrap;">{message}</p>
            </div>
            <hr style="margin: 30px 0;">
            <p style="color: #6b7280; font-size: 12px;">
                This is an automated message from the Face Recognition Attendance System.
            </p>
        </body>
        </html>
        """
        
        success, result = email_service.send_email(
            system_admin_email,
            email_subject,
            email_body
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Support request sent successfully to system administrator'
            }), 200
        else:
            return jsonify({'success': False, 'message': result}), 500
    except Exception as e:
        print(f"Error sending admin support request: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
