import urllib.request
import os
from pathlib import Path

# Paths
DATA_DIR = Path("../data")
MODELS_DIR = DATA_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# URLs for Yunet (Detection) and SFace (Recognition)
# Using 'main' branch
YUNET_URL = "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
SFACE_URL = "https://github.com/opencv/opencv_zoo/raw/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx"

def download_file(url, text_name):
    filename = url.split("/")[-1]
    filepath = MODELS_DIR / filename
    
    if filepath.exists():
        # Check size to ensure allow partial downloads retry
        if filepath.stat().st_size < 1000:
             print(f"⚠️ {text_name} seems too small, re-downloading...")
        else:
            print(f"✅ {text_name} already exists.")
            return str(filepath)
        
    print(f"⬇️ Downloading {text_name}...")
    try:
        urllib.request.urlretrieve(url, filepath)
        print(f"✅ Downloaded {text_name}")
        return str(filepath)
    except Exception as e:
        print(f"❌ Failed to download {text_name}: {e}")
        return None

if __name__ == "__main__":
    download_file(YUNET_URL, "YuNet (Face Detection)")
    download_file(SFACE_URL, "SFace (Face Recognition)")
