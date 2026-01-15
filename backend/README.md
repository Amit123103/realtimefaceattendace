# Face Recognition Attendance System - Backend API

## 🚀 Quick Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### Automatic Deployment

This repository is configured for one-click deployment to Render.com:

1. Click the "Deploy to Render" button above
2. Sign in to Render (or create account)
3. Configure environment variables:
   - `MAIL_USERNAME` - Your Gmail address
   - `MAIL_PASSWORD` - Your Gmail app password
4. Click "Create Web Service"
5. Wait 3-5 minutes for deployment

Your backend API will be live at: `https://your-app-name.onrender.com`

### Manual Deployment

If you prefer manual setup:

1. **Create Render Account:** https://render.com
2. **New Web Service** → Connect this repository
3. **Settings:**
   ```
   Name: face-attendance-api
   Environment: Python 3
   Build Command: pip install -r backend/requirements.txt
   Start Command: cd backend && gunicorn app:app
   ```
4. **Environment Variables:**
   ```
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   FLASK_ENV=production
   ```

### After Deployment

1. **Get your backend URL:** `https://your-app.onrender.com`
2. **Update frontend:** Change `API_BASE_URL` in all frontend JS files
3. **Test API:** Visit `https://your-app.onrender.com/api/health`

### Features

- ✅ 36 REST API endpoints
- ✅ Face recognition with OpenCV
- ✅ Excel-based data storage
- ✅ QR code generation
- ✅ PDF report generation
- ✅ Email notifications
- ✅ Multi-admin support
- ✅ Support ticket system

### API Documentation

Full API documentation available at: `/api/docs` (when deployed)

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PORT` | No | 5000 | Server port |
| `HOST` | No | 0.0.0.0 | Server host |
| `FLASK_ENV` | No | production | Environment mode |
| `MAIL_SERVER` | Yes* | smtp.gmail.com | SMTP server |
| `MAIL_PORT` | Yes* | 587 | SMTP port |
| `MAIL_USE_TLS` | Yes* | True | Use TLS |
| `MAIL_USERNAME` | Yes* | - | Email username |
| `MAIL_PASSWORD` | Yes* | - | Email password |

*Required only if using email features

### Local Development

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Server will start at `http://localhost:5000`

### Production Notes

- Uses `gunicorn` as WSGI server
- OpenCV headless version for cloud compatibility
- Automatic port binding from environment
- CORS enabled for frontend integration
- Debug mode disabled in production

### Support

- **Issues:** https://github.com/Amit123103/realtimeafaceattendance/issues
- **Email:** amitsingh6394366374@gmail.com

---

**Made with ❤️ by Amit Singh**
