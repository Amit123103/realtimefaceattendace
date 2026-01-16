// Admin Panel JavaScript
// API_BASE_URL is defined in config.js

let sessionToken = null;

// Check authentication on page load
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    loadDashboardData();
});

// Check if user is authenticated
async function checkAuth() {
    sessionToken = localStorage.getItem('admin_session');

    if (!sessionToken) {
        window.location.href = 'admin-login.html';
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/admin/verify-session`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ session_token: sessionToken })
        });

        const data = await response.json();

        if (!data.valid) {
            localStorage.removeItem('admin_session');
            window.location.href = 'admin-login.html';
        }
    } catch (error) {
        console.error('Error verifying session:', error);
        showNotification('Session verification failed', 'error');
    }
}

// Section Navigation
function showSection(sectionId) {
    // Update nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    event.target.classList.add('active');

    // Update sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(sectionId).classList.add('active');

    // Load section data
    if (sectionId === 'students') {
        loadStudents();
    } else if (sectionId === 'attendance') {
        loadAttendance();
    } else if (sectionId === 'analytics') {
        // Initialize analytics dashboard
        if (typeof AnalyticsDashboard !== 'undefined') {
            AnalyticsDashboard.init();
        }
    } else if (sectionId === 'admin-management') {
        loadAdmins();
    } else if (sectionId === 'student-support') {
        loadSupportTickets();
    }
}

// Load Dashboard Data
async function loadDashboardData() {
    try {
        // Load students count
        const studentsResponse = await fetch(`${API_BASE_URL}/admin/students`, {
            headers: { 'Authorization': sessionToken }
        });
        const studentsData = await studentsResponse.json();

        if (studentsData.success) {
            document.getElementById('total-students').textContent = studentsData.count;
        }

        // Load attendance count
        const attendanceResponse = await fetch(`${API_BASE_URL}/admin/attendance`, {
            headers: { 'Authorization': sessionToken }
        });
        const attendanceData = await attendanceResponse.json();

        if (attendanceData.success) {
            document.getElementById('total-attendance').textContent = attendanceData.count;

            // Calculate today's attendance
            const today = new Date().toISOString().split('T')[0];
            const todayRecords = attendanceData.data.filter(record => record.Date === today);
            document.getElementById('today-attendance').textContent = todayRecords.length;
        }
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

// Load Students
async function loadStudents() {
    const tbody = document.getElementById('students-table-body');
    tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 2rem; color: var(--text-muted);">Loading students...</td></tr>';

    try {
        const response = await fetch(`${API_BASE_URL}/admin/students`, {
            headers: { 'Authorization': sessionToken }
        });

        const data = await response.json();

        if (data.success && data.data.length > 0) {
            tbody.innerHTML = data.data.map(student => `
                <tr>
                    <td>${student.Name}</td>
                    <td>${student['Registration No']}</td>
                    <td>${student['Enrollment Date']}</td>
                    <td>
                        ${student['Image Path'] ? `<img src="../data/${student['Image Path']}" alt="${student.Name}" class="table-image">` : 'N/A'}
                    </td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 2rem; color: var(--text-muted);">No students registered yet</td></tr>';
        }
    } catch (error) {
        console.error('Error loading students:', error);
        tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 2rem; color: var(--error-color);">Error loading students</td></tr>';
    }
}

// Load Attendance
async function loadAttendance(startDate = null, endDate = null) {
    const tbody = document.getElementById('attendance-table-body');
    tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 2rem; color: var(--text-muted);">Loading attendance records...</td></tr>';

    try {
        let url = `${API_BASE_URL}/admin/attendance`;
        const params = new URLSearchParams();

        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);

        if (params.toString()) {
            url += '?' + params.toString();
        }

        const response = await fetch(url, {
            headers: { 'Authorization': sessionToken }
        });

        const data = await response.json();

        if (data.success && data.data.length > 0) {
            tbody.innerHTML = data.data.map(record => `
                <tr>
                    <td>${record.Name}</td>
                    <td>${record['Registration No']}</td>
                    <td>${record.Date}</td>
                    <td>${record.Time}</td>
                    <td>
                        ${record['Image Path'] ? `<img src="../data/${record['Image Path']}" alt="${record.Name}" class="table-image">` : 'N/A'}
                    </td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 2rem; color: var(--text-muted);">No attendance records found</td></tr>';
        }
    } catch (error) {
        console.error('Error loading attendance:', error);
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 2rem; color: var(--error-color);">Error loading attendance records</td></tr>';
    }
}

// Filter Attendance
function filterAttendance() {
    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;

    loadAttendance(startDate, endDate);
}

// Clear Filters
function clearFilters() {
    document.getElementById('start-date').value = '';
    document.getElementById('end-date').value = '';
    loadAttendance();
}

// Export Students
async function exportStudents() {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/export-students`, {
            headers: { 'Authorization': sessionToken }
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `students_export_${new Date().toISOString().split('T')[0]}.xlsx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            showNotification('Students data exported successfully!', 'success');
        } else {
            showNotification('Error exporting students data', 'error');
        }
    } catch (error) {
        console.error('Error exporting students:', error);
        showNotification('Network error during export', 'error');
    }
}

// Export Attendance
async function exportAttendance() {
    try {
        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;

        let url = `${API_BASE_URL}/admin/export-attendance`;
        const params = new URLSearchParams();

        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);

        if (params.toString()) {
            url += '?' + params.toString();
        }

        const response = await fetch(url, {
            headers: { 'Authorization': sessionToken }
        });

        if (response.ok) {
            const blob = await response.blob();
            const urlBlob = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = urlBlob;
            a.download = `attendance_export_${new Date().toISOString().split('T')[0]}.xlsx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(urlBlob);
            document.body.removeChild(a);

            showNotification('Attendance data exported successfully!', 'success');
        } else {
            showNotification('Error exporting attendance data', 'error');
        }
    } catch (error) {
        console.error('Error exporting attendance:', error);
        showNotification('Network error during export', 'error');
    }
}

// Bulk Upload
const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('bulk-file-input');

uploadArea.addEventListener('click', () => {
    fileInput.click();
});

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileUpload(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileUpload(e.target.files[0]);
    }
});

async function handleFileUpload(file) {
    const progressDiv = document.getElementById('upload-progress');
    const progressFill = document.getElementById('progress-fill');
    const uploadStatus = document.getElementById('upload-status');

    // Validate file type
    if (!file.name.endsWith('.zip') && !file.name.endsWith('.csv')) {
        showNotification('Please upload a ZIP or CSV file', 'error');
        return;
    }

    // Show progress
    progressDiv.style.display = 'block';
    progressFill.style.width = '0%';
    uploadStatus.textContent = 'Uploading file...';

    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE_URL}/admin/bulk-upload`, {
            method: 'POST',
            headers: {
                'Authorization': sessionToken
            },
            body: formData
        });

        const data = await response.json();

        // Simulate progress
        progressFill.style.width = '50%';
        uploadStatus.textContent = 'Processing data...';

        await new Promise(resolve => setTimeout(resolve, 500));

        progressFill.style.width = '100%';
        uploadStatus.textContent = 'Complete!';

        if (data.success) {
            showNotification(data.message, 'success');

            // Reload students if on that section
            if (document.getElementById('students').classList.contains('active')) {
                loadStudents();
            }

            // Reload dashboard data
            loadDashboardData();
        } else {
            showNotification(data.message || 'Upload failed', 'error');
        }

        // Hide progress after delay
        setTimeout(() => {
            progressDiv.style.display = 'none';
            fileInput.value = '';
        }, 2000);
    } catch (error) {
        console.error('Error uploading file:', error);
        showNotification('Network error during upload', 'error');
        progressDiv.style.display = 'none';
    }
}

// Register Admin Face
async function registerAdminFace() {
    const image = getCapturedImage('settings');

    if (!image) {
        showNotification('Please capture your face first', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/admin/register-face`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': sessionToken
            },
            body: JSON.stringify({ image })
        });

        const data = await response.json();

        if (data.success) {
            showNotification('Admin face registered successfully!', 'success');
            resetCameraUI('settings');
        } else {
            showNotification(data.message || 'Failed to register face', 'error');
        }
    } catch (error) {
        console.error('Error registering admin face:', error);
        showNotification('Network error', 'error');
    }
}

// Logout
function logout() {
    if (confirm('Are you sure you want to logout?')) {
        localStorage.removeItem('admin_session');
        window.location.href = 'index.html';
    }
}

// Notification
function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.classList.add('show');
    setTimeout(() => notification.classList.remove('show'), 4000);
}
