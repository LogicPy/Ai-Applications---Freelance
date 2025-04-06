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
from typing import Generator, List, Tuple, Any  # THIS IS THE CRUCIAL LINE!
import requests

# Define memory file path
memory_file = os.path.join(Path.home(), ".jarvis_chat_memory.pkl")
sessions_file = os.path.join(Path.home(), ".jarvis_sessions.json")

# Configuration
NOVITA_API_URL = "https://api.novita.ai/v3/openai/chat/completions"
NOVITA_API_KEY = "Your_API_Key"

# Initialize memory
memory = CircularBuffer(capacity=5)
# Add these imports at the top
import uuid
from datetime import datetime

# Add these session management functions
def load_sessions() -> dict:
    """Load all sessions from file"""
    try:
        with open(sessions_file, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"sessions": {}, "current_session": None}

def save_sessions(sessions: dict) -> None:
    """Save sessions to file"""
    with open(sessions_file, 'w') as f:
        json.dump(sessions, f, indent=2)

def create_new_session(sessions: dict, name: str = "New Chat") -> dict:
    """Create a new session"""
    session_id = str(uuid.uuid4())
    sessions["sessions"][session_id] = {
        "name": name,
        "created": datetime.now().isoformat(),
        "last_used": datetime.now().isoformat(),
        "history": []
    }
    sessions["current_session"] = session_id
    return sessions

def delete_session(sessions: dict, session_id: str) -> dict:
    """Delete a session"""
    if session_id in sessions["sessions"]:
        del sessions["sessions"][session_id]
        if sessions["current_session"] == session_id:
            sessions["current_session"] = None
    return sessions

def rename_session(sessions: dict, session_id: str, new_name: str) -> dict:
    """Rename a session"""
    if session_id in sessions["sessions"]:
        sessions["sessions"][session_id]["name"] = new_name
    return sessions

def get_current_session_history(sessions: dict) -> list:
    """Get history for current session"""
    if sessions["current_session"] and sessions["current_session"] in sessions["sessions"]:
        return sessions["sessions"][sessions["current_session"]]["history"]
    return []

def update_current_session_history(sessions: dict, history: list) -> dict:
    """Update history for current session"""
    if sessions["current_session"] and sessions["current_session"] in sessions["sessions"]:
        sessions["sessions"][sessions["current_session"]]["history"] = history
        sessions["sessions"][sessions["current_session"]]["last_used"] = datetime.now().isoformat()
    return sessions
# Core Functions
def save_memory(buffer: CircularBuffer, filename: str) -> None:
    """Save conversation memory to file"""
    with open(filename, 'wb') as f:
        pickle.dump(buffer, f)

def load_memory(filename: str) -> CircularBuffer:
    """Load conversation memory from file"""
    try:
        with open(filename, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return CircularBuffer(capacity=5)

def update_memory(user_msg: str, ai_msg: str) -> None:
    """Update conversation memory with new exchange"""
    memory.add({"role": "user", "content": user_msg})
    memory.add({"role": "assistant", "content": ai_msg})

def chat_with_novita_stream(message: str, history: List[Tuple[str, str]], 
                          system_prompt: str, sessions: dict) -> Generator:
    """Streaming chat function with session support"""
    if not message.strip():
        yield "", history, sessions
        return
    
    # Prepare messages for API
    messages = [{"role": "system", "content": system_prompt}]
    for human, ai in history:
        messages.append({"role": "user", "content": human})
        if ai:
            messages.append({"role": "assistant", "content": ai})
    messages.append({"role": "user", "content": message})
    
    # API payload
    payload = {
        "model": "deepseek/deepseek-v3-turbo",
        "messages": messages,
        "temperature": 0.7,
        "stream": True
    }
    
    headers = {
        "Authorization": f"Bearer {NOVITA_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream"
    }
    
    try:
        full_response = ""
        with requests.post(NOVITA_API_URL, json=payload, headers=headers, stream=True) as response:
            if response.status_code != 200:
                error_msg = f"API Error {response.status_code}: {response.text}"
                yield "", history + [(message, error_msg)], sessions
                return
                
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data: ') and decoded_line != 'data: [DONE]':
                        try:
                            data = json.loads(decoded_line[6:])
                            if data.get('choices') and data['choices'][0].get('delta'):
                                content = data['choices'][0]['delta'].get('content', '')
                                if content:
                                    full_response += content
                                    yield "", history + [(message, full_response)], sessions
                        except json.JSONDecodeError:
                            continue
        
        # After stream completes
        if full_response:
            # Update global memory (shared across all sessions)
            update_memory(message, full_response)
            save_memory(memory, memory_file)  # <-- This preserves memory universally
            
            # Update session-specific history
            sessions = update_current_session_history(sessions, history + [(message, full_response)])
            save_sessions(sessions)
            
            yield "", history + [(message, full_response)], sessions
            
    except Exception as e:
        error_msg = f"Connection Error: {str(e)}"
        yield "", history + [(message, error_msg)], sessions


def chat_with_memory(message, history, current_system_prompt, model_choice):
    memory = CircularBuffer(capacity=5)
    
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
    api_key="Your_API_Key"  # Remember to use your actual API key!
)

# 1. FIRST, LET'S UPGRADE YOUR CHAT FUNCTION
  # Stores last 5 exchanges

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
            model="deepseek-ai/DeepSeek-V3-0324-fast",
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
updated_css = avatar_css + ultimate_dark_css + toggle_height_fix

AVAILABLE_MODELS = {
    "DeepSeek v3": "deepseek-ai/DeepSeek-V3-0324-fast",
    "Dolphin Mixtral": "cognitivecomputations/dolphin-2.9.2-mixtral-8x22b"
}

# Create interface with avatar support
# Memory Management Functions
def clear_memory():
    """Clear conversation memory"""
    memory.clear()
    return {"status": "Memory cleared!", "contents": []}

def view_memory():
    """View current memory contents"""
    return {"capacity": memory.capacity, "contents": memory.get_all()}

def save_memory_callback():
    save_memory(memory, memory_file)
    return {"status": "Memory saved!", "contents": []}

def load_memory_callback():
    global memory
    memory = load_memory(memory_file)
    if memory is None:
        memory = CircularBuffer(capacity=5)
    return {"status": "Memory loaded!", "contents": []}

def update_memory_size(size: int):
    """Resize memory buffer"""
    global memory
    memory = CircularBuffer(int(size))
    return {"status": f"Memory resized to {size} slots!", "contents": []}

def append_emoji(emoji: str, current_text: str) -> str:
    """Append selected emoji to message"""
    return current_text + emoji if emji and current_text else current_text or ""

def weigh_memory_importance(memory):
    """Gives higher weight to memories with:"""
    return (
        ("code" in memory["content"]) * 2 +  # Technical discussions
        ("?" in memory["content"]) * 1.5 +   # Questions
        (memory["role"] == "user") * 0.5     # User statements
    )

def get_combined_context(sessions, current_session_id, memory_depth=3):
    """Creates a super-context blending recent memories across sessions"""
    context = []
    
    # Add current session memory
    current_mem = sessions["sessions"][current_session_id].get("memory", [])
    context.extend(current_mem[-memory_depth:])
    
    # Add highlights from other recent sessions
    for session_id, data in sessions["sessions"].items():
        if session_id != current_session_id:
            context.extend(data.get("memory", [])[-1:])  # Just the last exchange
    
    return sorted(context, key=lambda x: x.get("timestamp", 0))[-5:]  # Keep 5 most recent

# Create the interface
with gr.Blocks(title="Wayne's AI Companion", css=updated_css) as demo:
    system_prompt_state = gr.State("You are a helpful AI assistant who enjoys coding in Python.")
    sessions_state = gr.State(load_sessions())

    with gr.Tab("💞 Chat"):
        with gr.Row():
            session_dropdown = gr.Dropdown(
                label="Current Session",
                interactive=True,
                allow_custom_value=False
            )
            new_session_btn = gr.Button("+ New", variant="secondary")
            rename_session_btn = gr.Button("✏️ Rename", variant="secondary")
            delete_session_btn = gr.Button("🗑️ Delete", variant="stop")
        # Chat Interface
        chatbot = gr.Chatbot(
            value=[],
            elem_id="chatbot",
            avatar_images=(
                os.path.join(os.path.dirname(__file__), "user_avatar.png"),
                os.path.join(os.path.dirname(__file__), "bot_avatar.png")
            )
        )
        
        with gr.Row():
            msg = gr.Textbox(placeholder="Type something fun...", container=False)
            with gr.Column(scale=0, min_width=100):
                emoji_selector = gr.Dropdown(
                    choices=COMMON_EMOJIS,
                    label="Add Emoji",
                    allow_custom_value=False
                )
            submit = gr.Button("Send", variant="primary")
        
        # Memory Controls
        with gr.Accordion("Memory Controls", open=False):
            shared_memory = gr.Checkbox(label="Share memory across all sessions", value=True)
            memory_debugger = gr.JSON(
                label="Active Memory Composition",
                value=lambda: {"status": "Select a session first"}
            )
            def update_memory_debugger(sessions):
                if not sessions or not sessions.get("current_session"):
                    return {"status": "No active session"}
                
                return {
                    "current_memory": sessions["sessions"][sessions["current_session"]].get("memory", [])[-3:],
                    "cross_session_memories": get_combined_context(sessions, sessions["current_session"])
                }

            def display_memory(sessions):
                if not sessions.get("current_session"):
                    return gr.Markdown("### ✨ Select a session to see magical memories!")
                
                memories = sessions["sessions"][sessions["current_session"]].get("memory", [])
                return gr.Markdown(
                    "### 🌟 Recent Memories\n" + 
                    "\n".join(f"- {m['content'][:50]}..." for m in memories[-3:]) +
                    "\n\n*Cross-session wisdom active!*" if shared_memory.value else ""
                )

            # Connect it to session changes
            session_dropdown.change(
                update_memory_debugger,
                inputs=[sessions_state],
                outputs=[memory_debugger]
            )

            new_session_btn.click(
                update_memory_debugger,
                inputs=[sessions_state],
                outputs=[memory_debugger]
            )
            with gr.Row():
                clear_mem_btn = gr.Button("Clear Memory")
                view_mem_btn = gr.Button("👀 View Memory")
                save_mem_btn = gr.Button("Save Memory")
                load_mem_btn = gr.Button("Load Memory")
                mem_size = gr.Slider(1, 10, value=5, step=1, label="Memory Slots")

            mem_display = gr.JSON(label="Current Memory")
    with gr.Tab("🛠 System Prompt"):
        system_prompt_box = gr.Textbox(
            label="System Prompt",
            value=system_prompt_state.value,
            lines=5
        )
        system_prompt_box.change(
            lambda x: x,
            inputs=[system_prompt_box],
            outputs=[system_prompt_state]
        )   
            # Model selector
        model_selector = gr.Dropdown(
            choices=["deepseek", "gpt-4o"],
            value="deepseek",
            label="Select Model"
        )

        system_prompt_state.change(
            lambda x: gr.Info(f"System Prompt Updated to: {x}"),
            inputs=[system_prompt_state],
            outputs=[]
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
    
    def update_session_dropdown(sessions):
        session_options = [
            (f"{s['name']} ({datetime.fromisoformat(s['last_used']).strftime('%m/%d %H:%M')}", sid)
            for sid, s in sessions["sessions"].items()
        ]
        return gr.Dropdown(
            choices=session_options,
            value=sessions["current_session"],
            interactive=True
        )
    
    def create_session(sessions):
        sessions = create_new_session(sessions)
        save_sessions(sessions)
        return sessions, update_session_dropdown(sessions), []
    
    def delete_current_session(sessions):
        if sessions["current_session"]:
            sessions = delete_session(sessions, sessions["current_session"])
            save_sessions(sessions)
        return sessions, update_session_dropdown(sessions), []
    
    def rename_current_session(sessions, new_name):
        if sessions["current_session"] and new_name:
            sessions = rename_session(sessions, sessions["current_session"], new_name)
            save_sessions(sessions)
        return sessions, update_session_dropdown(sessions)
    
    def switch_session(sessions, session_id):
        if session_id:
            sessions["current_session"] = session_id
            save_sessions(sessions)
            history = get_current_session_history(sessions)
            return sessions, history
        return sessions, []
    
    # Connect session controls
    demo.load(
        fn=lambda s: update_session_dropdown(s),
        inputs=[sessions_state],
        outputs=[session_dropdown]
    )
    
    new_session_btn.click(
        fn=create_session,
        inputs=[sessions_state],
        outputs=[sessions_state, session_dropdown, chatbot]
    )
    
    delete_session_btn.click(
        fn=delete_current_session,
        inputs=[sessions_state],
        outputs=[sessions_state, session_dropdown, chatbot]
    )
    
    rename_session_btn.click(
        fn=rename_current_session,
        inputs=[sessions_state, gr.Textbox(label="New session name")],
        outputs=[sessions_state, session_dropdown]
    )
    
    session_dropdown.change(
        fn=switch_session,
        inputs=[sessions_state, session_dropdown],
        outputs=[sessions_state, chatbot]
    )
    
    # Update your existing chat function calls to include sessions_state
    
    # Connect components
    msg.submit(
        chat_with_novita_stream,
        [msg, chatbot, system_prompt_state, sessions_state],
        [msg, chatbot, sessions_state]
    )
    
    submit.click(
        chat_with_novita_stream,
        [msg, chatbot, system_prompt_state, sessions_state],
        [msg, chatbot, sessions_state]
    )
    emoji_selector.change(
        append_emoji,
        [emoji_selector, msg],
        msg
    )
    system_prompt_box.change(
        lambda x: x,
        [system_prompt_box],
        [system_prompt_state]
    )
    clear_mem_btn.click(clear_memory, None, mem_display)
    view_mem_btn.click(view_memory, None, mem_display)
    mem_size.change(update_memory_size, mem_size, mem_display)
    clear_mem_btn.click(clear_memory, None, mem_display)
    save_mem_btn.click(save_memory_callback, None, mem_display)
    load_mem_btn.click(load_memory_callback, None, mem_display)
    mem_size.change(update_memory_size, mem_size, mem_display)

if __name__ == "__main__":
    # Load memory at startup
    memory = load_memory(memory_file)
    demo.launch(
        server_name="0.0.0.0",
        server_port=9240,
        auth=("Wayne", "password123!")
    )