// API Configuration
// This file automatically detects if running locally or in production

const API_BASE_URL = (() => {
    // Check if we're on GitHub Pages
    if (window.location.hostname === 'amit123103.github.io') {
        // Production - Deployed backend on Render
        return 'https://faceattendance-509d.onrender.com/api';
    } else {
        // Local development
        return 'http://localhost:5000/api';
    }
})();

console.log('API Base URL:', API_BASE_URL);
