from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import pickle
from pathlib import Path
from datetime import datetime, timedelta

class AdminAuth:
    def __init__(self, multi_admin_handler):
        self.multi_admin = multi_admin_handler
        self.sessions = {}
    
    def verify_password(self, username, password):
        """Verify admin password using MultiAdminHandler"""
        success, result = self.multi_admin.verify_admin(username, password)
        return success
    
    def verify_face(self, face_encoding):
        """Verify admin face encoding using MultiAdminHandler"""
        success, result = self.multi_admin.verify_face_login(face_encoding)
        if success:
            return True, result # Return True, username
        return False, None
    
    def register_admin_face(self, username, face_encoding):
        """Register or update admin face encoding"""
        success, message = self.multi_admin.update_admin_face(username, face_encoding)
        return success
    
    def has_face_registered(self, username=None):
        """Check if admin has face registered"""
        if not username:
             return False # Need username to check specific admin
             
        success, admin_data = self.multi_admin.get_admin(username)
        if success and admin_data:
             return admin_data.get('Face Encoding Path') is not None and str(admin_data.get('Face Encoding Path')) != 'nan'
        return False
    
    def create_session(self, username):
        """Create a new session for admin"""
        try:
            session_token = secrets.token_urlsafe(32)
            
            self.sessions[session_token] = {
                'username': username,
                'created_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(hours=24)
            }
            
            return session_token
        except Exception as e:
            print(f"Error creating session: {e}")
            return None
    
    def verify_session(self, session_token):
        """Verify if session token is valid"""
        try:
            if session_token in self.sessions:
                session = self.sessions[session_token]
                
                # Check if session has expired
                if datetime.now() < session['expires_at']:
                    return True, session['username']
                else:
                    # Remove expired session
                    del self.sessions[session_token]
                    return False, None
            
            return False, None
        except Exception as e:
            print(f"Error verifying session: {e}")
            return False, None
    
    def logout(self, session_token):
        """Logout and invalidate session"""
        try:
            if session_token in self.sessions:
                del self.sessions[session_token]
                return True
            return False
        except Exception as e:
            print(f"Error logging out: {e}")
            return False
    
    def update_password(self, username, old_password, new_password):
        """Update admin password"""
        # TODO: Implement password update in MultiAdminHandler
        return False, "Not implemented in multi-admin mode yet"
