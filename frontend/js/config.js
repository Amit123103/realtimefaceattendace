// API Configuration
// This file automatically detects if running locally or in production

const API_BASE_URL = (() => {
    // Check if we're on GitHub Pages
    if (window.location.hostname === 'amit123103.github.io') {
        // Production - Update this URL after deploying backend to Render
        return 'https://your-backend-url.onrender.com/api';
        // TODO: Replace 'your-backend-url' with actual Render deployment URL
    } else {
        // Local development
        return 'http://localhost:5000/api';
    }
})();

console.log('API Base URL:', API_BASE_URL);
