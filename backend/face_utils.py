import cv2
import numpy as np
import base64
import io
from PIL import Image
from pathlib import Path

# Load Models
DATA_DIR = Path("../data")
MODELS_DIR = DATA_DIR / "models"
YUNET_PATH = MODELS_DIR / "face_detection_yunet_2023mar.onnx"
SFACE_PATH = MODELS_DIR / "face_recognition_sface_2021dec.onnx"

# Initialize detectors (Lazy load or global)
face_detector = None
face_recognizer = None

def init_models():
    global face_detector, face_recognizer
    if face_detector is None:
        try:
             # YuNet: input size can be dynamic, but init requires one. We update it per image.
            face_detector = cv2.FaceDetectorYN.create(
                str(YUNET_PATH),
                "",
                (320, 320),
                0.9, # Score threshold
                0.3, # NMS threshold
                5000 # Top K
            )
            face_recognizer = cv2.FaceRecognizerSF.create(
                str(SFACE_PATH),
                ""
            )
            print("✅ OpenCV Face Models Loaded")
        except Exception as e:
            print(f"❌ Error loading models: {e}")

# Call init
init_models()

def decode_image(image_file_or_base64):
    """
    Convert uploaded file or base64 string to numpy array (RGB)
    """
    try:
        # If it's bytes/file-like
        if hasattr(image_file_or_base64, "read"):
            image_data = image_file_or_base64.read()
            image = Image.open(io.BytesIO(image_data))
        elif isinstance(image_file_or_base64, str) and "base64" in image_file_or_base64:
            # Base64 string
            if "," in image_file_or_base64:
                image_file_or_base64 = image_file_or_base64.split(",")[1]
            image_data = base64.b64decode(image_file_or_base64)
            image = Image.open(io.BytesIO(image_data))
        else:
            return None

        # Convert to RGB (standard internal format)
        if image.mode != "RGB":
            image = image.convert("RGB")
            
        return np.array(image)
    except Exception as e:
        print(f"Error decoding image: {e}")
        return None

def get_face_embedding(image_array):
    """
    Detects EXACTLY one face and returns 128D encoding.
    Returns (encoding, error_message)
    """
    try:
        if face_detector is None:
            return None, "Models not initialized (missing ONNX files?)"

        # Convert to BGR for OpenCV
        img_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        h, w, _ = img_bgr.shape
        
        # Set input size
        face_detector.setInputSize((w, h))
        
        # Detect
        _, faces = face_detector.detect(img_bgr)
        
        if faces is None or len(faces) == 0:
            return None, "No face detected"
            
        # Filter weak faces? threshold is already 0.9 in init
        
        if len(faces) > 1:
            # Find the largest face
            # Face format: x1, y1, w, h, x_re, y_re, ... confidence
            largest_face = max(faces, key=lambda f: f[2] * f[3])
            
            # If strictly one face required:
            # return None, "Multiple faces detected. Please ensure only one person is in frame."
            
            # For robustness, we'll use the largest face but warn? 
            # User rule: "During registration, reject if no face or multiple faces."
            # So let's strict check.
            return None, f"Multiple faces detected ({len(faces)}). Please ensure only one person is in frame."
        else:
            largest_face = faces[0]

        # Align and Recognize
        # FaceRecognizerSF requires aligned face
        aligned_face = face_recognizer.alignCrop(img_bgr, largest_face)
        embedding = face_recognizer.feature(aligned_face)
        
        # embedding is (1, 128) float32
        return embedding[0].tolist(), None
        
    except Exception as e:
        return None, f"Processing error: {str(e)}"

def compare_faces(known_encoding, unknown_encoding, threshold=0.4):
    """
    Compare two face encodings.
    Using Cosine Similarity (OpenCV default for SFace).
    
    Returns (is_match, distance)
    
    WARNING: SFace match() returns SIMILARITY for COSINE mode.
    High score = Match.
    Threshold suggestion from OpenCV Zoo: 0.363
    
    To keep API consistent (distance, lower is better), we return 1 - similarity.
    """
    try:
        if face_recognizer is None:
            return False, 1.0

        known_np = np.array(known_encoding, dtype=np.float32).reshape(1, 128)
        unknown_np = np.array(unknown_encoding, dtype=np.float32).reshape(1, 128)
        
        # Match returns similarity score
        similarity = face_recognizer.match(known_np, unknown_np, cv2.FaceRecognizerSF_FR_COSINE)
        
        # Convert to "distance" (0 to 1 ideally)
        # Cosine similarity is usually -1 to 1.
        # Distance = 1 - similarity
        distance = 1.0 - similarity
        
        # Threshold Logic:
        # If threshold is 0.4 (distance), implies similarity >= 0.6.
        # SFace standard threshold is ~0.363 similarity.
        # So acceptable distance is 1 - 0.363 = 0.637.
        # Let's set default threshold to 0.6 (strict enough) passed in arg.
        
        # However, default arg is 0.4?
        # Let's verify what `threshold` means in the caller.
        # Caller uses: if dist < threshold (0.5).
        # So we need distance to be < 0.5 for match.
        # 1 - sim < 0.5 => sim > 0.5.
        # 0.5 similarity is strictly higher than 0.363, so it's a GOOD safe threshold.
        
        return distance <= threshold, distance
    except Exception as e:
        print(f"Comparison error: {e}")
        return False, 1.0

def save_image_to_disk(image_array, path):
    """Save numpy array as image"""
    try:
        # Convert RGB to BGR for OpenCV
        bgr_image = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        cv2.imwrite(str(path), bgr_image)
        return True
    except Exception as e:
        print(f"Save error: {e}")
        return False
