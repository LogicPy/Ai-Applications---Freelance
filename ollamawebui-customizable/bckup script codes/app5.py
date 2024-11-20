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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat_app.db'  # Using SQLite for simplicity
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

# Define Models AFTER initializing 'db'
class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    messages = db.relationship('ChatMessage', backref='chat', lazy=True)

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.String(32), db.ForeignKey('chat_sessions.id'), nullable=False)
    sender = db.Column(db.String(10), nullable=False)  # 'user' or 'ai'
    content = db.Column(db.Text, nullable=False)

# Routes

@app.route('/')
def index():
    return render_template('index.html')  # Ensure you have an 'index.html' template

@app.route('/create_chat', methods=['POST'])
def create_chat():
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

@app.route('/get_chats', methods=['GET'])
def get_chats():
    chats = ChatSession.query.all()
    chat_list = [{'id': chat.id, 'name': chat.name} for chat in chats]
    return jsonify({'chats': chat_list}), 200

@app.route('/get_chat_messages/<chat_id>', methods=['GET'])
def get_chat_messages(chat_id):
    chat = ChatSession.query.filter_by(id=chat_id).first()
    if not chat:
        logging.error(f"Chat ID {chat_id} not found.")
        return jsonify({'error': 'Chat session not found.'}), 404

    messages = ChatMessage.query.filter_by(chat_id=chat_id).all()
    message_list = [{'sender': msg.sender, 'content': msg.content} for msg in messages]
    return jsonify({'messages': message_list}), 200

@app.route('/chat/<chat_id>', methods=['GET'])
def chat_page(chat_id):
    chat = ChatSession.query.filter_by(id=chat_id).first()
    if not chat:
        logging.error(f"Chat ID {chat_id} not found.")
        return "Chat session not found.", 404

    return render_template('chat.html', chat_id=chat_id)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('prompt')
    chat_id = data.get('chat_id')
    ai_framework = data.get('ai_framework', 'openai')  # Default to OpenAI

    if not user_message:
        return jsonify({'response': 'No message provided.'}), 400

    chat = ChatSession.query.filter_by(id=chat_id).first()
    if not chat:
        logging.error(f"Chat ID {chat_id} not found.")
        return jsonify({'response': 'Chat session not found.'}), 404

    # Append user message to the chat session
    new_user_message = ChatMessage(chat_id=chat_id, sender='user', content=user_message)
    db.session.add(new_user_message)
    db.session.commit()

    # Generate AI response
    ai_response = generate_ai_response(user_message, ai_framework=ai_framework)

    if not ai_response:
        logging.error("Failed to generate AI response.")
        return jsonify({'response': 'Failed to generate AI response.'}), 500

    # Append AI response to the chat session
    new_ai_message = ChatMessage(chat_id=chat_id, sender='ai', content=ai_response)
    db.session.add(new_ai_message)
    db.session.commit()

    return jsonify({'response': ai_response})

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

if __name__ == "__main__":
    app.run(debug=True)
