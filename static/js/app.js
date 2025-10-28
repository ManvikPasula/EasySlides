// Voice to Slides Generator - Frontend JavaScript

class VoiceToSlidesApp {
    constructor() {
        this.recognition = null;
        this.isRecording = false;
        this.recordingStartTime = null;
        this.finalTranscript = '';
        
        this.initializeApp();
        this.setupEventListeners();
    }
    
    initializeApp() {
        // Check for Web Speech API support
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            console.warn('Web Speech API not supported');
            this.showNotification('Voice recording is not supported in your browser. Please upload an audio file instead.', 'warning');
        } else {
            this.initializeSpeechRecognition();
        }
        
        // Initialize Feather icons
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
    }
    
    initializeSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        
        this.recognition.continuous = true;
        this.recognition.interimResults = true;
        this.recognition.lang = 'en-US';
        
        this.recognition.onstart = () => {
            console.log('Speech recognition started');
            this.isRecording = true;
            this.recordingStartTime = Date.now();
            this.showRecordingStatus();
            this.startRecordingTimer();
        };
        
        this.recognition.onresult = (event) => {
            let interimTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    this.finalTranscript += transcript + ' ';
                } else {
                    interimTranscript += transcript;
                }
            }
            
            this.updateTranscriptDisplay(this.finalTranscript + interimTranscript);
        };
        
        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.stopRecording();
            this.showNotification('Speech recognition error: ' + event.error, 'error');
        };
        
        this.recognition.onend = () => {
            console.log('Speech recognition ended');
            this.stopRecording();
        };
    }
    
    setupEventListeners() {
        // Recording controls
        const recordBtn = document.getElementById('recordBtn');
        const stopBtn = document.getElementById('stopBtn');
        const generateBtn = document.getElementById('generateFromTranscript');
        
        if (recordBtn) {
            recordBtn.addEventListener('click', () => this.startRecording());
        }
        
        if (stopBtn) {
            stopBtn.addEventListener('click', () => this.stopRecording());
        }
        
        if (generateBtn) {
            generateBtn.addEventListener('click', () => this.generateSlidesFromTranscript());
        }
        
        // File upload
        const uploadZone = document.getElementById('uploadZone');
        const audioFileInput = document.getElementById('audioFile');
        
        if (uploadZone && audioFileInput) {
            uploadZone.addEventListener('click', () => audioFileInput.click());
            audioFileInput.addEventListener('change', (e) => this.handleFileUpload(e.target.files[0]));
            
            // Drag and drop
            uploadZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadZone.classList.add('dragover');
            });
            
            uploadZone.addEventListener('dragleave', () => {
                uploadZone.classList.remove('dragover');
            });
            
            uploadZone.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadZone.classList.remove('dragover');
                const file = e.dataTransfer.files[0];
                this.handleFileUpload(file);
            });
        }
    }
    
    startRecording() {
        if (!this.recognition) {
            this.showNotification('Speech recognition not available', 'error');
            return;
        }
        
        this.finalTranscript = '';
        this.recognition.start();
        
        // Update UI
        document.getElementById('recordBtn').classList.add('d-none');
        document.getElementById('stopBtn').classList.remove('d-none');
    }
    
    stopRecording() {
        if (this.recognition && this.isRecording) {
            this.recognition.stop();
        }
        
        this.isRecording = false;
        this.hideRecordingStatus();
        
        // Update UI
        document.getElementById('recordBtn').classList.remove('d-none');
        document.getElementById('stopBtn').classList.add('d-none');
        
        if (this.finalTranscript.trim()) {
            this.showTranscriptArea();
        }
    }
    
    showRecordingStatus() {
        document.getElementById('recordingStatus').classList.remove('d-none');
    }
    
    hideRecordingStatus() {
        document.getElementById('recordingStatus').classList.add('d-none');
    }
    
    startRecordingTimer() {
        const timerElement = document.getElementById('recordingTime');
        if (!timerElement) return;
        
        const updateTimer = () => {
            if (!this.isRecording) return;
            
            const elapsed = Date.now() - this.recordingStartTime;
            const minutes = Math.floor(elapsed / 60000);
            const seconds = Math.floor((elapsed % 60000) / 1000);
            
            timerElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            
            // Stop after 3 minutes
            if (elapsed >= 180000) {
                this.stopRecording();
                this.showNotification('Recording stopped after 3 minutes', 'info');
                return;
            }
            
            setTimeout(updateTimer, 1000);
        };
        
        updateTimer();
    }
    
    updateTranscriptDisplay(transcript) {
        const transcriptElement = document.getElementById('transcriptText');
        if (transcriptElement) {
            transcriptElement.textContent = transcript;
            transcriptElement.scrollTop = transcriptElement.scrollHeight;
        }
    }
    
    showTranscriptArea() {
        document.getElementById('transcriptArea').classList.remove('d-none');
    }
    
    async generateSlidesFromTranscript() {
        const transcript = this.finalTranscript.trim();
        
        if (!transcript) {
            this.showNotification('No transcript available', 'error');
            return;
        }
        
        if (transcript.split(' ').length < 10) {
            this.showNotification('Transcript too short. Please provide at least 10 words.', 'error');
            return;
        }
        
        this.showProcessingStatus();
        
        try {
            const response = await fetch('/process_transcript', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ transcript })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('Slides generated successfully!', 'success');
                setTimeout(() => {
                    window.location.href = `/presentation/${result.presentation_id}`;
                }, 1500);
            } else {
                this.hideProcessingStatus();
                this.showNotification(result.error || 'Failed to generate slides', 'error');
            }
            
        } catch (error) {
            console.error('Error generating slides:', error);
            this.hideProcessingStatus();
            this.showNotification('An error occurred while generating slides', 'error');
        }
    }
    
    async handleFileUpload(file) {
        if (!file) return;
        
        // Validate file type
        const allowedTypes = ['audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/m4a', 'audio/webm'];
        if (!allowedTypes.includes(file.type) && !file.name.match(/\.(mp3|wav|ogg|m4a|webm)$/i)) {
            this.showNotification('Please upload a valid audio file (MP3, WAV, OGG, M4A, or WebM)', 'error');
            return;
        }
        
        // Check file size (50MB limit)
        if (file.size > 50 * 1024 * 1024) {
            this.showNotification('File too large. Please upload a file smaller than 50MB', 'error');
            return;
        }
        
        this.showUploadProgress();
        
        const formData = new FormData();
        formData.append('audio_file', file);
        
        try {
            const response = await fetch('/upload_audio', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('Audio uploaded and processed successfully!', 'success');
                setTimeout(() => {
                    window.location.href = `/presentation/${result.presentation_id}`;
                }, 1500);
            } else {
                this.hideUploadProgress();
                this.showNotification(result.error || 'Failed to process audio file', 'error');
            }
            
        } catch (error) {
            console.error('Error uploading file:', error);
            this.hideUploadProgress();
            this.showNotification('An error occurred while uploading the file', 'error');
        }
    }
    
    showUploadProgress() {
        document.getElementById('uploadProgress').classList.remove('d-none');
    }
    
    hideUploadProgress() {
        document.getElementById('uploadProgress').classList.add('d-none');
    }
    
    showProcessingStatus() {
        document.getElementById('processingStatus').classList.remove('d-none');
        // Scroll to processing status
        document.getElementById('processingStatus').scrollIntoView({ behavior: 'smooth' });
    }
    
    hideProcessingStatus() {
        document.getElementById('processingStatus').classList.add('d-none');
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        notification.style.position = 'fixed';
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.zIndex = '9999';
        notification.style.maxWidth = '400px';
        
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new VoiceToSlidesApp();
});

// Global function for slide navigation (used in slides preview)
function showSlide(slideNumber) {
    // This function is defined in slides_preview.html template
    // It's here as a fallback in case it's needed globally
    console.log('Showing slide:', slideNumber);
}
