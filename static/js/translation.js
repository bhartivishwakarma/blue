// static/js/translation.js
class TranslationManager {
    constructor() {
        this.currentLanguage = document.documentElement.lang || 'en';
        this.init();
    }

    init() {
        this.setupLanguageSelector();
        this.setupRealTimeTranslation();
    }

    setupLanguageSelector() {
        const selector = document.getElementById('languageSelect');
        if (selector) {
            selector.addEventListener('change', (e) => {
                this.changeLanguage(e.target.value);
            });
        }
    }

    async changeLanguage(languageCode) {
        try {
            const response = await fetch('/change-language', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `language=${languageCode}`
            });

            const data = await response.json();
            
            if (data.success) {
                // Show success message
                this.showMessage(data.message, 'success');
                
                // Reload page to apply translations
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                this.showMessage('Failed to change language', 'error');
            }
        } catch (error) {
            console.error('Language change error:', error);
            this.showMessage('Error changing language', 'error');
        }
    }

    async translateText(text, targetLanguage = null) {
        if (!targetLanguage) {
            targetLanguage = this.currentLanguage;
        }

        if (targetLanguage === 'en' || !text) {
            return text;
        }

        try {
            const response = await fetch('/api/translate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    target_language: targetLanguage
                })
            });

            const data = await response.json();
            
            if (data.success) {
                return data.translated_text;
            } else {
                console.error('Translation failed:', data.error);
                return text;
            }
        } catch (error) {
            console.error('Translation error:', error);
            return text;
        }
    }

    async translateElement(element) {
        const text = element.textContent.trim();
        if (!text) return;

        const translated = await this.translateText(text);
        if (translated !== text) {
            element.textContent = translated;
        }
    }

    setupRealTimeTranslation() {
        // Auto-translate dynamic content
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === 1) { // Element node
                            this.translateDynamicContent(node);
                        }
                    });
                }
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    translateDynamicContent(element) {
        // Translate elements with data-translate attribute
        const translatableElements = element.querySelectorAll('[data-translate]');
        translatableElements.forEach(el => {
            this.translateElement(el);
        });

        // Translate input placeholders
        const inputs = element.querySelectorAll('input[placeholder], textarea[placeholder]');
        inputs.forEach(input => {
            this.translateAttribute(input, 'placeholder');
        });

        // Translate button texts
        const buttons = element.querySelectorAll('button:not([data-no-translate])');
        buttons.forEach(button => {
            this.translateElement(button);
        });
    }

    async translateAttribute(element, attribute) {
        const value = element.getAttribute(attribute);
        if (value) {
            const translated = await this.translateText(value);
            if (translated !== value) {
                element.setAttribute(attribute, translated);
            }
        }
    }

    showMessage(message, type) {
        // Use existing toast system or create simple alert
        if (window.blueCollarApp && window.blueCollarApp.showToast) {
            window.blueCollarApp.showToast(message, type);
        } else {
            alert(message);
        }
    }
}

// Initialize translation manager
document.addEventListener('DOMContentLoaded', () => {
    window.translationManager = new TranslationManager();
});

// Utility function for dynamic translation
async function translate(text) {
    if (window.translationManager) {
        return await window.translationManager.translateText(text);
    }
    return text;
}