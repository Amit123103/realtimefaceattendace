import pandas as pd
import io

def process_attendance_excel(file_content):
    """
    Parse Excel file and return list of registration numbers to mark.
    Expected columns: 'registration_number' (case insensitive)
    """
    try:
        # Try reading as Excel
        try:
            df = pd.read_excel(io.BytesIO(file_content))
        except:
            # Try CSV if Excel fails
            df = pd.read_csv(io.BytesIO(file_content))
            
        # Normalize column names
        df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]
        
        target_col = None
        possible_cols = ['registration_number', 'reg_no', 'registration_no', 'student_id']
        
        for col in possible_cols:
            if col in df.columns:
                target_col = col
                break
                
        if not target_col:
            return None, "Column 'registration_number' not found in file"
            
        # Extract unique registration numbers
        reg_numbers = df[target_col].dropna().astype(str).unique().tolist()
        return reg_numbers, None
        
    except Exception as e:
        return None, f"Error processing file: {str(e)}"

def generate_report_excel(data):
    """
    Generate Excel bytes from list of dictionaries
    """
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Report')
    output.seek(0)
    return output
