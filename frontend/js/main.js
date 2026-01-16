// Main JavaScript for Student Interface

// Enhanced Modal System implementation
const enhancedModal = {
    createModalHTML: (type, title, message, details = {}, action = null) => {
        const iconPaths = {
            success: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
            error: 'M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
            warning: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z'
        };

        let detailsHTML = '';
        if (Object.keys(details).length > 0) {
            detailsHTML = '<div class="modal-details">';
            for (const [key, value] of Object.entries(details)) {
                detailsHTML += `<div class="detail-item"><strong>${key}:</strong> ${value}</div>`;
            }
            detailsHTML += '</div>';
        }

        let actionButtonHTML = '';
        if (action) {
            actionButtonHTML = `
                <button class="modal-close-btn" style="margin-right: 10px; background: var(--primary-color);" id="enhanced-modal-action-btn">
                    ${action.label}
                </button>
            `;
        }

        return `
            <div class="enhanced-modal-container enhanced-modal-${type}">
                <div class="enhanced-modal">
                    <div class="modal-content-enhanced">
                        <div class="modal-icon-container">
                            <svg class="modal-icon ${type}-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="${iconPaths[type]}" />
                            </svg>
                        </div>
                        <h2 class="modal-title">${title}</h2>
                        <p class="modal-message">${message}</p>
                        ${detailsHTML}
                        <div style="margin-top: 20px;">
                            ${actionButtonHTML}
                            <button class="modal-close-btn" onclick="enhancedModal.close()">Close</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    show: (type, title, message, details = {}, action = null) => {
        // Remove existing modal if any
        enhancedModal.close();

        const modalDiv = document.createElement('div');
        modalDiv.id = 'enhanced-modal-wrapper';
        modalDiv.innerHTML = enhancedModal.createModalHTML(type, title, message, details, action);
        document.body.appendChild(modalDiv);

        // Add action listener
        if (action) {
            document.getElementById('enhanced-modal-action-btn').addEventListener('click', () => {
                action.callback();
                // Optional: keep open or close? Let's keep open so they can download
            });
        }

        // Trigger animation
        requestAnimationFrame(() => {
            const modalInner = modalDiv.querySelector('.enhanced-modal');
            if (modalInner) modalInner.classList.add('show');
        });
    },

    close: () => {
        const existing = document.getElementById('enhanced-modal-wrapper');
        if (existing) {
            existing.remove();
        }
    },

    showSuccess: (title, message, details, action) => enhancedModal.show('success', title, message, details, action),
    showError: (title, message, details) => enhancedModal.show('error', title, message, details),
    showWarning: (title, message) => enhancedModal.show('warning', title, message)
};


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

        let data;
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.indexOf("application/json") !== -1) {
            data = await response.json();
        } else {
            // Non-JSON response (likely HTML error page)
            const textText = await response.text();
            console.error('Non-JSON response:', textText);
            throw new Error(`Server returned ${response.status}: ${response.statusText}`);
        }

        if (response.ok && data.success) {
            enhancedModal.showSuccess(
                'Registration Successful!',
                `Welcome ${name}! You have been registered successfully.`,
                {
                    'Registration No': registrationNo,
                    'Status': 'Active'
                },
                {
                    label: '⬇ Download QR Code',
                    callback: () => generateStudentQR(registrationNo)
                }
            );
            closeModal('register-modal');
            document.getElementById('register-form').reset();
            // Automatically prompt download
            generateStudentQR(registrationNo);
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

// Generate & Download Student QR
async function generateStudentQR(regNoOverride = null) {
    let registrationNo = regNoOverride;

    if (!registrationNo) {
        const regNoInput = document.getElementById('qr-gen-reg-no');
        if (regNoInput) registrationNo = regNoInput.value.trim();
    }

    if (!registrationNo) {
        enhancedModal.showWarning('Missing Info', 'Please enter your Registration Number');
        return;
    }

    // Show simple notification/toast
    showNotification('Generating QR Code...', 'info');

    try {
        const response = await fetch(`${API_BASE_URL}/generate-student-qr`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ registration_no: registrationNo })
        });

        if (response.ok) {
            // It's a file (blob)
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `QR_${registrationNo}.png`;
            document.body.appendChild(a);
            a.click();
            a.remove();

            showNotification('QR Code Downloaded Successfuly!', 'success');

            // clear input if it exists
            const regNoInput = document.getElementById('qr-gen-reg-no');
            if (regNoInput) regNoInput.value = '';

        } else {
            const data = await response.json();
            enhancedModal.showError('Generation Failed', data.message || 'Could not generate QR');
        }
    } catch (error) {
        console.error("QR Gen Error", error);
        enhancedModal.showError('Connection Error', 'Could not connect to server');
    }
}

// Notification System
function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    if (!notification) return;

    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.classList.add('show');

    setTimeout(() => {
        notification.classList.remove('show');
    }, 4000);
}

// Explicitly export to window
window.enhancedModal = enhancedModal;
window.showRegisterForm = showRegisterForm;
window.showAttendanceForm = showAttendanceForm;
window.closeModal = closeModal;
window.switchAttendanceTab = switchAttendanceTab;
window.initQRScanner = initQRScanner;
window.scanAttendance = scanAttendance;
window.generateStudentQR = generateStudentQR;
window.showNotification = showNotification;

// Explicitly export to window
window.enhancedModal = enhancedModal;
window.showRegisterForm = showRegisterForm;
window.showAttendanceForm = showAttendanceForm;
window.closeModal = closeModal;
window.switchAttendanceTab = switchAttendanceTab;
window.initQRScanner = initQRScanner;
window.scanAttendance = scanAttendance;
window.generateStudentQR = generateStudentQR;
window.showNotification = showNotification;

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Face Recognition Attendance System Loaded');
    console.log('API Base URL:', typeof window.API_BASE_URL !== 'undefined' ? window.API_BASE_URL : 'Unknown');

    // Check Backend Health
    try {
        // Use window.API_BASE_URL explicitly
        const baseUrl = window.API_BASE_URL || API_BASE_URL;
        const response = await fetch(`${baseUrl.replace('/api', '')}/health`);
        const data = await response.json();
        console.log('Backend Status:', data);
    } catch (error) {
        console.error('Backend Health Check Failed:', error);
        enhancedModal.showError(
            'Backend Offline',
            'Cannot connect to the server. Please ensure the backend is running.',
            { 'URL': window.API_BASE_URL }
        );
    }
});
