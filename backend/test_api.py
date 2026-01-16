import requests
import json

API_URL = "http://localhost:8000/api"

def test_register():
    print("Testing Registration...")
    payload = {
        "registration_number": "TEST_001",
        "name": "Test Student",
        "password": "password123",
        "email": "test@example.com",
        "phone": "555-555-5555",
        "department": "CS"
    }
    
    try:
        res = requests.post(f"{API_URL}/auth/student/register", json=payload)
        print(f"Status: {res.status_code}")
        print(f"Response: {res.text}")
        
        if res.status_code == 200:
            print("✅ Registration Successful")
        elif res.status_code == 400 and "already registered" in res.text:
             print("⚠️  Already registered (Expected if run twice)")
        else:
            print("❌ Registration Failed")
            
    except Exception as e:
        print(f"❌ Error connecting to backend: {e}")

if __name__ == "__main__":
    test_register()
