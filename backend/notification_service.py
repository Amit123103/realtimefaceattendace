import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import os
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# --- Configuration ( Ideally from .env ) ---
# EMAIL CONFIG
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("MAIL_USERNAME", "your-email@gmail.com") 
SENDER_PASSWORD = os.getenv("MAIL_PASSWORD", "your-app-password") # NOT your login password, use App Password

# SMS CONFIG (Example: Fast2SMS for India, or Twilio)
SMS_API_KEY = os.getenv("SMS_API_KEY", "") 

def send_email_otp(to_email, otp):
    """
    Sends OTP via Gumail SMTP.
    Requires SENDER_EMAIL and SENDER_PASSWORD to be set.
    """
    if "your-email" in SENDER_EMAIL:
        print(f"⚠️  [EMAIL SKIPPED] Email credentials not set. OTP: {otp}")
        return False, "Credentials not set"

    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = "Your Attendance System Login OTP"

        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <div style="background-color: #f3f4f6; padding: 20px; border-radius: 10px; text-align: center;">
                    <h2 style="color: #4f46e5;">Verification Code</h2>
                    <p>Use the following OTP to log in to your Student Portal:</p>
                    <div style="background-color: white; font-size: 24px; font-weight: bold; letter-spacing: 5px; padding: 15px; margin: 20px auto; width: fit-content; border-radius: 5px; border: 1px solid #ddd;">
                        {otp}
                    </div>
                    <p style="color: #666; font-size: 12px;">This code is valid for 10 minutes.</p>
                </div>
            </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ [EMAIL SENT] OTP sent to {to_email}")
        return True, "Email sent"
    except Exception as e:
        print(f"❌ [EMAIL FAILED] {e}")
        return False, str(e)

def send_sms_otp(phone_number, otp):
    """
    Sends OTP via SMS API.
    Currently configured for Fast2SMS (popular in India) as an example.
    Replace with your provider logic.
    """
    if not SMS_API_KEY:
        print(f"⚠️  [SMS SKIPPED] SMS API Key not set. OTP: {otp}")
        return False, "API Key not set"
        
    # Example: Fast2SMS (Indian Provider)
    url = "https://www.fast2sms.com/dev/bulkV2"
    
    # Generic Payload
    payload = {
        "authorization": SMS_API_KEY,
        "variables_values": otp,
        "route": "otp",
        "numbers": phone_number
    }
    
    try:
        # Uncomment to actually send
        response = requests.get(url, params=payload) 
        print(f"✅ [SMS SENT] Response: {response.text}")
        return True, "SMS sent"
    except Exception as e:
        print(f"❌ [SMS FAILED] {e}")
        return False, str(e)
