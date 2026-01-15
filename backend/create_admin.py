import pickle
from werkzeug.security import generate_password_hash
from datetime import datetime
from pathlib import Path

# Create data directory if needed
data_dir = Path('../data')
data_dir.mkdir(exist_ok=True)

# Create admin credentials
admin_data = {
    'username': 'amitsingh6394366374@gmail.com',
    'password_hash': generate_password_hash('Amitkumar1@'),
    'face_encoding': None,
    'created_at': datetime.now().isoformat()
}

# Save to pickle file
with open(data_dir / 'admin_credentials.pkl', 'wb') as f:
    pickle.dump(admin_data, f)

print("✅ Admin credentials created successfully!")
print(f"Username: {admin_data['username']}")
print("Password: Amitkumar1@")
