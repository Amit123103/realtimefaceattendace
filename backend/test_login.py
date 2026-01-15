import requests
import json

url = 'http://localhost:5000/api/admin/login'
headers = {'Content-Type': 'application/json'}
data = {
    'type': 'password',
    'username': 'amitsingh6394366374@gmail.com',
    'password': 'Amitkumar1@'
}

try:
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
