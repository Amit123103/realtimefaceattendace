"""
Health check endpoint for deployment monitoring
"""
from flask import jsonify
import sys
import os

def register_health_routes(app):
    """Register health check routes"""
    
    @app.route('/health', methods=['GET'])
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': 'Face Recognition Attendance System',
            'version': '1.0.0',
            'python_version': sys.version,
            'environment': os.environ.get('FLASK_ENV', 'development')
        }), 200
    
    @app.route('/', methods=['GET'])
    def root():
        """Root endpoint"""
        return jsonify({
            'message': 'Face Recognition Attendance System API',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'health': '/health',
                'api_docs': '/api/docs',
                'student_register': '/api/register-student',
                'mark_attendance': '/api/mark-attendance',
                'admin_login': '/api/admin/login'
            },
            'frontend': 'https://amit123103.github.io/realtimeafaceattendance/'
        }), 200
