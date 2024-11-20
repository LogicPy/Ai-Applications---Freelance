# app.py

from flask import Flask, render_template, request, jsonify
import os
import logging
import uuid
from dotenv import load_dotenv
# app4.py
import logging
from flask import Flask, request, jsonify
import uuid
import logging
from dotenv import load_dotenv
import os
from flask import Flask, request, jsonify
import uuid
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
#from tts import send_tts_request_xtts, send_tts_request_elevenlabs, get_elevenlabs_voices
from tts.elevenlabs import send_tts_request_elevenlabs, get_elevenlabs_voices
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import uuid
import logging
from dotenv import load_dotenv
import os
from flask import Flask, request, jsonify, render_template
import uuid
import logging
from dotenv import load_dotenv
import os
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import uuid
import logging
from dotenv import load_dotenv
import os


# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configure SQLAlchemy
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///chats.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy and Flask-Migrate
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Configure Logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for detailed logs
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app_debug.log"),  # Logs will be saved to app_debug.log
        logging.StreamHandler()  # Also output logs to the console
    ]
)


# Define Models
class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    messages = db.relationship('ChatMessage', backref='chat', lazy=True)

# app.py

# ... [previous code]

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.String(32), db.ForeignKey('chat_sessions.id'), nullable=False)
    sender = db.Column(db.String(10), nullable=False)  # 'user' or 'ai'
    content = db.Column(db.Text, nullable=False)

# Error Handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Routes
@app.route('/')
def index():
    try:
        chats = ChatSession.query.all()
        return render_template('index.html', chats=chats)
    except Exception as e:
        logging.error(f"Error loading index page: {e}")
        return jsonify({'error': 'Failed to load chats.'}), 500

@app.route('/create_chat', methods=['POST'])
def create_chat():
    try:
        data = request.get_json()
        chat_name = data.get('name')

        if not chat_name:
            logging.error("No chat name provided in the request.")
            return jsonify({'success': False, 'error': 'No chat name provided.'}), 400

        # Generate a unique chat ID
        chat_id = uuid.uuid4().hex
        logging.info(f"Created new chat session: {chat_name} with ID: {chat_id}")

        # Create and store the chat session
        new_chat = ChatSession(id=chat_id, name=chat_name)
        db.session.add(new_chat)
        db.session.commit()

        return jsonify({'success': True, 'chat_id': chat_id, 'chat_name': chat_name}), 200
    except Exception as e:
        logging.error(f"Error creating chat: {e}")
        return jsonify({'success': False, 'error': 'Failed to create chat.'}), 500

@app.route('/get_chats', methods=['GET'])
def get_chats():
    try:
        chats = ChatSession.query.all()
        chat_list = [{'id': chat.id, 'name': chat.name} for chat in chats]
        return jsonify({'chats': chat_list}), 200
    except Exception as e:
        logging.error(f"Error fetching chats: {e}")
        return jsonify({'error': 'Failed to fetch chats.'}), 500

@app.route('/get_chat_messages/<chat_id>', methods=['GET'])
def get_chat_messages(chat_id):
    try:
        chat = ChatSession.query.filter_by(id=chat_id).first()
        if not chat:
            logging.error(f"Chat ID {chat_id} not found.")
            return jsonify({'error': 'Chat session not found.'}), 404

        messages = ChatMessage.query.filter_by(chat_id=chat_id).all()
        message_list = [{'sender': msg.sender, 'content': msg.content} for msg in messages]
        return jsonify({'messages': message_list}), 200
    except Exception as e:
        logging.error(f"Error fetching messages for chat {chat_id}: {e}")
        return jsonify({'error': 'Failed to fetch chat messages.'}), 500

@app.route('/chat/<chat_id>', methods=['GET'])
def chat_page(chat_id):
    try:
        chat = ChatSession.query.filter_by(id=chat_id).first()
        if not chat:
            logging.error(f"Chat ID {chat_id} not found.")
            return render_template('404.html'), 404  # Ensure you have a 404.html template

        return render_template('chat.html', chat_id=chat_id)
    except Exception as e:
        logging.error(f"Error loading chat page for {chat_id}: {e}")
        return render_template('500.html'), 500  # Ensure you have a 500.html template

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('prompt')
        chat_id = data.get('chat_id')
        ai_framework = data.get('ai_framework', 'ollama')  # Default to Ollama

        if not user_message:
            logging.error("No message provided in the request.")
            return jsonify({'response': 'No message provided.'}), 400

        chat = ChatSession.query.filter_by(id=chat_id).first()
        if not chat:
            logging.error(f"Chat ID {chat_id} not found.")
            return jsonify({'response': 'Chat session not found.'}), 404

        # Append user message to the chat session
        new_user_message = ChatMessage(chat_id=chat_id, sender='user', content=user_message)
        db.session.add(new_user_message)
        db.session.commit()

        # Generate AI response based on selected framework
        ai_response = generate_ai_response(message=user_message, ai_framework=ai_framework)

        if not ai_response:
            logging.error("Failed to generate AI response.")
            return jsonify({'response': 'Failed to generate AI response.'}), 500

        # Append AI response to the chat session
        new_ai_message = ChatMessage(chat_id=chat_id, sender='ai', content=ai_response)
        db.session.add(new_ai_message)
        db.session.commit()

        return jsonify({'response': ai_response}), 200
    except Exception as e:
        logging.error(f"Error in chat route: {e}")
        return jsonify({'response': 'Failed to send message.'}), 500


def generate_ai_response(message, ai_framework='ollama'):
    """
    Generate AI response using selected framework.

    Args:
        message (str): User message.
        ai_framework (str): AI framework to use ('ollama' or 'openai').

    Returns:
        str: AI response or None.
    """
    if ai_framework == 'ollama':
        return get_ollama_response(message)
    elif ai_framework == 'openai':
        return get_openai_response(message)
    else:
        logging.error(f"Unknown AI framework: {ai_framework}")
        return None

def get_openai_response(message):
    # Implement the function to get OpenAI GPT-4 response
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        logging.error("OpenAI API key not found.")
        return None

    try:
        import openai
        openai.api_key = openai_api_key
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        logging.error(f"Failed to get OpenAI response: {e}")
        return None


def get_ollama_response(message):
    # Implement the function to get Ollama response
    # Replace this with your actual Ollama integration code
    return "This is a response from Ollama."

def get_openai_response(message):
    # Implement the function to get OpenAI GPT-4 response
    # Ensure you have the OpenAI API key set in .env
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        logging.error("OpenAI API key not found.")
        return None

    try:
        import openai
        openai.api_key = openai_api_key
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        logging.error(f"Failed to get OpenAI response: {e}")
        return None


def get_ollama_response(message):
    # Implement the function to get Ollama response
    # Replace this with your actual Ollama integration code
    # For demonstration purposes, returning a static response
    return "This is a response from Ollama."

# Initialize chat sessions and messages storage
app.chat_sessions = []
app.chat_messages = {}  # Dictionary to store messages per chat_id

def generate_ai_response(message, ai_framework='openai'):
    """
    Generate AI response using selected framework.

    Args:
        message (str): User message.
        ai_framework (str): AI framework to use ('openai' or 'ollama').

    Returns:
        str: AI response or None.
    """
    if ai_framework == 'openai':
        return get_gpt4_response(message)
    elif ai_framework == 'ollama':
        return get_ollama_response(message)
    else:
        logging.error(f"Unknown AI framework: {ai_framework}")
        return None

# Define Models
class ChatSession(db.Model):
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    messages = db.relationship('ChatMessage', backref='chat', lazy=True)

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.String(32), db.ForeignKey('chat_session.id'), nullable=False)
    sender = db.Column(db.String(10), nullable=False)  # 'user' or 'ai'
    content = db.Column(db.Text, nullable=False)

# Create the database tables
with app.app_context():
    db.create_all()

# Initialize chat sessions storage
app.chat_sessions = []

# Configure logging at the beginning of your app.py
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to capture detailed logs
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app_debug.log"),  # Logs will be saved to app_debug.log
        logging.StreamHandler()  # Also output logs to the console
    ]
)

from flask import Flask, render_template, request, jsonify
import os
import logging
import uuid
from dotenv import load_dotenv
from ai_responses.openai_gpt4 import get_gpt4_response
from ai_responses.ollama import get_ollama_response

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define output directory for audio files
OUTPUT_DIR = os.path.join(app.root_path, "static", "audio")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Import modularized components
from audio_effects.effects import apply_reverb_effect, apply_giantess_echo_effect
from utils.emotion import detect_emotion
from utils.helpers import generate_unique_filename, escape_html

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define output directory for audio files
OUTPUT_DIR = os.path.join(app.root_path, "static", "audio")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Import modularized components
#from tts import send_tts_request_xtts, send_tts_request_elevenlabs, get_elevenlabs_voices
from ai_responses.openai_gpt4 import get_gpt4_response
from ai_responses.ollama import get_ollama_response
from audio_effects.effects import apply_reverb_effect, apply_giantess_echo_effect
from utils.emotion import detect_emotion
from utils.helpers import generate_unique_filename, escape_html

# Placeholder AI name
AI_NAME = "Jarvis"


@app.route('/generate_tts', methods=['POST'])
def generate_tts():
    data = request.get_json()
    text = data.get('text')
    tts_service = data.get('tts_service')
    ai_framework = data.get('ai_framework', 'openai')  # Default to OpenAI

    if not text:
        return jsonify({'error': 'No text provided.'}), 400

    # Detect emotion from the text
    detected_emotion = detect_emotion(text)
    logging.info(f"Detected emotion: {detected_emotion}")

    # Define character profiles based on emotion or predefined
    character_profiles = {
        "Default": {"pitch": 1.0, "speed": 1.0, "tone": "neutral", "emotion": "neutral", "gender": "female", "age": "adult"},
        "Narrator": {"pitch": 1.0, "speed": 0.9, "tone": "calm", "emotion": "calm", "gender": "male", "age": "senior"},
        "Energetic": {"pitch": 1.2, "speed": 1.1, "tone": "bright", "emotion": "excited", "gender": "female", "age": "young"},
        # Add more profiles as needed
    }

    # Select character profile based on detected emotion or default
    if detected_emotion in ['excited', 'happy']:
        selected_profile = character_profiles["Energetic"]
    elif detected_emotion == 'angry':
        selected_profile = character_profiles["Narrator"]  # Example mapping
    else:
        selected_profile = character_profiles["Default"]

    # Determine which audio effect to apply based on emotion
    if detected_emotion in ['excited', 'happy']:
        audio_effect = 'reverb'
    elif detected_emotion == 'angry':
        audio_effect = 'giantess_echo'
    else:
        audio_effect = 'none'

    # Generate audio using the selected TTS service
    if tts_service == 'elevenlabs':
        voice_id = data.get('voice_id')  # Expecting voice_id from frontend
        if not voice_id:
            return jsonify({'error': 'No voice ID provided for ElevenLabs.'}), 400
        audio_file = send_tts_request_elevenlabs(text, voice_id)
    elif tts_service == 'xtts':
        speaker_wav = selected_profile['gender']  # e.g., 'female' or 'male'
        audio_file = send_tts_request_xtts(text, speaker_wav=speaker_wav)
    else:
        return jsonify({'error': 'Invalid TTS service selected.'}), 400

    if not audio_file:
        return jsonify({'error': 'Failed to generate audio.'}), 500

    # Apply audio effects based on detected emotion
    if audio_effect == 'reverb':
        processed_file = apply_reverb_effect(audio_file)
    elif audio_effect == 'giantess_echo':
        processed_file = apply_giantess_echo_effect(audio_file)
    else:
        processed_file = audio_file  # No effect

    if not processed_file:
        return jsonify({'error': 'Failed to apply audio effects.'}), 500

    # Move the audio file to the OUTPUT_DIR with a unique filename
    extension = "mp3" if tts_service == 'elevenlabs' else "wav"
    unique_filename = generate_unique_filename(extension)
    destination_path = os.path.join(OUTPUT_DIR, unique_filename)
    os.rename(processed_file, destination_path)

    # Generate the audio URL
    audio_url = f"/static/audio/{unique_filename}"

    return jsonify({'audio_url': audio_url}), 200


# app.py

from flask import Flask, render_template, request, jsonify
import os
import logging
import uuid
from dotenv import load_dotenv

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define output directory for audio files
OUTPUT_DIR = os.path.join(app.root_path, "static", "audio")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Import modularized components
#from tts import send_tts_request_xtts, send_tts_request_elevenlabs, get_elevenlabs_voices
from ai_responses.openai_gpt4 import get_gpt4_response
from ai_responses.ollama import get_ollama_response
from audio_effects.effects import apply_reverb_effect, apply_giantess_echo_effect
from utils.emotion import detect_emotion
from utils.helpers import generate_unique_filename, escape_html


from flask import Flask, render_template, request, jsonify
import os
import logging
import uuid
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define output directory for audio files
OUTPUT_DIR = os.path.join(app.root_path, "static", "audio")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Import modularized components
from tts.xtts import send_tts_request_xtts
#from tts.elevenlabs import send_tts_request_elevenlabs, get_elevenlabs_voices
from ai_responses.openai_gpt4 import get_gpt4_response
from ai_responses.ollama import get_ollama_response
from utils.emotion import detect_emotion
from utils.helpers import generate_unique_filename, escape_html

# Placeholder AI name (can be dynamic based on session/chat)
AI_NAME = "Jarvis"


@app.route('/generate_tts', methods=['POST'])
def generate_tts():
    data = request.get_json()
    text = data.get('text')
    tts_service = data.get('tts_service')
    ai_framework = data.get('ai_framework', 'openai')  # Default to OpenAI

    if not text:
        return jsonify({'error': 'No text provided.'}), 400

    # Detect emotion from the text
    detected_emotion = detect_emotion(text)
    logging.info(f"Detected emotion: {detected_emotion}")

    # Define character profiles based on emotion or predefined
    character_profiles = {
        "Default": {"pitch": 1.0, "speed": 1.0, "tone": "neutral", "emotion": "neutral", "gender": "female", "age": "adult"},
        "Narrator": {"pitch": 1.0, "speed": 0.9, "tone": "calm", "emotion": "calm", "gender": "male", "age": "senior"},
        "Energetic": {"pitch": 1.2, "speed": 1.1, "tone": "bright", "emotion": "excited", "gender": "female", "age": "young"},
        # Add more profiles as needed
    }

    # Select character profile based on detected emotion or default
    if detected_emotion in ['excited', 'happy']:
        selected_profile = character_profiles["Energetic"]
    elif detected_emotion == 'angry':
        selected_profile = character_profiles["Narrator"]  # Example mapping
    else:
        selected_profile = character_profiles["Default"]

    # Determine which audio effect to apply based on emotion
    if detected_emotion in ['excited', 'happy']:
        audio_effect = 'reverb'
    elif detected_emotion == 'angry':
        audio_effect = 'giantess_echo'
    else:
        audio_effect = 'none'

    # Generate audio using the selected TTS service
    if tts_service == 'elevenlabs':
        voice_id = data.get('voice_id')  # Expecting voice_id from frontend
        if not voice_id:
            return jsonify({'error': 'No voice ID provided for ElevenLabs.'}), 400
        audio_file = send_tts_request_elevenlabs(text, voice_id)
    elif tts_service == 'xtts':
        speaker_wav = selected_profile['gender']  # e.g., 'female' or 'male'
        audio_file = send_tts_request_xtts(text, speaker_wav=speaker_wav)
    else:
        return jsonify({'error': 'Invalid TTS service selected.'}), 400

    if not audio_file:
        return jsonify({'error': 'Failed to generate audio.'}), 500

    # Apply audio effects based on detected emotion
    if audio_effect == 'reverb':
        processed_file = apply_reverb_effect(audio_file)
    elif audio_effect == 'giantess_echo':
        processed_file = apply_giantess_echo_effect(audio_file)
    else:
        processed_file = audio_file  # No effect

    if not processed_file:
        return jsonify({'error': 'Failed to apply audio effects.'}), 500

    # Move the audio file to the OUTPUT_DIR with a unique filename
    extension = "mp3" if tts_service == 'elevenlabs' else "wav"
    unique_filename = generate_unique_filename(extension)
    destination_path = os.path.join(OUTPUT_DIR, unique_filename)
    os.rename(processed_file, destination_path)

    # Generate the audio URL
    audio_url = f"/static/audio/{unique_filename}"

    return jsonify({'audio_url': audio_url}), 200


def generate_ai_response(message, ai_framework='openai'):
    """
    Generate AI response using selected framework.

    Args:
        message (str): User message.
        ai_framework (str): AI framework to use ('openai' or 'ollama').

    Returns:
        str: AI response or None.
    """
    if ai_framework == 'openai':
        return get_gpt4_response(message)
    elif ai_framework == 'ollama':
        return get_ollama_response(message)
    else:
        logging.error(f"Unknown AI framework: {ai_framework}")
        return None

def get_gpt4_response(message):
    # Implement the function to get GPT-4 response
    # For demonstration purposes, returning a static response
    return "This is a response from GPT-4."

def get_ollama_response(message):
    # Implement the function to get Ollama response
    # For demonstration purposes, returning a static response
    return "This is a response from Ollama."

from app import create_app, db

from app import create_app, db
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=80)
