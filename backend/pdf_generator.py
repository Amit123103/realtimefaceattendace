from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
from pathlib import Path
import io

class PDFReportGenerator:
    def __init__(self, reports_dir='../data/reports'):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#6366f1'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=12,
            spaceBefore=12
        ))
    
    def generate_attendance_report(self, attendance_data, start_date=None, end_date=None):
        """Generate comprehensive attendance report"""
        try:
            # Create filename
            date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"attendance_report_{date_str}.pdf"
            filepath = self.reports_dir / filename
            
            # Create PDF
            doc = SimpleDocTemplate(str(filepath), pagesize=A4)
            elements = []
            
            # Title
            title = Paragraph("Attendance Report", self.styles['CustomTitle'])
            elements.append(title)
            elements.append(Spacer(1, 0.2*inch))
            
            # Report info
            report_info = f"""
            <b>Generated:</b> {datetime.now().strftime("%B %d, %Y at %I:%M %p")}<br/>
            <b>Total Records:</b> {len(attendance_data)}<br/>
            """
            if start_date:
                report_info += f"<b>From:</b> {start_date}<br/>"
            if end_date:
                report_info += f"<b>To:</b> {end_date}<br/>"
            
            info_para = Paragraph(report_info, self.styles['Normal'])
            elements.append(info_para)
            elements.append(Spacer(1, 0.3*inch))
            
            # Attendance table
            if attendance_data:
                heading = Paragraph("Attendance Records", self.styles['CustomHeading'])
                elements.append(heading)
                
                # Table data
                table_data = [['Name', 'Reg. No', 'Date', 'Time']]
                for record in attendance_data:
                    table_data.append([
                        record.get('Name', 'N/A'),
                        record.get('Registration No', 'N/A'),
                        record.get('Date', 'N/A'),
                        record.get('Time', 'N/A')
                    ])
                
                # Create table
                table = Table(table_data, colWidths=[2*inch, 1.5*inch, 1.2*inch, 1*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                ]))
                
                elements.append(table)
            else:
                no_data = Paragraph("No attendance records found.", self.styles['Normal'])
                elements.append(no_data)
            
            # Build PDF
            doc.build(elements)
            
            return True, str(filepath)
        except Exception as e:
            print(f"Error generating PDF report: {e}")
            return False, str(e)
    
    def generate_student_report(self, student_data, attendance_records):
        """Generate individual student attendance report"""
        try:
            date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            reg_no = student_data.get('Registration No', 'unknown')
            filename = f"student_report_{reg_no}_{date_str}.pdf"
            filepath = self.reports_dir / filename
            
            doc = SimpleDocTemplate(str(filepath), pagesize=A4)
            elements = []
            
            # Title
            title = Paragraph(f"Student Attendance Report", self.styles['CustomTitle'])
            elements.append(title)
            elements.append(Spacer(1, 0.2*inch))
            
            # Student info
            student_info = f"""
            <b>Name:</b> {student_data.get('Name', 'N/A')}<br/>
            <b>Registration No:</b> {student_data.get('Registration No', 'N/A')}<br/>
            <b>Enrollment Date:</b> {student_data.get('Enrollment Date', 'N/A')}<br/>
            <b>Total Attendance:</b> {len(attendance_records)} days<br/>
            <b>Report Generated:</b> {datetime.now().strftime("%B %d, %Y")}
            """
            info_para = Paragraph(student_info, self.styles['Normal'])
            elements.append(info_para)
            elements.append(Spacer(1, 0.3*inch))
            
            # Attendance records
            if attendance_records:
                heading = Paragraph("Attendance History", self.styles['CustomHeading'])
                elements.append(heading)
                
                table_data = [['Date', 'Time', 'Status']]
                for record in attendance_records:
                    table_data.append([
                        record.get('Date', 'N/A'),
                        record.get('Time', 'N/A'),
                        'Present'
                    ])
                
                table = Table(table_data, colWidths=[2*inch, 2*inch, 2*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                
                elements.append(table)
            
            doc.build(elements)
            return True, str(filepath)
        except Exception as e:
            print(f"Error generating student report: {e}")
            return False, str(e)
    
    def generate_pdf_bytes(self, attendance_data):
        """Generate PDF and return as bytes for download"""
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            elements = []
            
            title = Paragraph("Attendance Report", self.styles['CustomTitle'])
            elements.append(title)
            elements.append(Spacer(1, 0.2*inch))
            
            if attendance_data:
                table_data = [['Name', 'Reg. No', 'Date', 'Time']]
                for record in attendance_data:
                    table_data.append([
                        record.get('Name', 'N/A'),
                        record.get('Registration No', 'N/A'),
                        record.get('Date', 'N/A'),
                        record.get('Time', 'N/A')
                    ])
                
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                
                elements.append(table)
            
            doc.build(elements)
            buffer.seek(0)
            return buffer
        except Exception as e:
            print(f"Error generating PDF bytes: {e}")
            return None
