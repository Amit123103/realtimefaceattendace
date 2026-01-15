# NEW API ENDPOINTS - Add these to app.py before the "if __name__ == '__main__':" line

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
