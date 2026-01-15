// Sound Alert System

class SoundAlerts {
    constructor() {
        this.audioContext = null;
        this.initAudioContext();
    }

    initAudioContext() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        } catch (e) {
            console.warn('Web Audio API not supported');
        }
    }

    playSuccessSound() {
        if (!this.audioContext) return;

        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);

        // Success sound: ascending notes
        oscillator.frequency.setValueAtTime(523.25, this.audioContext.currentTime); // C5
        oscillator.frequency.setValueAtTime(659.25, this.audioContext.currentTime + 0.1); // E5
        oscillator.frequency.setValueAtTime(783.99, this.audioContext.currentTime + 0.2); // G5

        gainNode.gain.setValueAtTime(0.3, this.audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.5);

        oscillator.start(this.audioContext.currentTime);
        oscillator.stop(this.audioContext.currentTime + 0.5);
    }

    playErrorSound() {
        if (!this.audioContext) return;

        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);

        // Error sound: descending beep
        oscillator.frequency.setValueAtTime(400, this.audioContext.currentTime);
        oscillator.frequency.setValueAtTime(200, this.audioContext.currentTime + 0.2);

        oscillator.type = 'square';

        gainNode.gain.setValueAtTime(0.3, this.audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.3);

        oscillator.start(this.audioContext.currentTime);
        oscillator.stop(this.audioContext.currentTime + 0.3);
    }

    playWarningSound() {
        if (!this.audioContext) return;

        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);

        // Warning sound: two beeps
        oscillator.frequency.setValueAtTime(600, this.audioContext.currentTime);

        gainNode.gain.setValueAtTime(0.3, this.audioContext.currentTime);
        gainNode.gain.setValueAtTime(0, this.audioContext.currentTime + 0.1);
        gainNode.gain.setValueAtTime(0.3, this.audioContext.currentTime + 0.15);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.3);

        oscillator.start(this.audioContext.currentTime);
        oscillator.stop(this.audioContext.currentTime + 0.3);
    }
}

// Initialize sound system
const soundAlerts = new SoundAlerts();

// Enhanced Modal System
class EnhancedModal {
    constructor() {
        this.createModalContainer();
    }

    createModalContainer() {
        // Create modal container if it doesn't exist
        if (!document.getElementById('enhanced-modal-container')) {
            const container = document.createElement('div');
            container.id = 'enhanced-modal-container';
            container.className = 'enhanced-modal-container';
            document.body.appendChild(container);
        }
    }

    showSuccess(title, message, details = {}) {
        soundAlerts.playSuccessSound();
        this.showModal('success', title, message, details);
    }

    showError(title, message, details = {}) {
        soundAlerts.playErrorSound();
        this.showModal('error', title, message, details);
    }

    showWarning(title, message, details = {}) {
        soundAlerts.playWarningSound();
        this.showModal('warning', title, message, details);
    }

    showModal(type, title, message, details) {
        const container = document.getElementById('enhanced-modal-container');

        const modal = document.createElement('div');
        modal.className = `enhanced-modal enhanced-modal-${type}`;

        const iconMap = {
            success: `
                <svg class="modal-icon success-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                    <path d="M8 12L11 15L16 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            `,
            error: `
                <svg class="modal-icon error-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                    <path d="M15 9L9 15M9 9L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
            `,
            warning: `
                <svg class="modal-icon warning-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L2 20H22L12 2Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                    <path d="M12 9V13M12 17H12.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
            `
        };

        let detailsHTML = '';
        if (Object.keys(details).length > 0) {
            detailsHTML = '<div class="modal-details">';
            for (const [key, value] of Object.entries(details)) {
                detailsHTML += `<div class="detail-item"><strong>${key}:</strong> ${value}</div>`;
            }
            detailsHTML += '</div>';
        }

        modal.innerHTML = `
            <div class="modal-content-enhanced">
                <div class="modal-icon-container">
                    ${iconMap[type]}
                </div>
                <h2 class="modal-title">${title}</h2>
                <p class="modal-message">${message}</p>
                ${detailsHTML}
                <button class="modal-close-btn" onclick="this.closest('.enhanced-modal').remove()">
                    OK
                </button>
            </div>
        `;

        container.appendChild(modal);

        // Animate in
        setTimeout(() => modal.classList.add('show'), 10);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            modal.classList.remove('show');
            setTimeout(() => modal.remove(), 300);
        }, 5000);
    }
}

// Initialize enhanced modal system
const enhancedModal = new EnhancedModal();

// Export for use in other files
window.soundAlerts = soundAlerts;
window.enhancedModal = enhancedModal;
