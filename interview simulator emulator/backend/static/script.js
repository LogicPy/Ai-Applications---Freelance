// static/script.js

document.addEventListener('DOMContentLoaded', () => {
    const dialogueBox = document.getElementById('dialogue-box');
    const sendButton = document.getElementById('send-button');
    const userInput = document.getElementById('user-input');
    const typingSound = document.getElementById('typing-sound');
    const sendSound = document.getElementById('send-sound');
    const volumeSlider = document.getElementById('volume-slider');

    // Set initial volume based on slider
    typingSound.volume = volumeSlider.value;
    sendSound.volume = volumeSlider.value;

    let isTyping = false;

    // Function to simulate typing
    function typeText(text, speed = 50) {
        return new Promise((resolve) => {
            let i = 0;
            dialogueBox.innerHTML = ''; // Clear previous text
            dialogueBox.classList.add('blinking-cursor');
            isTyping = true;
            typingSound.currentTime = 0; // Reset sound
            typingSound.play();

            const interval = setInterval(() => {
                if (i < text.length) {
                    dialogueBox.innerHTML += text.charAt(i);
                    i++;
                } else {
                    clearInterval(interval);
                    dialogueBox.classList.remove('blinking-cursor');
                    isTyping = false;
                    typingSound.pause();
                    typingSound.currentTime = 0;
                    resolve();
                }
            }, speed);
        });
    }

    // Function to display AI response
    async function displayAIResponse(message) {
        await typeText(message);
    }

    // Function to fetch AI response from backend
    async function fetchAIResponse(userMessage) {
        try {
            const response = await fetch('/get-response', { // Relative URL for Flask
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: userMessage }),
            });

            if (!response.ok) {
                throw new Error(`Error: ${response.statusText}`);
            }

            const data = await response.json();
            return data.response;
        } catch (error) {
            console.error("Failed to fetch AI response:", error);
            return "I'm sorry, but I couldn't process your request.";
        }
    }

    // Event listener for the send button
    sendButton.addEventListener('click', async () => {
        if (isTyping) return; // Prevent sending while typing

        const userResponse = userInput.value.trim();
        if (userResponse === '') return;

        // Play send sound
        sendSound.currentTime = 0;
        sendSound.play();

        // Display user's response
        dialogueBox.innerHTML += `<br><span class="user-text">You: ${userResponse}</span>`;
        userInput.value = '';
        sendButton.disabled = true;
        userInput.disabled = true;

        // Fetch AI response
        const aiResponse = await fetchAIResponse(userResponse);

        // Display AI response with typing effect
        await displayAIResponse(aiResponse);

        sendButton.disabled = false;
        userInput.disabled = false;
    });

    // Allow pressing Enter to send
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendButton.click();
        }
    });

    // Handle volume slider changes
    volumeSlider.addEventListener('input', (e) => {
        const volume = e.target.value;
        typingSound.volume = volume;
        sendSound.volume = volume;
    });

    // Initial AI prompt (optional)
    (async () => {
        const initialPrompt = "Hello! I'm glad you're here for the interview.";
        await displayAIResponse(initialPrompt);
    })();
});
