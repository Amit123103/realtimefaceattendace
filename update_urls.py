import glob
import os

files = glob.glob(r'c:\Users\amita\OneDrive\Desktop\fileme\face-attendance-system\frontend\*.html')

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content.replace('const API_URL = "http://localhost:8000/api";', 'const API_URL = "/api";')
    
    if content != new_content:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {fpath}")
    else:
        print(f"Skipped {fpath}")
