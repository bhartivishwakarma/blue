// static/js/voice-input.js
class VoiceInputHandler {
    constructor() {
        this.recognition = null;
        this.isListening = false;
        this.currentField = null;
        this.setupSpeechRecognition();
    }

    setupSpeechRecognition() {
        if ('webkitSpeechRecognition' in window) {
            this.recognition = new webkitSpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-IN'; // Indian English

            this.recognition.onstart = () => {
                this.isListening = true;
                this.updateUI('listening');
            };

            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                this.handleSpeechResult(transcript);
            };

            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.handleSpeechError(event.error);
            };

            this.recognition.onend = () => {
                this.isListening = false;
                this.updateUI('stopped');
            };
        } else {
            console.warn('Speech recognition not supported in this browser');
        }
    }

    startListening(fieldElement) {
        if (!this.recognition) {
            alert('Voice input is not supported in your browser. Please use Chrome or Edge.');
            return;
        }

        if (this.isListening) {
            this.stopListening();
            return;
        }

        this.currentField = fieldElement;
        
        try {
            this.recognition.start();
        } catch (error) {
            console.error('Error starting speech recognition:', error);
            this.showMessage('Error starting voice input. Please try again.', 'error');
        }
    }

    stopListening() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
        }
    }

    handleSpeechResult(transcript) {
        if (!this.currentField) return;

        const textInput = this.currentField.querySelector('input, textarea');
        const voiceInput = this.currentField.querySelector('input[type="hidden"]');
        
        if (textInput && voiceInput) {
            textInput.value = transcript;
            voiceInput.value = transcript;
            
            // Auto-enhance the text
            this.enhanceText(transcript, textInput.name)
                .then(enhancedText => {
                    if (enhancedText && enhancedText !== transcript) {
                        textInput.value = enhancedText;
                        voiceInput.value = enhancedText;
                        this.showMessage('Text enhanced using AI', 'success');
                    }
                })
                .catch(error => {
                    console.error('Text enhancement failed:', error);
                });
        }

        this.showMessage('Voice input captured successfully', 'success');
    }

    handleSpeechError(error) {
        let message = 'Voice input failed. ';
        
        switch (error) {
            case 'no-speech':
                message += 'No speech was detected.';
                break;
            case 'audio-capture':
                message += 'No microphone was found.';
                break;
            case 'not-allowed':
                message += 'Microphone permission was denied.';
                break;
            default:
                message += 'Please try again.';
        }
        
        this.showMessage(message, 'error');
    }

    async enhanceText(text, fieldName) {
        try {
            const response = await fetch('/voice-input', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    field_name: fieldName
                })
            });

            const data = await response.json();
            
            if (data.success && data.enhanced_text) {
                return data.enhanced_text;
            } else if (data.error) {
                throw new Error(data.error);
            }
            
            return text; // Return original if enhancement fails
        } catch (error) {
            console.error('Text enhancement error:', error);
            return text; // Return original text on error
        }
    }

    updateUI(state) {
        if (!this.currentField) return;

        const button = this.currentField.querySelector('.voice-btn');
        if (!button) return;

        switch (state) {
            case 'listening':
                button.classList.add('listening');
                button.innerHTML = '<i class="fas fa-stop"></i>';
                button.title = 'Click to stop listening';
                break;
            case 'stopped':
                button.classList.remove('listening');
                button.innerHTML = '<i class="fas fa-microphone"></i>';
                button.title = 'Click to start voice input';
                break;
        }
    }

    showMessage(message, type) {
        // Use the main app's toast system if available
        if (window.blueCollarApp && window.blueCollarApp.showToast) {
            window.blueCollarApp.showToast(message, type);
        } else {
            // Fallback simple notification
            console.log(`${type}: ${message}`);
        }
    }

    // Initialize voice buttons on page
    initVoiceButtons() {
        document.addEventListener('click', (e) => {
            if (e.target.closest('.voice-btn')) {
                const button = e.target.closest('.voice-btn');
                const fieldContainer = button.closest('.form-group');
                
                if (fieldContainer) {
                    this.startListening(fieldContainer);
                }
            }
        });

        // Add keyboard shortcut (Ctrl+Space) for voice input
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.code === 'Space') {
                e.preventDefault();
                const activeElement = document.activeElement;
                const fieldContainer = activeElement.closest('.form-group');
                
                if (fieldContainer && fieldContainer.querySelector('.voice-btn')) {
                    this.startListening(fieldContainer);
                }
            }
        });
    }
}

// Initialize voice input when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.voiceInputHandler = new VoiceInputHandler();
    window.voiceInputHandler.initVoiceButtons();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VoiceInputHandler;
}