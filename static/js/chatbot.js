// static/js/chatbot.js
class Chatbot {
    constructor() {
        this.isOpen = false;
        this.init();
    }

    init() {
        this.toggleBtn = document.getElementById('chatbotToggle');
        this.chatbotWindow = document.getElementById('chatbotWindow');
        this.closeBtn = document.getElementById('chatbotClose');
        this.sendBtn = document.getElementById('chatbotSend');
        this.voiceBtn = document.getElementById('chatbotVoice');
        this.input = document.getElementById('chatbotInput');
        this.messagesContainer = document.getElementById('chatbotMessages');

        this.setupEventListeners();
    }

    setupEventListeners() {
        this.toggleBtn.addEventListener('click', () => this.toggleChatbot());
        this.closeBtn.addEventListener('click', () => this.closeChatbot());
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
        this.voiceBtn.addEventListener('click', () => this.startVoiceInput());
    }

    toggleChatbot() {
        this.isOpen = !this.isOpen;
        this.chatbotWindow.style.display = this.isOpen ? 'block' : 'none';
        if (this.isOpen) {
            this.input.focus();
        }
    }

    closeChatbot() {
        this.isOpen = false;
        this.chatbotWindow.style.display = 'none';
    }

    async sendMessage() {
        const message = this.input.value.trim();
        if (!message) return;

        this.addMessage(message, 'user');
        this.input.value = '';

        // Show typing indicator
        this.showTypingIndicator();

        try {
            const response = await fetch('/chatbot', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    context: 'general'
                })
            });

            const data = await response.json();
            this.hideTypingIndicator();

            if (data.success) {
                this.addMessage(data.response, 'bot');
            } else {
                this.addMessage('Sorry, I encountered an error. Please try again.', 'bot');
            }
        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage('Sorry, I m having trouble connecting. Please check your internet connection.', 'bot');
        }
    }

    addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chatbot-message ${sender}-message`;
        messageDiv.textContent = text;
        
        this.messagesContainer.appendChild(messageDiv);
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'chatbot-message bot-message typing-indicator';
        indicator.id = 'typingIndicator';
        indicator.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
        
        this.messagesContainer.appendChild(indicator);
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    hideTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.remove();
        }
    }

    startVoiceInput() {
        if (!('webkitSpeechRecognition' in window)) {
            alert('Voice input is not supported in your browser. Please use Chrome or Edge.');
            return;
        }

        const recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            this.voiceBtn.classList.add('listening');
            this.input.placeholder = 'Listening...';
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            this.input.value = transcript;
            this.voiceBtn.classList.remove('listening');
            this.input.placeholder = 'Ask me about resume building...';
        };

        recognition.onerror = () => {
            this.voiceBtn.classList.remove('listening');
            this.input.placeholder = 'Ask me about resume building...';
        };

        recognition.onend = () => {
            this.voiceBtn.classList.remove('listening');
            this.input.placeholder = 'Ask me about resume building...';
        };

        recognition.start();
    }
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new Chatbot();
});