# 🎓 Face Recognition Attendance System

A complete, enterprise-grade attendance management system with facial recognition, QR codes, analytics, and comprehensive support features.

![System Demo](https://img.shields.io/badge/Status-Production%20Ready-success)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

### 🎯 Core Functionality
- **Face Recognition** - OpenCV-based face detection and SSIM comparison
- **Student Registration** - Register students with face capture
- **Attendance Marking** - Mark attendance via face recognition
- **Excel Data Management** - Store data in Excel files
- **Admin Authentication** - Password and face-based admin login
- **Bulk Upload** - Import multiple students via CSV/Excel

### 📊 Advanced Features
- **Analytics Dashboard** - Chart.js visualizations (daily/weekly/monthly trends)
- **QR Code Attendance** - Alternative attendance method with QR scanning
- **PDF Reports** - Generate professional attendance reports
- **Email Notifications** - Send reports via email (Flask-Mail)
- **Student Portal** - Students can view their attendance history
- **Multi-Admin Support** - Role-based permissions (super_admin, admin, viewer)
- **Support System** - Student-to-admin tickets and admin-to-email support

### 🎨 UI/UX
- **3D Animations** - Three.js particle effects and geometric shapes
- **Glassmorphism Design** - Modern dark theme with glass effects
- **Sound Alerts** - Web Audio API feedback
- **Enhanced Modals** - Animated success/error/warning popups
- **Responsive Design** - Works on all screen sizes

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Amit123103/face-attendance.git
cd face-attendance
```

2. **Install dependencies**
```bash
cd backend
pip install -r requirements.txt
```

3. **Run the server**
```bash
python app.py
```

4. **Open the application**
- Student Interface: `frontend/index.html`
- Admin Login: `frontend/admin-login.html`
- Student Portal: `frontend/student-portal.html`
- QR Scanner: `frontend/qr-scanner.html`

### Default Admin Credentials
- **Username:** `amitsingh6394366374@gmail.com`
- **Password:** `Amit1@`
- **Role:** `super_admin`

## 📁 Project Structure

```
face-attendance-system/
├── backend/
│   ├── app.py                    # Main Flask application (36 endpoints)
│   ├── face_engine.py            # Face detection and comparison
│   ├── excel_handler.py          # Excel data management
│   ├── admin_auth.py             # Admin authentication
│   ├── analytics.py              # Analytics engine
│   ├── qr_handler.py             # QR code generation/verification
│   ├── pdf_generator.py          # PDF report generation
│   ├── email_service.py          # Email notifications
│   ├── multi_admin.py            # Multi-admin management
│   ├── support_handler.py        # Support ticket system
│   └── requirements.txt          # Python dependencies
├── frontend/
│   ├── index.html                # Student interface
│   ├── admin-login.html          # Admin login page
│   ├── admin-panel.html          # Admin dashboard
│   ├── student-portal.html       # Student portal
│   ├── qr-scanner.html           # QR code scanner
│   ├── css/                      # Stylesheets
│   └── js/                       # JavaScript files
└── data/
    ├── students.xlsx             # Student records
    ├── attendance.xlsx           # Attendance records
    ├── admins.xlsx               # Admin accounts
    ├── support_tickets.xlsx      # Support tickets
    ├── images/                   # Student and attendance images
    ├── encodings/                # Face encodings
    ├── qr_codes/                 # Generated QR codes
    └── reports/                  # PDF reports
```

## 🔧 API Endpoints

### Student Endpoints
- `POST /api/register-student` - Register new student
- `POST /api/mark-attendance` - Mark attendance with face
- `POST /api/scan-qr-attendance` - Mark attendance with QR
- `POST /api/student/login` - Student portal login
- `POST /api/support/create-ticket` - Create support ticket

### Admin Endpoints
- `POST /api/admin/login` - Admin login
- `POST /api/admin/verify-session` - Verify session
- `GET /api/admin/students` - Get all students
- `GET /api/admin/attendance` - Get attendance records
- `GET /api/admin/export-students` - Export students Excel
- `GET /api/admin/export-attendance` - Export attendance Excel
- `POST /api/admin/bulk-upload` - Bulk upload students

### Analytics Endpoints
- `GET /api/admin/analytics/summary` - Summary statistics
- `GET /api/admin/analytics/daily` - Daily attendance
- `GET /api/admin/analytics/weekly` - Weekly trends
- `GET /api/admin/analytics/monthly` - Monthly overview
- `GET /api/admin/analytics/student-percentages` - Student percentages

### Support Endpoints
- `GET /api/admin/support/tickets` - Get all tickets
- `GET /api/admin/support/ticket/<id>` - Get specific ticket
- `POST /api/admin/support/update-ticket` - Update ticket
- `GET /api/admin/support/stats` - Ticket statistics
- `POST /api/admin/support/request-help` - Admin support request

### QR & Reports
- `GET /api/admin/generate-qr/<regno>` - Generate QR code
- `GET /api/admin/generate-pdf-report` - Generate PDF report
- `POST /api/admin/send-email-report` - Send email report

### Multi-Admin
- `POST /api/admin/manage/add-admin` - Add new admin
- `GET /api/admin/manage/list-admins` - List all admins
- `POST /api/admin/manage/update-role` - Update admin role
- `POST /api/admin/manage/deactivate` - Deactivate admin

## ⚙️ Configuration

### Email Setup (Optional)
Create `.env` file in `backend/` directory:

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@attendance.com
```

## 🎯 Usage

### For Students
1. Open `frontend/index.html`
2. Click "Register New Student"
3. Enter name and registration number
4. Capture face photo
5. Submit registration

To mark attendance:
1. Click "Mark Attendance"
2. Capture face photo
3. System matches face and marks attendance

### For Admins
1. Open `frontend/admin-login.html`
2. Login with credentials
3. Access admin panel features:
   - View dashboard statistics
   - Manage students
   - View attendance records
   - Export data to Excel
   - View analytics charts
   - Manage support tickets
   - Generate QR codes
   - Download PDF reports

## 🛠️ Technologies Used

### Backend
- **Flask** - Web framework
- **OpenCV** - Face detection
- **scikit-image** - SSIM face comparison
- **pandas** - Data management
- **openpyxl** - Excel file handling
- **qrcode** - QR code generation
- **ReportLab** - PDF generation
- **Flask-Mail** - Email sending

### Frontend
- **HTML5/CSS3/JavaScript** - Core web technologies
- **Three.js** - 3D animations
- **Particles.js** - Particle effects
- **Chart.js** - Data visualization
- **HTML5-QRCode** - QR code scanning
- **Webcam.js** - Camera access

## 📊 Statistics

- **Total API Endpoints:** 36
- **Frontend Pages:** 5
- **Backend Modules:** 10
- **Features:** 20+
- **Lines of Code:** 5000+

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License.

## 👨‍💻 Author

**Amit Singh**
- Email: amitsingh6394366374@gmail.com
- GitHub: [@Amit123103](https://github.com/Amit123103)

## 🙏 Acknowledgments

- OpenCV for face detection
- Flask community for excellent documentation
- Chart.js for beautiful visualizations

## 📞 Support

For technical support or questions, please:
1. Open an issue on GitHub
2. Email: amitsingh6394366374@gmail.com

---

**Made with ❤️ by Amit Singh**
