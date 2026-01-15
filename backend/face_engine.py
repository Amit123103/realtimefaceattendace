import cv2
import numpy as np
import pickle
import os
from pathlib import Path
from skimage.metrics import structural_similarity as ssim

class FaceEngine:
    def __init__(self, encodings_dir='../data/encodings'):
        self.encodings_dir = Path(encodings_dir)
        self.encodings_dir.mkdir(parents=True, exist_ok=True)
        self.known_encodings = {}
        
        # Load Haar Cascade for face detection
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        self.load_all_encodings()
    
    def detect_face(self, image_data):
        """
        Detect if a face exists in the image
        Returns: (bool, face_locations)
        """
        try:
            # Convert to grayscale for detection
            if isinstance(image_data, str):
                image = cv2.imread(image_data)
            else:
                image = image_data
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            return len(faces) > 0, faces
        except Exception as e:
            print(f"Error detecting face: {e}")
            return False, []
    
    def encode_face(self, image_data):
        """
        Generate face encoding from image (using cropped face region)
        Returns: face_encoding (cropped face image) or None
        """
        try:
            if isinstance(image_data, str):
                image = cv2.imread(image_data)
            else:
                image = image_data
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            if len(faces) > 0:
                # Get the first (largest) face
                (x, y, w, h) = faces[0]
                
                # Crop and resize face to standard size
                face_roi = gray[y:y+h, x:x+w]
                face_resized = cv2.resize(face_roi, (100, 100))
                
                return face_resized
            else:
                return None
        except Exception as e:
            print(f"Error encoding face: {e}")
            return None
    
    def save_encoding(self, encoding, identifier, category='student'):
        """
        Save face encoding to file
        """
        try:
            filename = f"{category}_{identifier}.pkl"
            filepath = self.encodings_dir / filename
            
            with open(filepath, 'wb') as f:
                pickle.dump(encoding, f)
            
            # Update in-memory cache
            self.known_encodings[identifier] = {
                'encoding': encoding,
                'category': category
            }
            
            return True
        except Exception as e:
            print(f"Error saving encoding: {e}")
            return False
    
    def load_encoding(self, identifier):
        """Load a specific encoding from file"""
        try:
            # Try student first
            filepath = self.encodings_dir / f"student_{identifier}.pkl"
            if not filepath.exists():
                # Try admin
                filepath = self.encodings_dir / f"admin_{identifier}.pkl"
            
            if filepath.exists():
                with open(filepath, 'rb') as f:
                    encoding = pickle.load(f)
                return encoding
            return None
        except Exception as e:
            print(f"Error loading encoding: {e}")
            return None
    
    def load_all_encodings(self):
        """Load all face encodings from directory"""
        try:
            self.known_encodings = {}
            
            for filepath in self.encodings_dir.glob('*.pkl'):
                try:
                    with open(filepath, 'rb') as f:
                        encoding = pickle.load(f)
                    
                    # Parse filename: category_identifier.pkl
                    filename = filepath.stem
                    parts = filename.split('_', 1)
                    
                    if len(parts) == 2:
                        category, identifier = parts
                        self.known_encodings[identifier] = {
                            'encoding': encoding,
                            'category': category
                        }
                except Exception as e:
                    print(f"Error loading {filepath}: {e}")
            
            print(f"Loaded {len(self.known_encodings)} face encodings")
            return True
        except Exception as e:
            print(f"Error loading all encodings: {e}")
            return False
    
    def compare_faces(self, face_encoding, category='student', tolerance=0.7):
        """
        Compare face encoding against known encodings using SSIM
        Returns: (match_found, identifier, confidence)
        """
        try:
            if face_encoding is None:
                return False, None, 0.0
            
            best_match = None
            best_similarity = 0.0
            
            for identifier, data in self.known_encodings.items():
                if data['category'] != category:
                    continue
                
                known_encoding = data['encoding']
                
                # Calculate similarity using SSIM
                similarity = ssim(known_encoding, face_encoding)
                
                if similarity > tolerance and similarity > best_similarity:
                    best_similarity = similarity
                    best_match = identifier
            
            if best_match:
                confidence = best_similarity * 100
                return True, best_match, confidence
            else:
                return False, None, 0.0
        except Exception as e:
            print(f"Error comparing faces: {e}")
            return False, None, 0.0
    
    def recognize_face(self, image_data, category='student'):
        """
        Complete face recognition pipeline
        Returns: (success, identifier, confidence, message)
        """
        try:
            # Detect face
            has_face, face_locations = self.detect_face(image_data)
            if not has_face:
                return False, None, 0.0, "No face detected in image"
            
            # Encode face
            encoding = self.encode_face(image_data)
            if encoding is None:
                return False, None, 0.0, "Could not encode face"
            
            # Compare with known faces
            match_found, identifier, confidence = self.compare_faces(encoding, category)
            
            if match_found:
                return True, identifier, confidence, f"Face recognized with {confidence:.1f}% confidence"
            else:
                return False, None, 0.0, "Face not recognized"
        except Exception as e:
            print(f"Error in face recognition: {e}")
            return False, None, 0.0, f"Error: {str(e)}"
