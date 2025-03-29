import gradio as gr
from openai import OpenAI
import os
from circular_buffer import CircularBuffer
import numpy as np
import gradio as gr
from random import choice
import pickle
from pathlib import Path
import json
import time

# Define memory file path
memory_file = os.path.join(Path.home(), ".jarvis_chat_memory.pkl")

def save_memory(buffer, filename):
    with open(filename, 'wb') as f:
        pickle.dump(buffer, f)

def load_memory(filename):
    try:
        with open(filename, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None

def chat_with_memory(message, history, current_system_prompt, model_choice):
    if history is None:
        history = []
    
    message = str(message or "").strip()
    current_system_prompt = str(current_system_prompt or "You are a helpful AI assistant.").strip()
    
    if message:
        memory.add({"role": "user", "content": message})
    
    try:
        api_messages = [{"role": "system", "content": current_system_prompt}]
        api_messages.extend([msg for msg in memory.get_all() if msg and "role" in msg and "content" in msg])
        
        # Use the selected model from the dropdown
        model = AVAILABLE_MODELS.get(model_choice, "cognitivecomputations/dolphin-2.9.2-mixtral-8x22b")  # Default to Llama if invalid
        completion = client.chat.completions.create(
            model=model,
            messages=api_messages,
            temperature=0.6
        )
        
        ai_response = completion.choices[0].message.content
        memory.add({"role": "assistant", "content": ai_response})
        save_memory(memory, memory_file)
        
        updated_history = []
        for item in history:
            if isinstance(item, dict) and "role" in item and "content" in item:
                updated_history.append(item)
        if message:
            updated_history.append({"role": "user", "content": message})
            updated_history.append({"role": "assistant", "content": ai_response})
        
        return "", updated_history
    
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        updated_history = history + [{"role": "user", "content": message}, {"role": "assistant", "content": error_msg}]
        return "", updated_history


# Configure the client
client = OpenAI(
    base_url="https://api.studio.nebius.ai/v1/",
    api_key=""  # Remember to use your actual API key!
)

# 1. FIRST, LET'S UPGRADE YOUR CHAT FUNCTION
memory = CircularBuffer(capacity=5)  # Stores last 5 exchanges

# 5. MEMORY VISUALIZATION CSS
memory_css = """
/* Beautiful memory panel */
.accordion-title {
    font-weight: bold !important;
    color: var(--primary-color) !important;
}

.memory-json {
    background: rgba(245, 245, 245, 0.8) !important;
    border-radius: 8px !important;
    padding: 10px !important;
}

.dark .memory-json {
    background: rgba(30, 30, 30, 0.8) !important;
}
"""

def chat_with_ai(message, history):
    """Your AI conversation function - now returns both message and history"""
    messages = [{"role": "system", "content": "You are an AI assistant with a warm, thoughtful demeanor."}]
    
    # Convert Gradio history format to API format
    for human, ai in history:
        messages.extend([
            {"role": "user", "content": human},
            {"role": "assistant", "content": ai}
        ])
    
    messages.append({"role": "user", "content": message})
    
    try:
        completion = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3-0324",
            messages=messages,
            temperature=0.6
        )
        ai_response = completion.choices[0].message.content
        
        # Return BOTH: (empty string to clear input, updated chat history)
        return "", history + [[message, ai_response]]
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        return "", history + [[message, error_msg]]

# Custom CSS with avatar support
# Updated CSS with larger avatars and perfect spacing
avatar_css = """
:root {
    --avatar-size: 60px;  /* 50% larger than default */
    --avatar-spacing: 75px; /* Matching increased spacing */
}

.avatar-container.svelte-yaaj3 {
    width: 120px !important;  
    height: 120px !important;
    /* Let's add these for perfection: */
    min-width: unset !important;  /* Prevents odd resizing */
    border-radius: 20% !important; /* Soft modern shape */
    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1)) !important;
}

/* Small (for compact chats) */
.avatar-sm.svelte-yaaj3 {
    width: 80px !important;
    height: 80px !important;
}
# Ultra-Responsive Avatar CSS (Add this to your styles)
/* Base avatar style - your perfect discovery! */

.avatar-container.svelte-yaaj3 {
    width: clamp(80px, 12vw, 160px) !important; /* Min:80px, Ideal:12% of viewport, Max:160px */
    height: clamp(80px, 12vw, 160px) !important;
    aspect-ratio: 1/1 !important; /* Perfect squares always */
    transition: all 0.3s ease !important;
}

/* Mobile-first adjustments */
@media (max-width: 768px) {
    .avatar-container.svelte-yaaj3 {
        width: clamp(60px, 10vw, 100px) !important;
        height: clamp(60px, 10vw, 100px) !important;
    }
    .message.svelte-1q6z5rm {
        padding-left: clamp(80px, 15vw, 120px) !important;
    }
}

/* Dynamic message spacing */
.message.svelte-1q6z5rm {
    padding-left: clamp(100px, 15vw, 180px) !important;
    min-height: clamp(90px, 13vw, 170px) !important;
}

/* Avatar quality enhancement */
.avatar-container.svelte-yaaj3 img {
    object-fit: cover;
    object-position: center;
    filter: brightness(1.02) contrast(1.05); /* Crispness boost */
}
/* For the avatar IMAGE inside the container */
.avatar-container.svelte-yaaj3 img {
    object-fit: cover !important;  /* Prevents stretching */
    transition: transform 0.3s ease !important;  /* For hover effects */
}

/* Gentle hover animation */
.avatar-container.svelte-yaaj3:hover img {
    transform: scale(1.05) !important;
}

/* Adjust message spacing to match */
.message.svelte-1q6z5rm {
    padding-left: 140px !important;  /* 120px avatar + 20px gap */
    min-height: 130px !important;    /* Taller bubbles */
}

.dark .avatar-container.svelte-yaaj3 {
    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3)) !important;
    border: 2px solid #4a4a4a !important;
}

/* Medium (your chosen size) */
.avatar-md.svelte-yaaj3 {
    width: 120px !important;
    height: 120px !important;
}

/* Large (for emphasis) */
.avatar-lg.svelte-yaaj3 {
    width: 160px !important;
    height: 160px !important;
}

/* Target ONLY the avatar images */
.gradio-chatbot .message .avatar img {
    width: 60px !important;      /* 50% larger */
    height: 60px !important;
    min-width: 60px !important;  /* Prevent squishing */
}

/* Adjust message padding to accommodate larger avatars */
.gradio-chatbot .message {
    padding-left: 80px !important;  /* More space for bigger avatar */
    min-height: 70px !important;    /* Taller messages */
    position: relative !important;
}

/* Position the avatar container */
.gradio-chatbot .message .avatar {
    position: absolute !important;
    left: 10px !important;
    top: 10px !important;
    width: 60px !important;
}

/* Keep your beautiful bubble styles intact */
.gradio-chatbot .message.user {
    background: #f1f3f5 !important;
    border: 1px solid #e9ecef !important;
}

.gradio-chatbot .message.bot {
    background: #ffffff !important;
    border: 1px solid #dee2e6 !important;
}

/* Keep all your existing beautiful styles */
.gradio-container {
    background: linear-gradient(to bottom, #ffffff, #f8f9fa) !important;
    font-family: 'Segoe UI', system-ui, sans-serif !important;
}

# If using base64 avatars from earlier, increase their resolution:
def create_avatar(text, bg_color, size=150):  # 50% larger canvas
    img = Image.new('RGB', (size, size), bg_color)
    d = ImageDraw.Draw(img)
    d.text((size//4, size//4), text[:1].upper(), fill="white", font_size=size//2)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode()

.gradio-container {
    background: linear-gradient(to bottom, #ffffff, #f8f9fa) !important;
    font-family: 'Segoe UI', system-ui, sans-serif !important;
}

.message.user {
    background: #f1f3f5 !important;
    border: 1px solid #e9ecef !important;
    padding-left: 60px !important;
    background-image: var(--user-avatar) !important;
    background-size: 40px !important;
    background-repeat: no-repeat !important;
    background-position: 10px center !important;
    min-height: 50px !important;
}

.message.bot {
    background: #ffffff !important;
    border: 1px solid #dee2e6 !important;
    padding-left: 60px !important;
    background-image: var(--bot-avatar) !important;
    background-size: 40px !important;
    background-repeat: no-repeat !important;
    background-position: 10px center !important;
    min-height: 50px !important;
}

/* Rest of your existing CSS */
.chatbot {
    background-color: #ffffff !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
}
.textbox {
    border: 1px solid #e9ecef !important;
    background: #ffffff !important;
}
.button-primary {
    background: red !important;
    border: none !important;
    color: white !important;
}

/* Gentle pulse animation when receiving messages */
@keyframes gentlePulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.03); }
    100% { transform: scale(1); }
}

.new-message .avatar-container.svelte-yaaj3 {
    animation: gentlePulse 0.6s ease;
}

/* Dynamic border color based on message type */
.message.user .avatar-container.svelte-yaaj3 {
    border: 2px solid #e1bee7 !important; /* Soft purple */
}

.message.bot .avatar-container.svelte-yaaj3 {
    border: 2px solid #bbdefb !important; /* Soft blue */
}

# Add this to your existing CSS
/* Beautiful toggle switch */
.theme-toggle {
    position: absolute !important;
    top: 15px !important;
    right: 15px !important;
    z-index: 1000 !important;
}

.primary.svelte-1ixn6qd, .lg.svelte-1ixn6qd, button
{
    /* Button color setup */
}

/* 1. TARGET GRADIO'S BUTTON STRUCTURE */
button.gradio-button {
    background-color: #ff0000 !important;
    border: 2px solid darkred !important;
}

/* 2. HOVER/FOCUS STATES */
button.gradio-button:hover {
    background-color: #cc0000 !important;
    transform: translateY(-1px) !important;
}

/* 3. ACTIVE STATE */
button.gradio-button:active {
    background-color: #aa0000 !important;
    transform: translateY(1px) !important;
}

/* 4. SPECIFIC BUTTON TYPES */
button.primary {
    background-color: linear-gradient(to right, #ff0000, #cc0000) !important;
}

/* 5. DARK MODE ADAPTATION */
.dark button.gradio-button {
    background-color: #990000 !important;
    box-shadow: 0 0 10px rgba(255,0,0,0.5) !important;
}

.theme-toggle .toggle-container {
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
}

.toggle-label {
    font-family: 'Segoe UI', sans-serif !important;
    font-size: 14px !important;
    color: var(--text-color) !important;
    cursor: pointer !important;
}

.toggle-switch {
    position: relative !important;
    width: 50px !important;
    height: 24px !important;
    background: #e0e0e0 !important;
    border-radius: 12px !important;
    transition: all 0.3s ease !important;
    cursor: pointer !important;
}

.toggle-switch:after {
    content: '' !important;
    position: absolute !important;
    width: 20px !important;
    height: 20px !important;
    border-radius: 50% !important;
    background: white !important;
    top: 2px !important;
    left: 2px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.2) !important;
}

.dark .toggle-switch {
    background: #424242 !important;
}

.dark .toggle-switch:after {
    left: 28px !important;
    background: #212121 !important;
}

/* System-aware theming */
@media (prefers-color-scheme: dark) {
    :root {
        --text-color: #f5f5f5 !important;
    }
    .toggle-switch {
        background: #424242 !important;
    }
    .toggle-switch:after {
        background: #212121 !important;
    }
}

@media (prefers-color-scheme: light) {
    :root {
        --text-color: #212121 !important;
    }
}

.logo {
  background: linear-gradient(45deg, #00fffc, #ff00f7, #00fffc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: shine 3s infinite alternate;
}
@keyframes shine {
  0% { opacity: 0.8; }
  100% { opacity: 1; text-shadow: 0 0 20px #00f7ff; }
}
"""
# 1. FIRST UPDATE YOUR CSS (add/replace these sections)
ultimate_dark_css = """
:root {
    --light-bg: #f8f9fa;
    --light-text: #212529;
    --dark-bg: #1a1a1a;
    --dark-text: #e9ecef;
    --dark-secondary: #2d2d2d;
    --dark-accent: #3a3a3a;
}

/* System-wide dark mode */
.dark .gradio-container {
    background: var(--dark-bg) !important;
    color: var(--dark-text) !important;
}

.dark .chatbot {
    background: var(--dark-secondary) !important;
    border-color: var(--dark-accent) !important;
}

.dark .message.user {
    background: var(--dark-accent) !important;
    color: var(--dark-text) !important;
    border-color: #444 !important;
}

.dark .message.bot {
    background: var(--dark-secondary) !important;
    color: var(--dark-text) !important;
}

.dark .textbox {
    background: var(--dark-secondary) !important;
    color: var(--dark-text) !important;
    border-color: var(--dark-accent) !important;
}

.dark .button-primary {
    background: linear-gradient(to right, #5a6268, #343a40) !important;
}

/* Avatar adjustments for dark mode */
.dark .avatar-container.svelte-yaaj3 img {
    filter: brightness(0.9) contrast(1.1);
}

/* Settings panel dark mode */
.dark .panel {
    background: var(--dark-secondary) !important;
    border-color: var(--dark-accent) !important;
}
"""

# Add this to your existing CSS
theme_toggle_css = """
/* Beautiful toggle switch */
.theme-toggle {
    position: absolute !important;
    top: 15px !important;
    right: 15px !important;
    z-index: 1000 !important;
}

.theme-toggle .toggle-container {
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
}

.toggle-label {
    font-family: 'Segoe UI', sans-serif !important;
    font-size: 14px !important;
    color: var(--text-color) !important;
    cursor: pointer !important;
}

.toggle-switch {
    position: relative !important;
    width: 50px !important;
    height: 24px !important;
    background: #e0e0e0 !important;
    border-radius: 12px !important;
    transition: all 0.3s ease !important;
    cursor: pointer !important;
}

.toggle-switch:after {
    content: '' !important;
    position: absolute !important;
    width: 20px !important;
    height: 20px !important;
    border-radius: 50% !important;
    background: white !important;
    top: 2px !important;
    left: 2px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.2) !important;
}

.dark .toggle-switch {
    background: #424242 !important;
}

.dark .toggle-switch:after {
    left: 28px !important;
    background: #212121 !important;
}

/* System-aware theming */
@media (prefers-color-scheme: dark) {
    :root {
        --text-color: #f5f5f5 !important;
    }
    .toggle-switch {
        background: #424242 !important;
    }
    .toggle-switch:after {
        background: #212121 !important;
    }
}

@media (prefers-color-scheme: light) {
    :root {
        --text-color: #212121 !important;
    }
}
"""
    
# Add this to your existing CSS
toggle_height_fix = """
/* Desktop-specific height boost */
@media (min-width: 769px) {
    #component-4.toggle-label.svelte-11xb1hd {
        min-height: 48px !important;  /* Doubled from default */
        display: flex !important;
        align-items: center !important;
    }
    
    /* Make the icon larger too */
    #component-4 .iconify {
        width: 24px !important;
        height: 24px !important;
        margin-right: 8px !important;
    }
    
    /* Adjust text sizing */
    #component-4 label.svelte-i3tvor {
        font-size: 16px !important;
        padding: 12px 0 !important;
    }
}

/* Mobile remains compact */
@media (max-width: 768px) {
    #component-4.toggle-label {
        min-height: 32px !important;
    }
}
"""

fixed_css = """
/* Force light mode when .dark class is absent */
.gradio-container:not(.dark) {
    background: var(--light-bg) !important;
    color: var(--light-text) !important;
}

/* Explicit light mode styles */
.light .chatbot {
    background: white !important;
    border-color: #e9ecef !important;
}

.light .message.user {
    background: #f1f3f5 !important;
    color: #212529 !important;
}

.light .textbox {
    background: white !important;
    color: #000 !important;
}
"""

emoji_css = """
/* Emoji Picker Styles */
#emoji-picker {
  position: relative;
  display: inline-block;
}
#emoji-button {
  background: transparent;
  border: none;
  font-size: 1.5em;
  cursor: pointer;
  padding: 0 10px;
}
#emoji-list {
  display: none;
  position: absolute;
  bottom: 100%;
  left: 0;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 10px;
  width: 200px;
  max-height: 300px;
  overflow-y: auto;
  z-index: 1000;
}
#emoji-list.show {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 5px;
}
#emoji-list span {
  cursor: pointer;
  font-size: 1.2em;
  padding: 5px;
}
#emoji-list span:hover {
  transform: scale(1.2);
}
.dark #emoji-list {
  background: #2d2d2d;
  border-color: #444;
}
#emoji-list {
  display: none;
  /* ... other styles ... */
}
#emoji-list.show {
  display: grid;
}

"""
# Add these imports if not already present

# Add this emoji list (you can expand it as needed)
COMMON_EMOJIS = [
    "😊", "😂", "❤️", "👍", "😢", "😡", "🎉", "✨", "🤔", "🤪",
    "😍", "👋", "🚀", "🌈", "🎈", "💡", "🙌", "🌟", "🍕", "🐱"
]

# Update your CSS by adding this to your existing emoji_css
emoji_css = """
#emoji-picker {
    position: relative;
    display: inline-block;
    margin-left: 10px;
}
#emoji-button {
    background: transparent;
    border: none;
    font-size: 1.5em;
    cursor: pointer;
    padding: 5px;
    transition: transform 0.2s;
}
#emoji-button:hover {
    transform: scale(1.2);
}
#emoji-list {
    display: none;
    position: absolute;
    bottom: 100%;
    left: 0;
    background: white;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 10px;
    width: 200px;
    max-height: 300px;
    overflow-y: auto;
    z-index: 1000;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}
#emoji-list.show {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 5px;
}
#emoji-list span {
    cursor: pointer;
    font-size: 1.5em;
    padding: 5px;
    text-align: center;
}
#emoji-list span:hover {
    background: #f0f0f0;
    border-radius: 4px;
}
.dark #emoji-list {
    background: #2d2d2d;
    border-color: #444;
}
.dark #emoji-list span:hover {
    background: #3a3a3a;
}
"""

# Add this JavaScript function
def get_emoji_js():
    return """
    <script>
    // Ensure the script runs after DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        // Define all functions in global scope
        window.toggleEmojiPicker = function() {
            const emojiList = document.getElementById('emoji-list');
            if (emojiList) {
                emojiList.classList.toggle('show');
            }
        }

        window.addEmoji = function(emoji) {
            const textbox = document.querySelector('.gradio-textbox input');
            if (textbox) {
                textbox.value += emoji;
                textbox.focus();
                textbox.dispatchEvent(new Event('input'));
            }
            const emojiList = document.getElementById('emoji-list');
            if (emojiList) {
                emojiList.classList.remove('show');
            }
        }

        // Close emoji picker when clicking outside
        document.addEventListener('click', function(event) {
            const picker = document.getElementById('emoji-picker');
            if (picker && !picker.contains(event.target)) {
                const emojiList = document.getElementById('emoji-list');
                if (emojiList) {
                    emojiList.classList.remove('show');
                }
            }
        });
    });
    </script>
    """

emoji_js = """
document.addEventListener('DOMContentLoaded', function() {
    console.log('Emoji JS loaded'); // Debug to confirm loading
    
    window.toggleEmojiPicker = function() {
        console.log('ToggleEmojiPicker called'); // Debug click
        const emojiList = document.getElementById('emoji-list');
        if (emojiList) {
            emojiList.classList.toggle('show');
        } else {
            console.log('Emoji list not found');
        }
    }

    window.addEmoji = function(emoji) {
        console.log('Adding emoji:', emoji); // Debug emoji selection
        const textbox = document.querySelector('.gradio-textbox input');
        if (textbox) {
            textbox.value += emoji;
            textbox.focus();
            textbox.dispatchEvent(new Event('input'));
        }
        const emojiList = document.getElementById('emoji-list');
        if (emojiList) {
            emojiList.classList.remove('show');
        }
    }

    document.addEventListener('click', function(event) {
        const picker = document.getElementById('emoji-picker');
        if (picker && !picker.contains(event.target)) {
            const emojiList = document.getElementById('emoji-list');
            if (emojiList) {
                emojiList.classList.remove('show');
            }
        }
    });
});
"""

# Modify your chat interface section

def update_theme(dark_mode):
    # 1. Update HTML class
    js = f"""
    document.body.classList.toggle('dark', {str(dark_mode).lower()});
    document.body.classList.toggle('light', {str(not dark_mode).lower()});
    """
    
    # 2. Update Gradio theme
    theme = gr.themes.Default(
        primary_hue="blue",
        neutral_hue="slate" if dark_mode else "gray"
    ).set(
        body_background_fill="var(--dark-bg)" if dark_mode else "var(--light-bg)",
        chatbot_background_color="var(--dark-secondary)" if dark_mode else "white"
    )
    
    # 3. Force refresh all components
    return theme, gr.update(visible=True), js

def flip_text(x):
    flips = ["(◕‿◕)┌∩┐", "(╯°□°)╯︵ ┻━┻", "︵‿︵‿୨♡୧‿︵‿︵"]
    return f"{x[::-1]} {choice(flips)}"

def flip_image(x):
    return np.fliplr(x), gr.update(value="https://i.imgur.com/KfZPvFn.gif", visible=True)

def stream_chars(message, history):
    response = ""
    for char in "This is a streaming test response...":
        response += char
        time.sleep(0.05)  # Adjust typing speed
        yield "", history + [[message, response]]


def sync_with_settings():
    return """
    <script>
    // DEBUG MODE - Uncomment to make emoji list permanently visible
    // document.getElementById('emoji-list').style.display = 'grid !important';
    // document.getElementById('emoji-list').style.opacity = '1 !important';
    // document.getElementById('emoji-list').style.visibility = 'visible !important';
    
    function showEmojiPicker() {
        const list = document.getElementById('emoji-list');
        if (!list) return;
        
        // Nuclear visibility (overrides everything)
        list.style.cssText = `
            display: grid !important;
            opacity: 1 !important;
            visibility: visible !important;
            position: absolute !important;
            z-index: 9999 !important;
            background: red !important;  /* Debug color */
        `;
    }
    </script>
    """
    
COMMON_EMOJIS = ["😀", "😂", "😍", "🤔", "😎", "🥳", "😴", "🥰", "🤩", "🥳", "👏" , "🙂", "😊", "👍", "👌", "✅", "❤️", "💙", "💜", "💚", "🧡", "💛", "🤍", "🧠"]

updated_css = avatar_css + ultimate_dark_css + toggle_height_fix  # No need for emoji_css

AVAILABLE_MODELS = {
    "deepseek": "deepseek-ai/DeepSeek-V3-0324",
    "gpt-4o": "gpt-4o",
    "dolphin mixtral": "meta-llama/Meta-Llama-3.1-70B-Instruct"
}

# Link the send button to the send_message function
# Create interface with avatar support
with gr.Blocks(css=updated_css) as demo:   
    system_prompt_state = gr.State("You are a helpful AI assistant.")
    
    system_prompt_state = gr.Textbox(
        label="System Prompt",
        lines=3,
        value="You are a helpful AI assistant who enjoys coding in Python with the user...",
        visible=False
    )
        
    with gr.Tab("💞 Chat"):
        chatbot = gr.Chatbot(
            value=[],  # Initialize empty
            elem_id="chatbot",
            show_label=False,  # Optional: adds like/dislike buttons
            layout="panel",  # Better mobile rendering
            type="messages",
            avatar_images=(
                os.path.join(os.path.dirname(__file__), "user_avatar.png"),
                os.path.join(os.path.dirname(__file__), "bot_avatar.png")
            )
        )       

        with gr.Row():
            msg = gr.Textbox(placeholder="Type something fun...", container=False)
        
        # Bind the submit actions
            with gr.Column(scale=1, min_width=100):
                # New Gradio Dropdown for emoji selection
                emoji_selector = gr.Dropdown(
                    choices=COMMON_EMOJIS,
                    label="Add an Emoji",
                    value=None,  # Start with no selection
                    allow_custom_value=False
                )
            with gr.Column(scale=1, min_width=50):
                submit = gr.Button("Send", variant="primary")

        # Model selector
        model_selector = gr.Dropdown(
            choices=list(AVAILABLE_MODELS.keys()),
            value="deepseek",  # Default to Llama
            label="Select Model",
            interactive=True  # Explicitly enable interaction
        )

        # Function to handle emoji selection and append to textbox
        def append_emoji(emoji, current_text):
            if emoji and current_text is not None:
                return current_text + emoji
            return current_text or ""
        
        emoji_selector.change(
            fn=append_emoji,
            inputs=[emoji_selector, msg],
            outputs=msg
        )
        
        msg.submit(
            fn=chat_with_memory,
            inputs=[msg, chatbot, system_prompt_state, model_selector],
            outputs=[msg, chatbot]
        )
        submit.click(
            fn=chat_with_memory,
            inputs=[msg, chatbot, system_prompt_state, model_selector],
            outputs=[msg, chatbot]
        )
        
        system_prompt_state.change(
            lambda x: gr.Info(f"System Prompt Updated to: {x}"),
            inputs=[system_prompt_state],
            outputs=[]
        )
        gr.Examples(
            examples=[
                ["Can you show me a Python 'hello world' please?"],
                ["How far away is Mars from Earth?"],
                ["How many carbon atoms are in human beings?"],
                ["Can you replace carbon with silicon in biology?"],
            ],
            inputs=msg
        )


        with gr.Accordion("Memory Controls", open=False):
            with gr.Row():
                clear_mem_btn = gr.Button(" Clear Memory")
                view_mem_btn = gr.Button("👀 View Memory")
                save_mem_btn = gr.Button("Save Memory")
                load_mem_btn = gr.Button("Load Memory")
                mem_size = gr.Slider(1, 10, value=5, step=1, label="Memory Slots")

            mem_display = gr.JSON(label="Current Memory")

        
        # 3. MEMORY MANAGEMENT FUNCTIONS


        def clear_memory():
            confirm_clear = gr.Confirmation("Confirm Clear Memory", "Are you sure you want to clear the memory?")
            if confirm_clear:
                save_before_clear = gr.Confirmation("Save Before Clear", "Do you want to save the memory before clearing?")
                if save_before_clear:
                    save_memory(memory, memory_file)
                memory.clear()
            return {"status": "Memory cleared!", "contents": []}
        
        def save_memory_callback():
            save_memory(memory, memory_file)
            return {"status": "Memory saved!", "contents": []}

        def load_memory_callback():
            global memory
            memory = load_memory(memory_file)
            if memory is None:
                memory = CircularBuffer(capacity=5)
            return {"status": "Memory loaded!", "contents": []}
        
        def view_memory():
            return {"capacity": memory.capacity, "contents": memory.get_all()}
        
        def update_memory_size(size):
            global memory
            memory = CircularBuffer(int(size))
            return {"status": f"Memory resized to {size} slots!", "contents": []}
        
        # 4. CONNECT CONTROLS
        clear_mem_btn.click(clear_memory, None, mem_display)
        view_mem_btn.click(view_memory, None, mem_display)
        mem_size.change(update_memory_size, mem_size, mem_display)
        clear_mem_btn.click(clear_memory, None, mem_display)
        save_mem_btn.click(save_memory_callback, None, mem_display)
        load_mem_btn.click(load_memory_callback, None, mem_display)
    
    with gr.Tab("🛠 System Prompt"):
        system_prompt_box = gr.Textbox(
            label="System Prompt",
            value="You are a helpful AI assistant who enjoys coding in Python with the user...",
            lines=5
        )
        system_prompt_box.change(
            lambda x: x,
            inputs=[system_prompt_box],
            outputs=[system_prompt_state]
        )
        
        # Debug button to show current memory
        debug_btn = gr.Button("Show Memory")
        debug_btn.click(
            lambda: print(f"Current Memory: {memory.get_all()}"),
            inputs=[],
            outputs=[]
        )
        # Add this to your interface
        debug_btn2 = gr.Button("Debug Memory")
        debug_btn2.click(
            lambda: [
                print("Raw Memory:", memory.get_all()),
                print("Formatted History:", [
                    [msg.get("content", "") for msg in memory.buffer[i:i+2]] 
                    for i in range(0, len(memory.buffer), 2)
                    if i+1 < len(memory.buffer)
                ])
            ],
            inputs=[],
            outputs=[]
        )
        
    with gr.Tab("🎮 Tetris Zone"):
        # METHOD 1: HTML EMBED (MOST RELIABLE)
        gr.HTML("""
        <iframe src="https://wayne.cool/tetris/" 
                width="100%" 
                height="700"
                style="border:none">
                
        </iframe>
        """)

if __name__ == "__main__":
    # 1. LAUNCH COMMAND THAT SOLVES EVERYTHING
    demo.launch(
        server_name="0.0.0.0",  # Listen on all network interfaces
        server_port=9240,
        share=False,  # Disable ngrok tunnel
        auth=("user", "password")  # Optional security
    )
    # demo.launch(server_name="0.0.0.0", server_port=9240)
