from flask_mail import Mail, Message
from datetime import datetime
import os

class EmailService:
    def __init__(self, app=None):
        self.mail = None
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize Flask-Mail with app"""
        # Email configuration
        app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
        app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
        app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
        app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', '')
        app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', '')
        app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@attendance.com')
        
        self.mail = Mail(app)
    
    def send_attendance_report(self, recipient_email, attendance_data, report_date=None):
        """Send daily attendance report to admin"""
        try:
            if not self.mail:
                return False, "Email service not configured"
            
            if not report_date:
                report_date = datetime.now().strftime("%B %d, %Y")
            
            # Create message
            msg = Message(
                subject=f"Attendance Report - {report_date}",
                recipients=[recipient_email]
            )
            
            # HTML body
            html_body = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .header {{ background: linear-gradient(135deg, #6366f1, #4f46e5); color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                    th {{ background-color: #6366f1; color: white; padding: 12px; text-align: left; }}
                    td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
                    tr:hover {{ background-color: #f5f5f5; }}
                    .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>📊 Attendance Report</h1>
                    <p>{report_date}</p>
                </div>
                <div class="content">
                    <h2>Summary</h2>
                    <p><strong>Total Attendance Records:</strong> {len(attendance_data)}</p>
                    
                    <h2>Attendance Details</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Registration No</th>
                                <th>Date</th>
                                <th>Time</th>
                            </tr>
                        </thead>
                        <tbody>
            """
            
            for record in attendance_data:
                html_body += f"""
                            <tr>
                                <td>{record.get('Name', 'N/A')}</td>
                                <td>{record.get('Registration No', 'N/A')}</td>
                                <td>{record.get('Date', 'N/A')}</td>
                                <td>{record.get('Time', 'N/A')}</td>
                            </tr>
                """
            
            html_body += """
                        </tbody>
                    </table>
                </div>
                <div class="footer">
                    <p>This is an automated email from Face Recognition Attendance System</p>
                    <p>Please do not reply to this email</p>
                </div>
            </body>
            </html>
            """
            
            msg.html = html_body
            
            # Send email
            self.mail.send(msg)
            return True, "Email sent successfully"
        except Exception as e:
            print(f"Error sending email: {e}")
            return False, str(e)
    
    def send_student_summary(self, student_email, student_name, attendance_count, total_days):
        """Send attendance summary to student"""
        try:
            if not self.mail:
                return False, "Email service not configured"
            
            percentage = (attendance_count / total_days * 100) if total_days > 0 else 0
            
            msg = Message(
                subject=f"Your Attendance Summary",
                recipients=[student_email]
            )
            
            html_body = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .header {{ background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; }}
                    .stats {{ background: #f0fdf4; padding: 20px; border-radius: 10px; margin: 20px 0; }}
                    .stat-item {{ margin: 10px 0; font-size: 18px; }}
                    .percentage {{ font-size: 48px; font-weight: bold; color: #10b981; text-align: center; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>👨‍🎓 Attendance Summary</h1>
                </div>
                <div class="content">
                    <h2>Hello {student_name},</h2>
                    <p>Here's your attendance summary:</p>
                    
                    <div class="stats">
                        <div class="percentage">{percentage:.1f}%</div>
                        <div class="stat-item">📅 <strong>Total Days:</strong> {total_days}</div>
                        <div class="stat-item">✅ <strong>Days Present:</strong> {attendance_count}</div>
                        <div class="stat-item">❌ <strong>Days Absent:</strong> {total_days - attendance_count}</div>
                    </div>
                    
                    <p>Keep up the good work!</p>
                </div>
                <div style="text-align: center; padding: 20px; color: #666; font-size: 12px;">
                    <p>Face Recognition Attendance System</p>
                </div>
            </body>
            </html>
            """
            
            msg.html = html_body
            self.mail.send(msg)
            return True, "Email sent successfully"
        except Exception as e:
            print(f"Error sending student summary: {e}")
            return False, str(e)
