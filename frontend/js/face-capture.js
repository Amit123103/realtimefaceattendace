// Webcam and Face Capture Utilities

const cameraStreams = {
    register: null,
    attendance: null,
    admin: null
};

const capturedImages = {
    register: null,
    attendance: null,
    admin: null
};

// Start camera for specific context
async function startCamera(context) {
    try {
        const video = document.getElementById(`${context}-video`);
        const startBtn = document.getElementById(`start-${context}-camera`);
        const captureBtn = document.getElementById(`capture-${context}-btn`) || document.getElementById(`scan-${context}-btn`);

        // Request camera access
        const stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: 'user'
            },
            audio: false
        });

        // Store stream
        cameraStreams[context] = stream;

        // Set video source
        video.srcObject = stream;
        video.play();

        // Update UI
        if (startBtn) startBtn.style.display = 'none';
        if (captureBtn) captureBtn.style.display = 'inline-flex';

        showNotification('Camera started successfully', 'success');
    } catch (error) {
        console.error('Error accessing camera:', error);
        showNotification('Could not access camera. Please grant permission.', 'error');
    }
}

// Stop camera
function stopCamera(context) {
    const stream = cameraStreams[context];
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        cameraStreams[context] = null;
    }

    const video = document.getElementById(`${context}-video`);
    if (video) {
        video.srcObject = null;
    }
}

// Capture image from video
function captureImage(context) {
    const video = document.getElementById(`${context}-video`);
    const canvas = document.getElementById(`${context}-canvas`);
    const preview = document.getElementById(`${context}-preview`);
    const previewImg = document.getElementById(`${context}-preview-img`);
    const captureBtn = document.getElementById(`capture-${context}-btn`);
    const retakeBtn = document.getElementById(`retake-${context}-btn`);

    if (!video || !canvas) return;

    // Set canvas dimensions
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw video frame to canvas
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Get image data
    const imageData = canvas.toDataURL('image/jpeg', 0.9);
    capturedImages[context] = imageData;

    // Show preview
    if (preview && previewImg) {
        previewImg.src = imageData;
        preview.style.display = 'flex';
        video.style.display = 'none';
    }

    // Update UI
    if (captureBtn) captureBtn.style.display = 'none';
    if (retakeBtn) retakeBtn.style.display = 'inline-flex';

    // Stop camera
    stopCamera(context);

    showNotification('Face captured successfully!', 'success');
}

// Retake image
function retakeImage(context) {
    const video = document.getElementById(`${context}-video`);
    const preview = document.getElementById(`${context}-preview`);
    const captureBtn = document.getElementById(`capture-${context}-btn`);
    const retakeBtn = document.getElementById(`retake-${context}-btn`);

    // Clear captured image
    capturedImages[context] = null;

    // Show video, hide preview
    if (video && preview) {
        video.style.display = 'block';
        preview.style.display = 'none';
    }

    // Update UI
    if (captureBtn) captureBtn.style.display = 'inline-flex';
    if (retakeBtn) retakeBtn.style.display = 'none';

    // Restart camera
    startCamera(context);
}

// Get captured image
function getCapturedImage(context) {
    return capturedImages[context];
}

// Clear captured image
function clearCapturedImage(context) {
    capturedImages[context] = null;
}

// Check if image is captured
function hasImageCaptured(context) {
    return capturedImages[context] !== null;
}

// Reset camera UI
function resetCameraUI(context) {
    const video = document.getElementById(`${context}-video`);
    const preview = document.getElementById(`${context}-preview`);
    const startBtn = document.getElementById(`start-${context}-camera`);
    const captureBtn = document.getElementById(`capture-${context}-btn`) || document.getElementById(`scan-${context}-btn`);
    const retakeBtn = document.getElementById(`retake-${context}-btn`);

    // Stop camera
    stopCamera(context);

    // Clear captured image
    clearCapturedImage(context);

    // Reset UI
    if (video) video.style.display = 'block';
    if (preview) preview.style.display = 'none';
    if (startBtn) startBtn.style.display = 'inline-flex';
    if (captureBtn) captureBtn.style.display = 'none';
    if (retakeBtn) retakeBtn.style.display = 'none';
}
