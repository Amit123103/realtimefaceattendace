// Main JavaScript for Student Interface

const API_BASE_URL = 'http://localhost:5000/api';

// Show/Hide Modals
function showRegisterForm() {
    const modal = document.getElementById('register-modal');
    modal.classList.add('active');
    resetCameraUI('register');
}

function showAttendanceForm() {
    const modal = document.getElementById('attendance-modal');
    modal.classList.add('active');
    resetCameraUI('attendance');
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.remove('active');

    // Stop cameras and reset
    if (modalId === 'register-modal') {
        stopCamera('register');
        resetCameraUI('register');
        document.getElementById('register-form').reset();
    } else if (modalId === 'attendance-modal') {
        stopCamera('attendance');
        resetCameraUI('attendance');
    }
}

// Close modal on outside click
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        closeModal(e.target.id);
    }
});

// Student Registration Form Handler
document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const name = document.getElementById('student-name').value.trim();
    const registrationNo = document.getElementById('registration-no').value.trim();
    const image = getCapturedImage('register');

    // Validation
    if (!name || !registrationNo) {
        enhancedModal.showWarning('Missing Information', 'Please fill in all fields');
        return;
    }

    if (!image) {
        enhancedModal.showWarning('Face Not Captured', 'Please capture your face image before submitting');
        return;
    }

    // Show loading
    const submitBtn = document.getElementById('submit-register-btn');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoader = submitBtn.querySelector('.btn-loader');

    submitBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline-block';

    try {
        const response = await fetch(`${API_BASE_URL}/register-student`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                registration_no: registrationNo,
                image: image
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            enhancedModal.showSuccess(
                'Registration Successful!',
                `Welcome ${name}! You have been registered successfully.`,
                {
                    'Registration No': registrationNo,
                    'Status': 'Active'
                }
            );
            closeModal('register-modal');
            document.getElementById('register-form').reset();
        } else {
            enhancedModal.showError(
                'Registration Failed',
                data.message || 'Unable to register student. Please try again.',
                data.details || {}
            );
        }
    } catch (error) {
        console.error('Error:', error);
        enhancedModal.showError(
            'Network Error',
            'Could not connect to server. Please ensure the backend is running.',
            { 'Server': 'http://localhost:5000' }
        );
    } finally {
        submitBtn.disabled = false;
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
});

// Scan Attendance
async function scanAttendance() {
    const image = getCapturedImage('attendance');

    if (!image) {
        // Capture image first
        captureImage('attendance');
        return;
    }

    // Show loading
    const scanBtn = document.getElementById('scan-attendance-btn');
    const btnText = scanBtn.querySelector('.btn-text');
    const btnLoader = scanBtn.querySelector('.btn-loader');

    scanBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline-block';

    try {
        const response = await fetch(`${API_BASE_URL}/mark-attendance`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                image: image
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            // SUCCESS: Face matched!
            enhancedModal.showSuccess(
                '✓ Attendance Marked!',
                `Welcome ${data.data.name}! Your attendance has been recorded.`,
                {
                    'Name': data.data.name,
                    'Registration No': data.data.registration_no,
                    'Time': data.data.time,
                    'Confidence': `${data.data.confidence}%`
                }
            );
            closeModal('attendance-modal');
        } else {
            // ERROR: Face not matched!
            enhancedModal.showError(
                '✗ Face Not Recognized',
                data.message || 'Your face was not recognized in our system. Please register first or try again.',
                {
                    'Status': 'Not Matched',
                    'Action': 'Please register or try scanning again'
                }
            );
            // Allow retake
            retakeImage('attendance');
        }
    } catch (error) {
        console.error('Error:', error);
        enhancedModal.showError(
            'Connection Error',
            'Could not connect to the attendance server. Please try again.',
            { 'Server Status': 'Unreachable' }
        );
    } finally {
        scanBtn.disabled = false;
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
}

// Notification System
function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');

    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.classList.add('show');

    setTimeout(() => {
        notification.classList.remove('show');
    }, 4000);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('Face Recognition Attendance System Loaded');
    console.log('API Base URL:', API_BASE_URL);
});
