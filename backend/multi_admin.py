import pandas as pd
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

class MultiAdminHandler:
    def __init__(self, admins_file='../data/admins.xlsx'):
        self.admins_file = Path(admins_file)
        self._init_admins_file()
    
    def _init_admins_file(self):
        """Initialize admins Excel file with default super admin"""
        if not self.admins_file.exists():
            df = pd.DataFrame(columns=[
                'Username', 'Password Hash', 'Role', 'Email', 
                'Face Encoding Path', 'Created At', 'Status'
            ])
            
            # Add default super admin
            df = pd.concat([df, pd.DataFrame([{
                'Username': 'admin',
                'Password Hash': generate_password_hash('admin123'),
                'Role': 'super_admin',
                'Email': 'admin@attendance.com',
                'Face Encoding Path': None,
                'Created At': pd.Timestamp.now(),
                'Status': 'active'
            }])], ignore_index=True)
            
            df.to_excel(self.admins_file, index=False)
    
    def add_admin(self, username, password, role='admin', email=''):
        """Add new admin account"""
        try:
            df = pd.read_excel(self.admins_file)
            
            # Check if username exists
            if username in df['Username'].values:
                return False, "Username already exists"
            
            # Validate role
            valid_roles = ['super_admin', 'admin', 'viewer']
            if role not in valid_roles:
                return False, f"Invalid role. Must be one of: {', '.join(valid_roles)}"
            
            # Add new admin
            new_admin = {
                'Username': username,
                'Password Hash': generate_password_hash(password),
                'Role': role,
                'Email': email,
                'Face Encoding Path': None,
                'Created At': pd.Timestamp.now(),
                'Status': 'active'
            }
            
            df = pd.concat([df, pd.DataFrame([new_admin])], ignore_index=True)
            df.to_excel(self.admins_file, index=False)
            
            return True, "Admin added successfully"
        except Exception as e:
            print(f"Error adding admin: {e}")
            return False, str(e)
    
    def get_all_admins(self):
        """Get all admin accounts (excluding passwords)"""
        try:
            df = pd.read_excel(self.admins_file)
            # Remove password hash from response
            admins = df.drop(columns=['Password Hash']).to_dict('records')
            return True, admins
        except Exception as e:
            print(f"Error getting admins: {e}")
            return False, []
    
    def get_admin(self, username):
        """Get specific admin details"""
        try:
            df = pd.read_excel(self.admins_file)
            admin = df[df['Username'] == username]
            
            if admin.empty:
                return False, None
            
            admin_data = admin.iloc[0].to_dict()
            # Remove password hash
            admin_data.pop('Password Hash', None)
            return True, admin_data
        except Exception as e:
            print(f"Error getting admin: {e}")
            return False, None
    
    def verify_admin(self, username, password):
        """Verify admin credentials"""
        try:
            df = pd.read_excel(self.admins_file)
            admin = df[df['Username'] == username]
            
            if admin.empty:
                return False, "Admin not found"
            
            admin_data = admin.iloc[0]
            
            # Check if account is active
            if admin_data['Status'] != 'active':
                return False, "Account is inactive"
            
            # Verify password
            if check_password_hash(admin_data['Password Hash'], password):
                return True, admin_data['Role']
            else:
                return False, "Invalid password"
        except Exception as e:
            print(f"Error verifying admin: {e}")
            return False, str(e)
    
    def update_admin_role(self, username, new_role):
        """Update admin role (super_admin only)"""
        try:
            df = pd.read_excel(self.admins_file)
            
            if username not in df['Username'].values:
                return False, "Admin not found"
            
            valid_roles = ['super_admin', 'admin', 'viewer']
            if new_role not in valid_roles:
                return False, f"Invalid role"
            
            df.loc[df['Username'] == username, 'Role'] = new_role
            df.to_excel(self.admins_file, index=False)
            
            return True, "Role updated successfully"
        except Exception as e:
            print(f"Error updating role: {e}")
            return False, str(e)
    
    def deactivate_admin(self, username):
        """Deactivate admin account"""
        try:
            df = pd.read_excel(self.admins_file)
            
            if username not in df['Username'].values:
                return False, "Admin not found"
            
            # Don't allow deactivating the default super admin
            if username == 'admin':
                return False, "Cannot deactivate default super admin"
            
            df.loc[df['Username'] == username, 'Status'] = 'inactive'
            df.to_excel(self.admins_file, index=False)
            
            return True, "Admin deactivated successfully"
        except Exception as e:
            print(f"Error deactivating admin: {e}")
            return False, str(e)
    
    def check_permission(self, username, required_permission):
        """Check if admin has required permission"""
        try:
            df = pd.read_excel(self.admins_file)
            admin = df[df['Username'] == username]
            
            if admin.empty:
                return False
            
            role = admin.iloc[0]['Role']
            
            # Permission hierarchy
            permissions = {
                'super_admin': ['view', 'edit', 'delete', 'manage_admins'],
                'admin': ['view', 'edit', 'delete'],
                'viewer': ['view']
            }
            
            return required_permission in permissions.get(role, [])
        except Exception as e:
            print(f"Error checking permission: {e}")
            return False
