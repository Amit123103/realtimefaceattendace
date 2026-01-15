// Main JavaScript for Student Interface

// API_BASE_URL is now loaded from js/config.js

// Valid Tabs
let currentAttTab = 'face';
let html5QrcodeScanner = null;

// Show/Hide Modals
function showRegisterForm() {
    const modal = document.getElementById('register-modal');
    modal.classList.add('active');
    resetCameraUI('register');
}

function showAttendanceForm() {
    const modal = document.getElementById('attendance-modal');
    modal.classList.add('active');

    // Default to face tab
    switchAttendanceTab('face');
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

        // Stop QR Scanner
        if (html5QrcodeScanner) {
            html5QrcodeScanner.clear();
            html5QrcodeScanner = null;
        }
    }
}

// Switch Attendance Tab
function switchAttendanceTab(tab) {
    currentAttTab = tab;

    // Update buttons
    const buttons = document.querySelectorAll('.tab-btn');
    buttons.forEach(btn => btn.classList.remove('active'));
    // Simple logic assuming order: 0 is face, 1 is qr. 
    // Better to use ID or event target, but for now:
    if (tab === 'face') buttons[0].classList.add('active');
    else buttons[1].classList.add('active');

    // Toggle content
    document.getElementById('att-face-tab').style.display = tab === 'face' ? 'block' : 'none';
    document.getElementById('att-qr-tab').style.display = tab === 'qr' ? 'block' : 'none';

    // Handle camera states
    if (tab === 'face') {
        if (html5QrcodeScanner) {
            html5QrcodeScanner.clear();
            html5QrcodeScanner = null;
        }
        resetCameraUI('attendance');
    } else {
        stopCamera('attendance');
    }
}

// QR Scanner Logic
function initQRScanner() {
    if (html5QrcodeScanner) return; // Already running

    html5QrcodeScanner = new Html5QrcodeScanner(
        "qr-reader",
        { fps: 10, qrbox: { width: 250, height: 250 } },
        /* verbose= */ false
    );

    html5QrcodeScanner.render(onScanSuccess, onScanFailure);

    // Hide the start button
    event.target.style.display = 'none';
}

async function onScanSuccess(decodedText, decodedResult) {
    // Handle the scanned code
    console.log(`Code matched = ${decodedText}`, decodedResult);

    // Stop scanning
    if (html5QrcodeScanner) {
        html5QrcodeScanner.clear();
        html5QrcodeScanner = null;
        document.getElementById('qr-reader').innerHTML = ""; // Clear div
    }

    document.getElementById('qr-result').innerText = "Processing: " + decodedText; // Show feedback

    // Call backend
    try {
        const response = await fetch(`${API_BASE_URL}/mark-attendance-qr`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ qr_data: decodedText })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            enhancedModal.showSuccess(
                '✓ Attendance Marked (QR)!',
                `Welcome ${data.data.name}! Your attendance has been recorded via QR Code.`,
                {
                    'Name': data.data.name,
                    'Registration No': data.data.registration_no,
                    'Time': data.data.time,
                    'Mode': 'QR Scan'
                }
            );
            closeModal('attendance-modal');
        } else {
            enhancedModal.showError(
                '✗ QR Not Recognized',
                data.message || 'Invalid QR Code',
                { 'Scanned Data': decodedText }
            );
        }
    } catch (error) {
        console.error("QR Error", error);
        enhancedModal.showError('Connection Error', 'Could not verify QR code.');
    }
}

function onScanFailure(error) {
    // handle scan failure, usually better to ignore and keep scanning.
    // console.warn(`Code scan error = ${error}`);
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

// Scan Attendance (Face) - Improved
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
                data.message || 'Your face was not recognized. Please scan slowly or try QR Code.',
                {
                    'Status': 'Not Matched',
                    'Action': 'Try Again or Use QR Tab'
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
    console.log('API Base URL:', typeof API_BASE_URL !== 'undefined' ? API_BASE_URL : 'Unknown');
});
