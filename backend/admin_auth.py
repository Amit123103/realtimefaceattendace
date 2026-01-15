from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import pickle
from pathlib import Path
from datetime import datetime, timedelta

class AdminAuth:
    def __init__(self, data_dir='../data'):
        self.data_dir = Path(data_dir)
        self.admin_file = self.data_dir / 'admin_credentials.pkl'
        self.sessions = {}
        
        # Initialize with default admin if file doesn't exist
        self._init_admin()
    
    def _init_admin(self):
        """Initialize default admin account"""
        if not self.admin_file.exists():
            default_admin = {
                'username': 'amitsingh6394366374@gmail.com',
                'password_hash': generate_password_hash('Amitkumar1@'),
                'face_encoding': None,
                'created_at': datetime.now().isoformat()
            }
            
            with open(self.admin_file, 'wb') as f:
                pickle.dump(default_admin, f)
    
    def _load_admin(self):
        """Load admin credentials from file"""
        try:
            with open(self.admin_file, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Error loading admin credentials: {e}")
            return None
    
    def _save_admin(self, admin_data):
        """Save admin credentials to file"""
        try:
            with open(self.admin_file, 'wb') as f:
                pickle.dump(admin_data, f)
            return True
        except Exception as e:
            print(f"Error saving admin credentials: {e}")
            return False
    
    def verify_password(self, username, password):
        """Verify admin password"""
        try:
            admin = self._load_admin()
            print(f"DEBUG: Attempting login for user: {username}")
            
            if admin:
                print(f"DEBUG: Found admin user: {admin.get('username')}")
                if admin['username'] == username:
                    is_valid = check_password_hash(admin['password_hash'], password)
                    print(f"DEBUG: Password valid: {is_valid}")
                    return is_valid
                else:
                    print(f"DEBUG: Username mismatch. Expected {admin['username']}, got {username}")
            else:
                print("DEBUG: No admin data loaded")
            
            return False
        except Exception as e:
            print(f"Error verifying password: {e}")
            return False
    
    def verify_face(self, face_encoding):
        """Verify admin face encoding"""
        try:
            admin = self._load_admin()
            
            if admin and admin['face_encoding'] is not None:
                import face_recognition
                
                # Compare face encodings
                matches = face_recognition.compare_faces(
                    [admin['face_encoding']], 
                    face_encoding,
                    tolerance=0.6
                )
                
                return matches[0] if matches else False
            
            return False
        except Exception as e:
            print(f"Error verifying face: {e}")
            return False
    
    def register_admin_face(self, face_encoding):
        """Register or update admin face encoding"""
        try:
            admin = self._load_admin()
            
            if admin:
                admin['face_encoding'] = face_encoding
                admin['face_updated_at'] = datetime.now().isoformat()
                return self._save_admin(admin)
            
            return False
        except Exception as e:
            print(f"Error registering admin face: {e}")
            return False
    
    def has_face_registered(self):
        """Check if admin has face registered"""
        try:
            admin = self._load_admin()
            return admin and admin['face_encoding'] is not None
        except Exception as e:
            print(f"Error checking face registration: {e}")
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
        try:
            if not self.verify_password(username, old_password):
                return False, "Current password is incorrect"
            
            admin = self._load_admin()
            admin['password_hash'] = generate_password_hash(new_password)
            admin['password_updated_at'] = datetime.now().isoformat()
            
            if self._save_admin(admin):
                return True, "Password updated successfully"
            else:
                return False, "Error saving new password"
        except Exception as e:
            print(f"Error updating password: {e}")
            return False, f"Error: {str(e)}"
