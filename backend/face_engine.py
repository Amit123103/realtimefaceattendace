import cv2
import numpy as np
import pickle
import os
from pathlib import Path

class FaceEngine:
    def __init__(self, data_dir='../data'):
        self.data_dir = Path(data_dir)
        self.encodings_dir = self.data_dir / 'encodings'
        self.encodings_dir.mkdir(parents=True, exist_ok=True)
        
        # Paths
        self.model_path = self.data_dir / 'face_model.yml'
        self.labels_path = self.data_dir / 'labels_map.pkl'
        
        # Face Detection
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        # Face Recognition (LBPH)
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.label_map = {}  # int -> reg_no
        self.next_label = 0
        
        # Load existing model if available
        self.load_model()

    def load_model(self):
        """Load trained model and label mapping"""
        if self.model_path.exists() and self.labels_path.exists():
            try:
                self.recognizer.read(str(self.model_path))
                with open(self.labels_path, 'rb') as f:
                    data = pickle.load(f)
                    self.label_map = data['map']
                    self.next_label = data['next_label']
                print("✅ Face recognition model loaded successfully")
            except Exception as e:
                print(f"Error loading model: {e}")
                print("Re-training model...")
                self.train_model()
        else:
            print("ℹ️ No existing model found. Training new model...")
            self.train_model()

    def train_model(self):
        """Train model on all student images"""
        print("🔄 Starting model training...")
        images_dir = self.data_dir / 'images' / 'students'
        if not images_dir.exists():
            print("⚠️ No images directory found")
            return False

        faces = []
        labels = []
        self.label_map = {}
        self.next_label = 0
        
        # Helper to map reg_no to int label
        reg_to_label = {}

        count = 0
        for image_path in images_dir.glob('*'):
            if image_path.suffix.lower() not in ['.jpg', '.png', '.jpeg']:
                continue
                
            try:
                # Filename format: regno_timestamp.jpg (e.g. 12345_20240101.jpg)
                # Or just regno.jpg
                filename = image_path.stem
                if '_' in filename:
                    reg_no = filename.split('_')[0]
                else:
                    reg_no = filename
                
                # Assign label
                if reg_no not in reg_to_label:
                    reg_to_label[reg_no] = self.next_label
                    self.label_map[self.next_label] = reg_no
                    self.next_label += 1
                
                label = reg_to_label[reg_no]
                
                # Detect face in image for training
                img = cv2.imread(str(image_path))
                if img is None:
                    continue
                    
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                
                detected_faces = self.face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30)
                )
                
                for (x, y, w, h) in detected_faces:
                    faces.append(gray[y:y+h, x:x+w])
                    labels.append(label)
                    count += 1
                    
            except Exception as e:
                print(f"Error processing {image_path}: {e}")

        if len(faces) > 0:
            self.recognizer.train(faces, np.array(labels))
            self.recognizer.save(str(self.model_path))
            
            with open(self.labels_path, 'wb') as f:
                pickle.dump({
                    'map': self.label_map,
                    'next_label': self.next_label
                }, f)
                
            print(f"✅ Model trained on {count} faces for {len(self.label_map)} students")
            return True
        else:
            print("⚠️ No valid face data found for training")
            return False

    def detect_face(self, image_data):
        """
        Detect if a face exists in the image
        Returns: (bool, face_locations)
        """
        try:
            if isinstance(image_data, str):
                image = cv2.imread(image_data)
            else:
                image = image_data
            
            if image is None:
                return False, []

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
        Included for compatibility. Returns crop of face.
        """
        has_face, faces = self.detect_face(image_data)
        if has_face:
            # Just return the first face crop
            (x, y, w, h) = faces[0]
            if isinstance(image_data, str):
                image = cv2.imread(image_data)
            else:
                image = image_data
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            return gray[y:y+h, x:x+w]
        return None

    def save_encoding(self, encoding, identifier, category='student'):
        """
        Legacy compatibility. Triggers training if student.
        """
        # We rely on save_image being called by app.py, then we train.
        # But this function is usually called BEFORE save_image in app.py.
        # So we can't train here yet if the image isn't saved.
        # We will add an explicit train call in app.py.
        return True

    def recognize_face(self, image_data, category='student'):
        """
        Recognize face using LBPH model
        """
        try:
            has_face, faces = self.detect_face(image_data)
            if not has_face:
                return False, None, 0.0, "No face detected in image"
            
            # Use the largest face
            # Sort by area (w * h)
            faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
            (x, y, w, h) = faces[0]
            
            if isinstance(image_data, str):
                img = cv2.imread(image_data)
            else:
                img = image_data
                
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            face_roi = gray[y:y+h, x:x+w]
            
            # Predict
            label, confidence = self.recognizer.predict(face_roi)
            
            print(f"🔍 Prediction: Label={label}, Distance={confidence}")
            
            # LBPH Confidence is "Distance": Lower is better.
            # < 50 is very good
            # < 80 is acceptable
            # > 80 is unknown
            threshold = 75 # Adjust based on lighting conditions
            
            if confidence < threshold:
                if label in self.label_map:
                    reg_no = self.label_map[label]
                    # Convert distance to a readable 0-100% confidence score
                    # 0 distance -> 100%
                    # 100 distance -> 0%
                    display_conf = max(0, 100 - confidence)
                    return True, reg_no, display_conf, f"Face recognized (Match: {display_conf:.1f}%)"
            
            return False, None, 0.0, "Face valid, but not recognized in database. Please register."
            
        except Exception as e:
            print(f"Error in face recognition: {e}")
            return False, None, 0.0, f"Error: {str(e)}"
