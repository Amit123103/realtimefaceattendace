import pickle
from werkzeug.security import generate_password_hash
from pathlib import Path

# Create data directory if it doesn't exist
data_dir = Path('data')
data_dir.mkdir(exist_ok=True)

# New admin credentials
admin_data = {
    'username': 'amitsingh6394366374@gmail.com',
    'password_hash': generate_password_hash('Amitkumar1@')
}

# Save to pickle file
with open(data_dir / 'admin_credentials.pkl', 'wb') as f:
    pickle.dump(admin_data, f)

print("✅ Admin credentials updated successfully!")
print(f"Username: {admin_data['username']}")
print("Password: Amitkumar1@")
