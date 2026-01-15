import pandas as pd
from pathlib import Path
from datetime import datetime
import os

class ExcelHandler:
    def __init__(self, data_dir='../data'):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.students_file = self.data_dir / 'students.xlsx'
        self.attendance_file = self.data_dir / 'attendance.xlsx'
        
        # Initialize Excel files if they don't exist
        self._init_students_file()
        self._init_attendance_file()
    
    def _init_students_file(self):
        """Initialize students Excel file with headers"""
        if not self.students_file.exists():
            df = pd.DataFrame(columns=['Name', 'Registration No', 'Image Path', 'Enrollment Date'])
            df.to_excel(self.students_file, index=False, engine='openpyxl')
    
    def _init_attendance_file(self):
        """Initialize attendance Excel file with headers"""
        if not self.attendance_file.exists():
            df = pd.DataFrame(columns=['Name', 'Registration No', 'Image Path', 'Date', 'Time'])
            df.to_excel(self.attendance_file, index=False, engine='openpyxl')
    
    def add_student(self, name, registration_no, image_path):
        """Add a new student to the Excel file"""
        try:
            # Check if student already exists
            if self.student_exists(registration_no):
                return False, "Student with this registration number already exists"
            
            # Read existing data
            df = pd.read_excel(self.students_file, engine='openpyxl')
            
            # Create new row
            new_row = {
                'Name': name,
                'Registration No': registration_no,
                'Image Path': image_path,
                'Enrollment Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Append new row
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            
            # Save to Excel
            df.to_excel(self.students_file, index=False, engine='openpyxl')
            
            return True, "Student registered successfully"
        except Exception as e:
            print(f"Error adding student: {e}")
            return False, f"Error: {str(e)}"
    
    def student_exists(self, registration_no):
        """Check if a student exists in the database"""
        try:
            df = pd.read_excel(self.students_file, engine='openpyxl')
            return registration_no in df['Registration No'].values
        except Exception as e:
            print(f"Error checking student existence: {e}")
            return False
    
    def get_student_by_regno(self, registration_no):
        """Get student details by registration number"""
        try:
            df = pd.read_excel(self.students_file, engine='openpyxl')
            student = df[df['Registration No'] == registration_no]
            
            if not student.empty:
                return student.iloc[0].to_dict()
            return None
        except Exception as e:
            print(f"Error getting student: {e}")
            return None
    
    def add_attendance(self, name, registration_no, image_path):
        """Record attendance for a student"""
        try:
            # Read existing data
            df = pd.read_excel(self.attendance_file, engine='openpyxl')
            
            now = datetime.now()
            today = now.strftime('%Y-%m-%d')
            
            # Check if student already marked attendance today
            if not df.empty:
                today_attendance = df[
                    (df['Registration No'] == registration_no) & 
                    (df['Date'] == today)
                ]
                if not today_attendance.empty:
                    return False, "Attendance already marked for today"
            
            # Create new row
            new_row = {
                'Name': name,
                'Registration No': registration_no,
                'Image Path': image_path,
                'Date': today,
                'Time': now.strftime('%H:%M:%S')
            }
            
            # Append new row
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            
            # Save to Excel
            df.to_excel(self.attendance_file, index=False, engine='openpyxl')
            
            return True, "Attendance marked successfully"
        except Exception as e:
            print(f"Error adding attendance: {e}")
            return False, f"Error: {str(e)}"
    
    def get_all_students(self):
        """Get all registered students"""
        try:
            df = pd.read_excel(self.students_file, engine='openpyxl')
            return df.to_dict('records')
        except Exception as e:
            print(f"Error getting students: {e}")
            return []
    
    def get_attendance_records(self, start_date=None, end_date=None, registration_no=None):
        """Get attendance records with optional filters"""
        try:
            df = pd.read_excel(self.attendance_file, engine='openpyxl')
            
            if df.empty:
                return []
            
            # Apply filters
            if registration_no:
                df = df[df['Registration No'] == registration_no]
            
            if start_date:
                df = df[pd.to_datetime(df['Date']) >= pd.to_datetime(start_date)]
            
            if end_date:
                df = df[pd.to_datetime(df['Date']) <= pd.to_datetime(end_date)]
            
            return df.to_dict('records')
        except Exception as e:
            print(f"Error getting attendance records: {e}")
            return []
    
    def export_students_to_excel(self, output_path):
        """Export students data to a new Excel file"""
        try:
            df = pd.read_excel(self.students_file, engine='openpyxl')
            df.to_excel(output_path, index=False, engine='openpyxl')
            return True, "Students data exported successfully"
        except Exception as e:
            print(f"Error exporting students: {e}")
            return False, f"Error: {str(e)}"
    
    def export_attendance_to_excel(self, output_path, start_date=None, end_date=None):
        """Export attendance records to a new Excel file"""
        try:
            records = self.get_attendance_records(start_date, end_date)
            df = pd.DataFrame(records)
            df.to_excel(output_path, index=False, engine='openpyxl')
            return True, "Attendance data exported successfully"
        except Exception as e:
            print(f"Error exporting attendance: {e}")
            return False, f"Error: {str(e)}"
    
    def bulk_import_students(self, csv_data):
        """Import multiple students from CSV data"""
        try:
            # Parse CSV data
            import io
            df_new = pd.read_csv(io.StringIO(csv_data))
            
            # Validate required columns
            required_cols = ['name', 'registration_no', 'image_path']
            if not all(col in df_new.columns for col in required_cols):
                return False, f"CSV must contain columns: {', '.join(required_cols)}"
            
            # Read existing students
            df_existing = pd.read_excel(self.students_file, engine='openpyxl')
            
            success_count = 0
            errors = []
            
            for idx, row in df_new.iterrows():
                reg_no = row['registration_no']
                
                # Check if student already exists
                if reg_no in df_existing['Registration No'].values:
                    errors.append(f"Row {idx+1}: Student {reg_no} already exists")
                    continue
                
                # Add student
                new_row = {
                    'Name': row['name'],
                    'Registration No': reg_no,
                    'Image Path': row['image_path'],
                    'Enrollment Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                df_existing = pd.concat([df_existing, pd.DataFrame([new_row])], ignore_index=True)
                success_count += 1
            
            # Save updated data
            df_existing.to_excel(self.students_file, index=False, engine='openpyxl')
            
            message = f"Imported {success_count} students successfully"
            if errors:
                message += f". {len(errors)} errors: " + "; ".join(errors[:3])
            
            return True, message
        except Exception as e:
            print(f"Error in bulk import: {e}")
            return False, f"Error: {str(e)}"
