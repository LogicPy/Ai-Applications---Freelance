# app.py

from flask import (
    Flask, 
    render_template, 
    request, 
    jsonify, 
    session, 
    redirect, 
    url_for
)
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import uuid
import logging
import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, instance_relative_config=True)

# Set the SECRET_KEY
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'this_should_be_a_secure_and_unique_secret_key')

# Configure the SQLAlchemy Database URI
basedir = os.path.abspath(os.path.dirname(__file__))
database_path = os.path.join(basedir, 'chats.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + database_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)

print('Database URI:', app.config['SQLALCHEMY_DATABASE_URI'])

# Configure Logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for detailed logs
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app_debug.log"),  # Logs saved to app_debug.log
        logging.StreamHandler()  # Logs also output to the console
    ]
)

# Define your models
class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False, default="Chat with AI")
    context = db.Column(db.Text(), nullable=False, default="")
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.String(36), db.ForeignKey('chat_sessions.id'), nullable=False)
    sender = db.Column(db.String(10), nullable=False)  # 'user' or 'ai'
    content = db.Column(db.Text(), nullable=False)

# Error Handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# Routes
@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        logging.error(f"Error loading index page: {e}")
        return "500 Internal Server Error\nSomething went wrong on our end. Please try again later.", 500

@app.route('/create_chat', methods=['POST'])
def create_chat():
    try:
        # Determine the content type of the request
        if request.is_json:
            data = request.get_json()
            chat_name = data.get('name')
        else:
            chat_name = request.form.get('name', 'Chat with AI')

        if not chat_name:
            logging.error("No chat name provided in the request.")
            # Differentiate responses based on request type
            if request.is_json:
                return jsonify({'success': False, 'error': 'No chat name provided.'}), 400
            else:
                return "No chat name provided.", 400

        # Generate a unique chat ID
        chat_id = str(uuid.uuid4())
        logging.info(f"Created new chat session: {chat_name} with ID: {chat_id}")

        # Store the chat_id in the session
        session['chat_id'] = chat_id

        # Create and store the chat session
        new_chat = ChatSession(
            id=chat_id,
            name=chat_name,
            context=""  # Initialize context
        )
        db.session.add(new_chat)
        db.session.commit()

        logging.info(f"Chat session {chat_id} saved to database.")

        # Respond based on request type
        if request.is_json:
            return jsonify({'success': True, 'chat_id': chat_id, 'chat_name': chat_name}), 200
        else:
            return redirect(url_for('chat_page', chat_id=chat_id))
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating chat: {e}")
        # Differentiate responses based on request type
        if request.is_json:
            return jsonify({'success': False, 'error': 'Failed to create chat.'}), 500
        else:
            return "Failed to create chat.", 500

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
        # Store chat_id in session
        session['chat_id'] = chat_id

        chat = ChatSession.query.filter_by(id=chat_id).first()
        if not chat:
            logging.error(f"Chat ID {chat_id} not found.")
            return render_template('404.html'), 404

        messages = ChatMessage.query.filter_by(chat_id=chat_id).order_by(ChatMessage.id.asc()).all()
        return render_template('chat.html', chat_id=chat_id, ai_name="Britney", messages=messages)
    except Exception as e:
        logging.error(f"Error loading chat page for {chat_id}: {e}")
        return render_template('500.html'), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        chat_id = session.get('chat_id')
        prompt = request.form.get('message')

        logging.info(f"Received message: {prompt} for chat_id: {chat_id}")

        if not chat_id:
            logging.warning("No chat_id found in session.")
            return jsonify({'error': 'Chat session not found.'}), 400

        # Retrieve the chat session
        chat_session = ChatSession.query.filter_by(id=chat_id).first()

        if not chat_session:
            logging.warning(f"Chat session with id {chat_id} not found.")
            return jsonify({'error': 'Chat session not found.'}), 404

        # Append the user's message
        chat_session.context += f"User: {prompt}\n"

        # Save the user's message to ChatMessage
        user_message = ChatMessage(
            chat_id=chat_id,
            sender='user',
            content=prompt
        )
        db.session.add(user_message)

        # Generate AI response using Ollama
        ai_response = get_ollama_response(prompt, chat_id)

        if ai_response:
            chat_session.context += f"AI: {ai_response}\n"
            # Save the AI's message to ChatMessage
            ai_message = ChatMessage(
                chat_id=chat_id,
                sender='ai',
                content=ai_response
            )
            db.session.add(ai_message)
        else:
            ai_response = "I'm sorry, I couldn't process that request."

        # Commit changes
        db.session.commit()

        logging.info(f"AI response: {ai_response} for chat_id: {chat_id}")

        return jsonify({'response': ai_response})

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error processing chat message: {e}")
        return jsonify({'error': 'An error occurred while processing your message.'}), 500

# AI Response Generation Functions
def get_ollama_response(message, chat_id):
    """
    Function to interact with the Ollama API.
    """
    try:
        # Retrieve all messages for this chat to build context
        messages = ChatMessage.query.filter_by(chat_id=chat_id).order_by(ChatMessage.id.asc()).all()

        # Build context
        context = ""
        for msg in messages:
            context += f"{msg.sender.capitalize()}: {msg.content}\n"

        # Append the latest user message
        context += f"User: {message}\n"

        # Define the API endpoint and headers
        api_url = "http://localhost:11434/api/chat"
        headers = {
            "Content-Type": "application/json"
        }

        # Create the JSON payload with context
        payload = {
            "model": "dolphin-llama3",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a role-playing AI. Your name is Britney. You're my AI best friend. Willing to help out your best friend master at any turn because you know I love you very much."
                },
                {
                    "role": "user",
                    "content": context
                }
            ]
        }

        # Send a request to the Ollama server
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()

        # Process the response
        response_json = response.json()

        if 'message' in response_json and 'content' in response_json['message']:
            ai_message = response_json['message']['content']
            return ai_message.strip()
        else:
            logging.error("Ollama response format is unexpected.")
            return "I'm sorry, I couldn't process that request."

    except requests.exceptions.RequestException as e:
        logging.error(f"Ollama API request failed: {e}")
        return "I'm sorry, I'm having trouble connecting to my AI friend right now."
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {e}")
        return "I'm sorry, I received an unexpected response."
    except Exception as e:
        logging.error(f"Error generating Ollama response: {e}")
        return "I'm sorry, something went wrong while processing your request."

# Run the Flask application
if __name__ == '__main__':
    # Remove or comment out this line to prevent overriding the SECRET_KEY
    # app.secret_key = 'super secret key'

    # Paths to your SSL certificate and private key
    cert_file = 'SSL/certificate.crt'
    key_file = 'SSL/private.key'

    # Validate the existence of SSL files
    if not os.path.exists(cert_file):
        raise FileNotFoundError(f"Certificate file not found: {cert_file}")
    if not os.path.exists(key_file):
        raise FileNotFoundError(f"Private key file not found: {key_file}")

    print(f"Starting Flask app with SSL...\nCertificate: {cert_file}\nKey: {key_file}")
    
    # Run the app with SSL
    app.run(host='0.0.0.0', port=443, ssl_context=(cert_file, key_file))
