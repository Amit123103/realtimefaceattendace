// API Configuration
// This file automatically detects if running locally or in production

// API Configuration
window.API_BASE_URL = (() => {
    const host = window.location.hostname;

    // Check if we're on GitHub Pages
    if (host === 'amit123103.github.io') {
        // Production - Deployed backend on Render
        return 'https://face-attendance-ajre.onrender.com/api';
    } else if (host === 'localhost' || host === '127.0.0.1' || host === '') {
        // Local development or file:// access
        return 'http://localhost:8000/api';
    } else {
        // Network access (e.g. 192.168.x.x) - assume backend is on same IP port 5000
        return `http://${host}:8000/api`;
    }
})();

const API_BASE_URL = window.API_BASE_URL; // Local const for THIS file if needed, but not strictly necessary if we use window.API_BASE_URL everywhere. 
// However, main.js uses API_BASE_URL directly. Defining it on window makes it available as 'API_BASE_URL' (global var) in most browsers, but explicit window.API_BASE_URL is safer.
// To support `const API_BASE_URL` usage in other files without window., we rely on the fact that window properties are global variables.


console.log('API Base URL:', API_BASE_URL);
