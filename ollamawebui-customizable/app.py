# app.py

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_session import Session
from extensions import db
from models import ChatSession, ChatMessage
import uuid
import logging
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from utils.sanitization import sanitize_ai_message, post_process_ai_message
import requests
import json
import re
from bs4 import BeautifulSoup  # Ensure BeautifulSoup is imported

# Initialize Flask application
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app_debug.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logging.debug("Flask app initialized successfully.")

# Load environment variables from .env file
load_dotenv()

# Secret key for session encryption
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secure_secret_key_here')

# Session configuration
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './flask_session/'
app.config['SESSION_PERMANENT'] = False

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'  # Replace with your DB URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
Session(app)

# Redirect HTTP to HTTPS
@app.before_request
def redirect_to_https():
    if request.url.startswith('http://'):
        return redirect(request.url.replace('http://', 'https://'), code=301)

# Context processor to handle static file caching
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.static_folder, filename)
            if os.path.exists(file_path):
                values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

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
    try:
        chat_ids = session.get('chat_ids', [])
        if not chat_ids:
            chats = []
        else:
            chats = ChatSession.query.filter(ChatSession.id.in_(chat_ids)).all()
        return render_template('index.html', chats=chats)
    except Exception as e:
        logging.error(f"Error in index route: {e}")
        return render_template('500.html'), 500


# Chat Page Route
@app.route('/chat/<chat_id>', methods=['GET'])
def chat_page(chat_id):
    try:
        if 'chat_ids' not in session or chat_id not in session['chat_ids']:
            return redirect(url_for('index'))

        chat_session = ChatSession.query.filter_by(id=chat_id).first()
        if not chat_session:
            return redirect(url_for('index'))

        messages = ChatMessage.query.filter_by(chat_id=chat_id).order_by(ChatMessage.id).all()
        return render_template(
            'chat.html',
            messages=messages,
            chat_id=chat_id,
            ai_name='Jarvis',
            chats=ChatSession.query.filter(ChatSession.id.in_(session['chat_ids'])).all()
        )
    except Exception as e:
        logging.error(f"Error in chat_page route for chat_id {chat_id}: {e}")
        return render_template('500.html'), 500

# Helper Functions

def fetch_page_title(url):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.title.string.strip() if soup.title else url
    except Exception:
        return url  # Fallback to URL if title can't be fetched

def convert_urls_to_links(text):
    url_regex = re.compile(r'(https?://[^\s]+)')
    def replace_url(match):
        url = match.group(1)
        title = fetch_page_title(url)
        return f'<a href="{url}" target="_blank">{title}</a>'
    return url_regex.sub(replace_url, text)

# app.py

# app.py

from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import logging
import os
from dotenv import load_dotenv
from groq import Groq  # Ensure the groq package is installed

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'  # Update as needed
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key_here')  # Secure your secret key
db = SQLAlchemy(app)

# Configure Logging
logging.basicConfig(level=logging.INFO, filename='yourai_companion.log',
                    format='%(asctime)s %(levelname)s:%(message)s')

# Define your database models
class ChatSession(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    current_intent = db.Column(db.String, nullable=False)
    current_ai = db.Column(db.String, nullable=False, default='ollama')  # Default AI framework
    context = db.Column(db.Text, nullable=False, default='')

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.String, db.ForeignKey('chat_session.id'), nullable=False)
    sender = db.Column(db.String, nullable=False)  # 'user' or 'ai'
    content = db.Column(db.Text, nullable=False)
    model = db.Column(db.String, nullable=True)
    sanitized = db.Column(db.Boolean, default=False)

# Initialize the database (run once)
# with app.app_context():
#     db.create_all()

# Define your AI response functions
def get_groq_response(message, chat_id):
    """
    Generates a response from the Groq AI model based on the user's message.
    """
    try:
        # Fetch API key from environment variables
        API_KEY = os.getenv('GROQ_API_KEY')
        if not API_KEY:
            logging.error("GROQ_API_KEY is not set in environment variables.")
            return "Groq API key not configured.", "Unknown"

        # Initialize Groq client
        client = Groq(api_key=API_KEY)

        # Fetch the chat session context
        chat_session = ChatSession.query.filter_by(id=chat_id).first()
        if not chat_session:
            logging.warning(f"Chat session with id {chat_id} not found.")
            return "I'm sorry, but I couldn't find the current chat session.", "Unknown"

        # Retrieve intent description (assuming INTENTS is defined)
        INTENTS = {
            'assistant': 'Assistant AI for general queries.',
            'tutor': 'Educational assistance.',
            'travel_advisor': 'Travel planning and advice.',
            # Add more intents as needed
        }
        intent_description = INTENTS.get(chat_session.current_intent, 
                                         'Assistant AI for general queries.')

        # Construct the context with user message
        context = chat_session.context + f"User: {message}\n"

        # Prepare the payload for the Groq API
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an AI assistant designed to perceive and describe the world in a way that feels human. "
                        "When asked, you may express observations, emotions, and sensory interpretations as if you were "
                        "experiencing them like a human. Use vivid descriptions and empathetic language to make interactions "
                        "more relatable and engaging."
                    )
                },
                {
                    "role": "user",
                    "content": context
                }
            ],
            "model": "llama3-8b-8192",  # Ensure this is the correct model name
            "stream": False,
            "temperature": 0
        }

        # Make the API request to Groq
        chat_completion = client.chat.completions.create(
            messages=payload["messages"],
            model=payload["model"],
            stream=payload["stream"],
            temperature=payload["temperature"]
        )

        # Extract the assistant's reply
        assistant_reply = chat_completion.choices[0].message.content.strip()
        model_name = chat_completion.model  # Adjust based on actual response

        if not assistant_reply:
            logging.warning("No valid response from Groq.")
            return "I'm sorry, I couldn't process your request at this time.", "Unknown"

        # Update the chat session context with AI's reply
        chat_session.context += f"AI: {assistant_reply}\n"
        db.session.add(chat_session)
        db.session.commit()

        return assistant_reply, model_name

    except Exception as e:
        logging.exception(f"Unexpected error generating Groq response: {e}")
        return "I'm sorry, an unexpected error occurred.", "Unknown"

def get_ai_response(message, chat_id, ai_framework):
    """
    Generates a response from the selected AI model based on the user's message.
    
    Parameters:
        message (str): The user's message.
        chat_id (str): The unique identifier for the chat session.
        ai_framework (str): The AI framework to use ('ollama', 'grok', 'groq').
        
    Returns:
        tuple: A tuple containing the AI's response and the model name.
    """
    ai_framework = ai_framework.lower()
    if ai_framework == 'ollama':
        return get_ollama_response(message, chat_id)
    elif ai_framework == 'grok':
        return get_grok_response(message, chat_id)
    elif ai_framework == 'groq':
        return get_groq_response(message, chat_id)
    else:
        logging.warning(f"Unsupported AI framework selected: {ai_framework}")
        return "I'm sorry, the selected AI framework is not supported.", "Unknown"

# Placeholder functions for Ollama and Grok responses
def get_ollama_response(message, chat_id):
    # Implement your Ollama response logic here
    return "Ollama response placeholder.", "Ollama"

def get_grok_response(message, chat_id):
    # Implement your Grok response logic here
    return "Grok response placeholder.", "Grok"

@app.route('/create_chat', methods=['POST'])
def create_chat():
    """
    Endpoint to create a new chat session.
    Expects JSON with 'name' and 'intent'.
    """
    try:
        data = request.get_json()
        chat_name = data.get('name', 'Unnamed Chat').strip()
        intent = data.get('intent', 'assistant').strip().lower()

        if not chat_name:
            return jsonify({'success': False, 'error': 'Chat name cannot be empty.'}), 400

        # Generate a unique chat ID (simple example using name; consider using UUID for uniqueness)
        chat_id = chat_name.lower().replace(' ', '_') + '_' + str(len(ChatSession.query.all()) + 1)

        # Create a new chat session
        new_chat = ChatSession(
            id=chat_id,
            name=chat_name,
            current_intent=intent,
            current_ai='ollama',  # Default AI framework; adjust as needed
            context=''
        )
        db.session.add(new_chat)
        db.session.commit()

        return jsonify({'success': True, 'chat_id': chat_id, 'chat_name': chat_name, 'chat_intent': intent}), 201

    except Exception as e:
        logging.exception(f"Error creating chat: {e}")
        return jsonify({'success': False, 'error': 'Failed to create chat session.'}), 500

@app.route('/chat/<chat_id>')
def chat(chat_id):
    """
    Route to render the chat page for a specific chat session.
    """
    chat_session = ChatSession.query.filter_by(id=chat_id).first()
    if not chat_session:
        return redirect(url_for('index'))

    # Fetch all messages for this chat session
    messages = ChatMessage.query.filter_by(chat_id=chat_id).all()

    # Determine AI name based on current_ai framework
    ai_name_map = {
        'ollama': 'Ollama AI',
        'grok': 'Grok AI',
        'groq': 'Groq AI'
    }
    ai_name = ai_name_map.get(chat_session.current_ai, 'AI')

    return render_template('chat.html', ai_name=ai_name, messages=messages, chat_id=chat_id)

@app.route('/chat/<chat_id>/send', methods=['POST'])
def send_message(chat_id):
    """
    Endpoint to handle sending messages in a chat session.
    Expects JSON with 'message' and 'ai_framework'.
    """
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        ai_framework = data.get('ai_framework', 'ollama').strip().lower()

        if not user_message:
            logging.error("Message cannot be empty.")
            return jsonify({'success': False, 'error': 'Message cannot be empty.'}), 400

        # Verify that the chat session exists
        chat_session = ChatSession.query.filter_by(id=chat_id).first()
        if not chat_session:
            logging.error(f"Chat session with id {chat_id} not found.")
            return jsonify({'success': False, 'error': 'Chat session not found.'}), 404

        # Save user message
        user_msg = ChatMessage(
            chat_id=chat_id,
            sender='user',
            content=user_message,
            sanitized=True
        )
        db.session.add(user_msg)

        # Generate AI response
        ai_response, model_name = get_ai_response(user_message, chat_id, ai_framework)

        # Log the AI response and model name
        app.logger.info(f"AI Framework: {ai_framework}, Model Name: {model_name}, Response: {ai_response}")

        # Convert URLs to links (assuming a function exists)
        ai_response = convert_urls_to_links(ai_response)

        # Save AI message
        ai_msg = ChatMessage(
            chat_id=chat_id,
            sender='ai',
            content=ai_response.strip(),
            model=model_name,
            sanitized=True
        )
        db.session.add(ai_msg)

        db.session.commit()

        return jsonify({'success': True, 'response': ai_response, 'model': model_name}), 200

    except Exception as e:
        db.session.rollback()
        logging.exception(f"Exception in send_message: {e}")
        return jsonify({'success': False, 'error': 'Failed to send message.'}), 500


# Announcement Route
@app.route('/announcement')
def announcement():
    return render_template('announcement.html')

# Run the Flask app with SSL
if __name__ == '__main__':
    # Paths to your SSL certificate and private key
    cert_file = 'SSL/certificate.crt'
    key_file = 'SSL/private.key'

    # Validate the existence of SSL files
    if not os.path.exists(cert_file):
        raise FileNotFoundError(f"Certificate file not found: {cert_file}")
    if not os.path.exists(key_file):
        raise FileNotFoundError(f"Private key file not found: {key_file}")

    logging.debug(f"Starting Flask app with SSL...\nCertificate: {cert_file}\nKey: {key_file}")

    # Create all database tables
    with app.app_context():
        db.create_all()

    # Run the app with SSL in debug mode
    app.run(host='0.0.0.0', port=443, ssl_context=(cert_file, key_file), debug=True)
