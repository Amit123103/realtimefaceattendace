from multi_admin import MultiAdminHandler
from werkzeug.security import generate_password_hash
import pandas as pd
from pathlib import Path
import os

def reset_admin():
    print("🔄 Resetting Admin Credentials...")
    
    # Path to admins file
    admins_file = Path('../data/admins.xlsx')
    
    # Ensure data directory exists
    if not admins_file.parent.exists():
        admins_file.parent.mkdir(parents=True)
    
    # Delete existing file if exists to start fresh
    if admins_file.exists():
        try:
            os.remove(admins_file)
            print("Deleted existing admins.xlsx")
        except Exception as e:
            print(f"Error removing file: {e}")
    
    # Create new DataFrame
    df = pd.DataFrame(columns=[
        'Username', 'Password Hash', 'Role', 'Email', 
        'Face Encoding Path', 'Created At', 'Status'
    ])
    
    # Default admin
    default_admin = {
        'Username': 'admin',
        'Password Hash': generate_password_hash('admin123'),
        'Role': 'super_admin',
        'Email': 'admin@attendance.com',
        'Face Encoding Path': None,
        'Created At': pd.Timestamp.now(),
        'Status': 'active'
    }
    
    df = pd.concat([df, pd.DataFrame([default_admin])], ignore_index=True)
    
    try:
        df.to_excel(admins_file, index=False)
        print("✅ SUCCESS: Admin reset to 'admin' / 'admin123'")
        print(f"📂 Verified file at: {admins_file.resolve()}")
    except Exception as e:
        print(f"❌ FAILED to write excel: {e}")

if __name__ == "__main__":
    reset_admin()
