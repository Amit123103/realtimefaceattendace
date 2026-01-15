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
