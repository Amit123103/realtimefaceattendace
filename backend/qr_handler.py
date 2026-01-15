import qrcode
import io
import json
from pathlib import Path
from datetime import datetime

class QRCodeHandler:
    def __init__(self, qr_codes_dir='../data/qr_codes'):
        self.qr_codes_dir = Path(qr_codes_dir)
        self.qr_codes_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_student_qr(self, registration_no, name):
        """Generate QR code for a student"""
        try:
            # Create QR data
            qr_data = {
                'type': 'student_attendance',
                'registration_no': registration_no,
                'name': name,
                'generated_at': datetime.now().isoformat()
            }
            
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(json.dumps(qr_data))
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Save to file
            filename = f"qr_{registration_no}.png"
            filepath = self.qr_codes_dir / filename
            img.save(filepath)
            
            return True, str(filepath), qr_data
        except Exception as e:
            print(f"Error generating QR code: {e}")
            return False, None, None
    
    def generate_qr_bytes(self, registration_no, name):
        """Generate QR code and return as bytes for download"""
        try:
            qr_data = {
                'type': 'student_attendance',
                'registration_no': registration_no,
                'name': name,
                'generated_at': datetime.now().isoformat()
            }
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(json.dumps(qr_data))
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to bytes
            img_io = io.BytesIO()
            img.save(img_io, 'PNG')
            img_io.seek(0)
            
            return img_io
        except Exception as e:
            print(f"Error generating QR bytes: {e}")
            return None
    
    def verify_qr_data(self, qr_data_str):
        """Verify and parse QR code data"""
        try:
            qr_data = json.loads(qr_data_str)
            
            if qr_data.get('type') != 'student_attendance':
                return False, "Invalid QR code type"
            
            registration_no = qr_data.get('registration_no')
            if not registration_no:
                return False, "Missing registration number"
            
            return True, registration_no
        except Exception as e:
            print(f"Error verifying QR data: {e}")
            return False, str(e)
