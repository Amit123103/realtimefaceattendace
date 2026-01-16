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
        
        # Student Model Paths
        self.student_model_path = self.data_dir / 'face_model.yml'
        self.student_labels_path = self.data_dir / 'labels_map.pkl'
        
        # Admin Model Paths
        self.admin_model_path = self.data_dir / 'admin_face_model.yml'
        self.admin_labels_path = self.data_dir / 'admin_labels_map.pkl'
        
        # Face Detection
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        # Recognizers
        self.student_recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.admin_recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        self.student_label_map = {}
        self.admin_label_map = {}
        
        # Load models
        self.load_models()

    def load_models(self):
        """Load both student and admin models"""
        # Load Student Model
        if self.student_model_path.exists() and self.student_labels_path.exists():
            try:
                self.student_recognizer.read(str(self.student_model_path))
                with open(self.student_labels_path, 'rb') as f:
                    data = pickle.load(f)
                    self.student_label_map = data['map']
                print("✅ Student model loaded")
            except Exception as e:
                print(f"Error loading student model: {e}")
        
        # Load Admin Model
        if self.admin_model_path.exists() and self.admin_labels_path.exists():
            try:
                self.admin_recognizer.read(str(self.admin_model_path))
                with open(self.admin_labels_path, 'rb') as f:
                    data = pickle.load(f)
                    self.admin_label_map = data['map']
                print("✅ Admin model loaded")
            except Exception as e:
                print(f"Error loading admin model: {e}")

    def detect_face(self, image_data):
        """Detect face in image"""
        try:
            if isinstance(image_data, str):
                image = cv2.imread(image_data)
            else:
                image = image_data
            
            if image is None:
                return False, []

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )
            return len(faces) > 0, faces
        except Exception as e:
            print(f"Error detecting face: {e}")
            return False, []

    def encode_face(self, image_data):
        """Legacy: Returns face crop (not really an encoding)"""
        has_face, faces = self.detect_face(image_data)
        if has_face:
            (x, y, w, h) = faces[0]
            if isinstance(image_data, str):
                image = cv2.imread(image_data)
            else:
                image = image_data
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            return gray[y:y+h, x:x+w]
        return None

    def save_encoding(self, encoding, identifier, category='student'):
        """No-op for LBPH"""
        return True

    def train_model(self, category='student'):
        """Train model for specific category"""
        print(f"🔄 Training {category} model...")
        
        faces = []
        labels = []
        label_map = {}
        next_label = 0
        img_label_lookup = {} # id -> int
        count = 0

        if category == 'student':
            images_dir = self.data_dir / 'images' / 'students'
            model_path = self.student_model_path
            labels_path = self.student_labels_path
            recognizer = self.student_recognizer

            if not images_dir.exists():
                images_dir.mkdir(parents=True, exist_ok=True)
                return False

            for image_path in images_dir.glob('*'):
                if image_path.suffix.lower() not in ['.jpg', '.png', '.jpeg']:
                    continue
                
                try:
                    filename = image_path.stem
                    # student logic: reg_no_timestamp
                    # We take the part before the last underscore as ID, or safe fallback
                    if '_' in filename:
                        identifier = filename.rsplit('_', 1)[0]
                    else:
                        identifier = filename

                    if identifier not in img_label_lookup:
                        img_label_lookup[identifier] = next_label
                        label_map[next_label] = identifier
                        next_label += 1
                    
                    label = img_label_lookup[identifier]
                    
                    img = cv2.imread(str(image_path))
                    if img is None: continue
                    
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    detected = self.face_cascade.detectMultiScale(gray, 1.1, 5)
                    
                    for (x, y, w, h) in detected:
                        faces.append(gray[y:y+h, x:x+w])
                        labels.append(label)
                        count += 1
                        
                except Exception as e:
                    print(f"Error processing {image_path}: {e}")

        else: # Admin - Use Excel Source of Truth
            import pandas as pd
            admins_file = self.data_dir / 'admins.xlsx'
            model_path = self.admin_model_path
            labels_path = self.admin_labels_path
            recognizer = self.admin_recognizer

            if not admins_file.exists():
                print("Admins file not found")
                return False

            try:
                df = pd.read_excel(admins_file)
                # Filter admins with registered faces
                # Note: register_admin_face saves path in 'Face Encoding Path' column in our modified app.py logic
                
                for index, row in df.iterrows():
                    username = row['Username']
                    face_path_str = str(row['Face Encoding Path'])
                    
                    # Check if it looks like a file path (contains separator or extension)
                    if not face_path_str or face_path_str == 'nan' or face_path_str == 'None':
                        continue
                        
                    # Fix path separators if needed or just use relative
                    # The app saves as absolute or relative? app.py:825: admin_auth.register_admin_face(username, str(image_path))
                    # image_path was absolute or relative? It was derived from IMAGES_FOLDER (Path object)
                    
                    if os.path.exists(face_path_str):
                        image_path = Path(face_path_str)
                    else:
                        # Try relative to data folder
                        possible_path = self.data_dir / 'images' / 'admins' / Path(face_path_str).name
                        if possible_path.exists():
                            image_path = possible_path
                        else:
                            continue

                    if username not in img_label_lookup:
                        img_label_lookup[username] = next_label
                        label_map[next_label] = username
                        next_label += 1
                    
                    label = img_label_lookup[username]
                    
                    img = cv2.imread(str(image_path))
                    if img is None: continue
                    
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    detected = self.face_cascade.detectMultiScale(gray, 1.1, 5)
                    
                    for (x, y, w, h) in detected:
                        faces.append(gray[y:y+h, x:x+w])
                        labels.append(label)
                        count += 1
                        
            except Exception as e:
                print(f"Error processing admin faces: {e}")

        if len(faces) > 0:
            recognizer.train(faces, np.array(labels))
            recognizer.save(str(model_path))
            
            with open(labels_path, 'wb') as f:
                pickle.dump({'map': label_map}, f)
            
            # Update memory
            if category == 'student':
                self.student_label_map = label_map
            else:
                self.admin_label_map = label_map
                
            print(f"✅ {category.capitalize()} model trained on {count} faces")
            return True
        return False

    def recognize_face(self, image_data, category='student'):
        """Recognize face"""
        try:
            has_face, faces = self.detect_face(image_data)
            if not has_face:
                return False, None, 0.0, "No face detected"
            
            # Largest face
            faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
            (x, y, w, h) = faces[0]
            
            if isinstance(image_data, str):
                img = cv2.imread(image_data)
            else:
                img = image_data
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            face_roi = gray[y:y+h, x:x+w]
            
            if category == 'student':
                recognizer = self.student_recognizer
                label_map = self.student_label_map
            else:
                recognizer = self.admin_recognizer
                label_map = self.admin_label_map
            
            try:
                label, confidence = recognizer.predict(face_roi)
            except cv2.error:
                 # Model not initialized/trained yet
                 return False, None, 0.0, "Model not trained yet"

            # Threshold
            # Lower is better match
            threshold = 85 
            
            if confidence < threshold:
                if label in label_map:
                    identifier = label_map[label]
                    conf_score = max(0, 100 - confidence)
                    return True, identifier, conf_score, "Match found"
            
            return False, None, 0.0, "Face valid but not recognized"
            
        except Exception as e:
            print(f"Recognition error: {e}")
            return False, None, 0.0, str(e)
