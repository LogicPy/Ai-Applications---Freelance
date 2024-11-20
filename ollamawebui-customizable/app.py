# app.py

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_session import Session
from extensions import db
from models import ChatSession, ChatMessage
import uuid
import logging
import os
from flask import url_for

from dotenv import load_dotenv
from utils.sanitization import sanitize_ai_message, post_process_ai_message
import requests
import json


#client = MemoryClient(api_key="m0-enlAKCd9ZVXSkKVvPgl23bwUwyspVlsIQPJCPbsF")


# Initialize Flask application
app = Flask(__name__)

@app.before_request
def redirect_to_https():
    if request.url.startswith('http://'):
        return redirect(request.url.replace('http://', 'https://'), code=301)

@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            values['q'] = int(os.stat(os.path.join(app.static_folder, filename)).st_mtime)
    return url_for(endpoint, **values)

# Load environment variables from .env file
load_dotenv()

# Secret key for session encryption
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secure_secret_key_here')

# Session configuration
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './flask_session/'
app.config['SESSION_PERMANENT'] = False

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chats.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
Session(app)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app_debug.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logging.debug("Flask app and SQLAlchemy initialized successfully.")

# Error Handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# Index Route
@app.route('/', methods=['GET'])
def index():
    chats = ChatSession.query.filter(ChatSession.id.in_(session.get('chat_ids', []))).all()
    return render_template('index.html', chats=chats)

# Create Chat Route
@app.route('/create_chat', methods=['POST'])
def create_chat():
    try:
        data = request.get_json()
        chat_name = data.get('name', 'New Chat')
        new_chat_id = str(uuid.uuid4())
        new_chat = ChatSession(id=new_chat_id, name=chat_name, context="")
        db.session.add(new_chat)
        db.session.commit()

        # Update the user's session
        if 'chat_ids' not in session:
            session['chat_ids'] = []
        session['chat_ids'].append(new_chat_id)
        session['current_chat_id'] = new_chat_id

        return jsonify({'success': True, 'chat_id': new_chat_id, 'chat_name': chat_name}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating chat session: {e}")
        return jsonify({'success': False, 'error': 'Failed to create chat session.'}), 500

# Chat Page Route
@app.route('/chat/<chat_id>', methods=['GET'])
def chat_page(chat_id):
    if 'chat_ids' not in session or chat_id not in session['chat_ids']:
        return redirect(url_for('index'))

    chat_session = ChatSession.query.filter_by(id=chat_id).first()
    if not chat_session:
        return redirect(url_for('index'))

    messages = ChatMessage.query.filter_by(chat_id=chat_id).order_by(ChatMessage.id).all()
    return render_template('chat.html', messages=messages, chat_id=chat_id, ai_name='Jarvis', chats=ChatSession.query.filter(ChatSession.id.in_(session['chat_ids'])).all())

# Chat Endpoint for Sending Messages
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        ai_framework = data.get('ai_framework', 'ollama').strip().lower()  # Default to Ollama
        chat_id = session.get('current_chat_id')

        if not chat_id:
            return jsonify({'error': 'No active chat session.'}), 400

        chat_session = ChatSession.query.filter_by(id=chat_id).first()
        if not chat_session:
            return jsonify({'error': 'Chat session not found.'}), 404

        # Save user message to the database
        sanitized_message = sanitize_ai_message(user_message)
        user_msg = ChatMessage(chat_id=chat_id, sender='user', content=sanitized_message, sanitized=True)
        db.session.add(user_msg)

        # Get AI response based on selected framework
        if ai_framework == 'ollama':
            ai_response = get_ai_response(user_message, chat_id, ai_framework)
        elif ai_framework == 'grok':
            ai_response = get_grok_response(user_message, chat_id)
        else:
            logging.warning(f"Unsupported AI framework selected: {ai_framework}")
            ai_response = "Unsupported AI framework selected."

        # Save AI response to the database
        sanitized_ai_response = sanitize_ai_message(ai_response.strip())
        sanitized_ai_response = post_process_ai_message(sanitized_ai_response)
        ai_msg = ChatMessage(chat_id=chat_id, sender='ai', content=sanitized_ai_response, sanitized=True)
        db.session.add(ai_msg)

        db.session.commit()

        return jsonify({'response': sanitized_ai_response}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error in chat endpoint: {e}")
        return jsonify({'error': 'An error occurred during the chat.'}), 500

# Function to generate AI response using Ollama
def get_ai_response(message, chat_id, ai_framework):
    """
    Generates a response from the Ollama AI model based on the user's message.
    """
    try:
        # Define the API endpoint for Ollama
        api_url = "http://localhost:11434/api/chat"
        headers = {"Content-Type": "application/json"}

        # Prepare the context for the chat (optional: include previous messages for context)
        chat_session = ChatSession.query.filter_by(id=chat_id).first()
        if not chat_session:
            logging.warning(f"Chat session with id {chat_id} not found.")
            return "I'm sorry, but I couldn't find the current chat session."

        context = chat_session.context + f"User: {message}\n"

        # Build the payload for the request
        payload = {
            "model": "dolphin-llama3",  # Replace with your Ollama model
            "messages": [
                {
                    "role": "system",
                    "content": "You are an AI assistant named Llama3, known for concise and accurate responses."
                },
                {
                    "role": "user",
                    "content": context
                }
            ]
        }

        # Make the request to the Ollama API
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()

        # Parse the API response
        responses = response.text.strip().split("\n")
        ai_message = ""
        for resp in responses:
            try:
                data = json.loads(resp.strip())
                if "message" in data and "content" in data["message"]:
                    ai_message += data["message"]["content"].strip() + "\n"
            except json.JSONDecodeError:
                logging.warning(f"Invalid response from Ollama: {resp.strip()}")
                continue

        if not ai_message.strip():
            logging.warning("No valid response from Ollama.")
            return "I'm sorry, I couldn't process your request at this time."

        # Update the chat session context
        chat_session.context += f"AI: {ai_message.strip()}\n"
        db.session.add(chat_session)
        db.session.commit()

        return ai_message.strip()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error connecting to Ollama API: {e}")
        return "I'm sorry, I couldn't connect to the AI server."
    except Exception as e:
        logging.error(f"Error generating Ollama response: {e}")
        return "I'm sorry, an error occurred while processing your request."

# Function to generate AI response using Grok
def get_grok_response(message, chat_id):
    """
    Generates a response from the Grok AI model based on the user's message.
    """
    try:
        # Replace with your actual Grok API key from environment variables
        API_KEY = os.getenv('GROK_API_KEY')
        if not API_KEY:
            logging.error("GROK_API_KEY is not set in environment variables.")
            return "Grok API key not configured."

        # Define the API URL
        api_url = "https://api.x.ai/v1/chat/completions"

        # Define headers for the API call
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }

        # Fetch the chat session context
        chat_session = ChatSession.query.filter_by(id=chat_id).first()
        if not chat_session:
            logging.warning(f"Chat session with id {chat_id} not found.")
            return "I'm sorry, but I couldn't find the current chat session."

        context = chat_session.context + f"User: {message}\n"

        # Prepare the payload for the Grok API
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are an AI model named Grok. When asked, identify yourself clearly and provide accurate responses without humor or ambiguity."
                },
                {
                    "role": "user",
                    "content": context
                }
            ],
            "model": "grok-beta",  # Use the appropriate Grok model
            "stream": False,
            "temperature": 0
        }

        # Make the API request to Grok
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()

        # Parse the response from Grok
        response_json = response.json()
        assistant_reply = (
            response_json.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )

        if not assistant_reply.strip():
            logging.warning("No valid response from Grok.")
            return "I'm sorry, I couldn't process your request at this time."

        # Update the chat session context
        chat_session.context += f"AI: {assistant_reply.strip()}\n"
        db.session.add(chat_session)
        db.session.commit()

        return assistant_reply.strip()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error connecting to Grok API: {e}")
        return "I'm sorry, I couldn't connect to the AI server."
    except Exception as e:
        logging.error(f"Error generating Grok response: {e}")
        return "I'm sorry, an error occurred while processing your request."

@app.route('/announcement')
def announcement():
    return render_template('announcement.html')

if __name__ == '__main__':
    # Paths to your SSL certificate and private key
    cert_file = 'SSL/certificate.crt'
    key_file = 'SSL/private.key'

    # Validate the existence of SSL files
    if not os.path.exists(cert_file):
        raise FileNotFoundError(f"Certificate file not found: {cert_file}")
    if not os.path.exists(key_file):
        raise FileNotFoundError(f"Private key file not found: {key_file}")

    print(f"Starting Flask app with SSL...\nCertificate: {cert_file}\nKey: {key_file}")

    # Create all database tables
    with app.app_context():
        db.create_all()

    # Run the app with SSL in debug mode
    app.run(host='0.0.0.0', port=443, ssl_context=(cert_file, key_file), debug=True)
