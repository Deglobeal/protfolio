// Typing effect for home page
function initTypingEffect() {
    // Check if we're on the home page
    if (!document.getElementById('typing-title')) return;
    
    // Elements to apply typing effect to
    const elements = [
        { id: 'typing-title', text: "Gerard Ugwu", delay: 0, speed: 100 },
        { id: 'typing-subtitle', text: "Welcome to My Page", delay: 1200, speed: 80 },
        { id: 'typing-text1', text: "This is my page. Feel free to look around and leave an Email for positive feedback and updates!", delay: 2500, speed: 30 },
        { id: 'typing-text2', text: "Fiath is a very shy person and doesn't like to talk much, but she is very friendly and loves to help others.", delay: 5500, speed: 30 }
    ];
    
    // Typing effect function
    function typeWriter(element, text, speed, delay, callback) {
        setTimeout(() => {
            let i = 0;
            const interval = setInterval(() => {
                if (i < text.length) {
                    // Handle special case for email link
                    if (text.substr(i, 5) === "Email" && element.id === 'typing-text1') {
                        element.innerHTML += '<a href="/email"><span>Email</span></a>';
                        i += 5;
                    } else {
                        element.innerHTML += text.charAt(i);
                        i++;
                    }
                } else {
                    clearInterval(interval);
                    element.classList.add('typing-complete');
                    if (callback) callback();
                }
            }, speed);
        }, delay);
    }
    
    // Initialize typing for all elements
    elements.forEach(item => {
        const element = document.getElementById(item.id);
        if (element) {
            // Add cursor class initially
            element.classList.add('typing-cursor');
            typeWriter(element, item.text, item.speed, item.delay);
        }
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initTypingEffect);