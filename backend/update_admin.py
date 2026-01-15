"""
Script to update admin credentials
"""
import json
import pandas as pd
from pathlib import Path
from werkzeug.security import generate_password_hash
from datetime import datetime

# New credentials
NEW_USERNAME = "amitsingh6394366374@gmail.com"
NEW_PASSWORD = "Amit1@"
NEW_EMAIL = "amitsingh6394366374@gmail.com"

# Generate password hash
password_hash = generate_password_hash(NEW_PASSWORD)

print("=" * 60)
print("Updating Admin Credentials")
print("=" * 60)

# 1. Update admin_credentials.json
credentials_file = Path('../data/admin_credentials.json')
if credentials_file.exists():
    with open(credentials_file, 'r') as f:
        credentials = json.load(f)
    
    credentials['username'] = NEW_USERNAME
    credentials['password_hash'] = password_hash
    
    with open(credentials_file, 'w') as f:
        json.dump(credentials, f, indent=4)
    
    print(f"✓ Updated {credentials_file}")
else:
    # Create new credentials file
    credentials = {
        'username': NEW_USERNAME,
        'password_hash': password_hash,
        'face_encoding_path': None
    }
    credentials_file.parent.mkdir(parents=True, exist_ok=True)
    with open(credentials_file, 'w') as f:
        json.dump(credentials, f, indent=4)
    
    print(f"✓ Created {credentials_file}")

# 2. Update admins.xlsx
admins_file = Path('../data/admins.xlsx')
if admins_file.exists():
    df = pd.read_excel(admins_file)
    
    # Update the default admin row
    admin_row = df[df['Username'] == 'admin']
    if not admin_row.empty:
        df.loc[df['Username'] == 'admin', 'Username'] = NEW_USERNAME
        df.loc[df['Username'] == NEW_USERNAME, 'Password Hash'] = password_hash
        df.loc[df['Username'] == NEW_USERNAME, 'Email'] = NEW_EMAIL
    else:
        # If admin doesn't exist, add new row
        new_admin = pd.DataFrame([{
            'Username': NEW_USERNAME,
            'Password Hash': password_hash,
            'Role': 'super_admin',
            'Email': NEW_EMAIL,
            'Face Encoding Path': None,
            'Created At': datetime.now(),
            'Status': 'active'
        }])
        df = pd.concat([df, new_admin], ignore_index=True)
    
    df.to_excel(admins_file, index=False)
    print(f"✓ Updated {admins_file}")
else:
    # Create new admins.xlsx
    df = pd.DataFrame([{
        'Username': NEW_USERNAME,
        'Password Hash': password_hash,
        'Role': 'super_admin',
        'Email': NEW_EMAIL,
        'Face Encoding Path': None,
        'Created At': datetime.now(),
        'Status': 'active'
    }])
    admins_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(admins_file, index=False)
    print(f"✓ Created {admins_file}")

print("\n" + "=" * 60)
print("Admin Credentials Updated Successfully!")
print("=" * 60)
print(f"\nNew Login Credentials:")
print(f"  Username: {NEW_USERNAME}")
print(f"  Password: {NEW_PASSWORD}")
print(f"  Role: super_admin")
print("\n" + "=" * 60)
