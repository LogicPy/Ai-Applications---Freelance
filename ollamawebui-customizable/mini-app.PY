# app.py

import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import uuid
import logging
import requests
import json

# Initialize Flask app
app = Flask(__name__, instance_relative_config=True)

# **1. Set the SECRET_KEY before initializing extensions**
app.config['SECRET_KEY'] = 'this_should_be_a_secure_and_unique_secret_key'

# **2. Configure the SQLAlchemy Database URI**
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/chats.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# **3. Initialize SQLAlchemy and Flask-Migrate**
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# **4. Configure Logging**
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more detailed logs
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app_debug.log"),
        logging.StreamHandler()
    ]
)

# **5. Define Your Models**
class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), nullable=False, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False, default="Chat with AI")
    context = db.Column(db.Text(), nullable=False, default="")
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.String(36), db.ForeignKey('chat_sessions.id'), nullable=False)
    sender = db.Column(db.String(10), nullable=False)  # 'user' or 'ai'
    content = db.Column(db.Text(), nullable=False)

# **6. Define Your Routes**
@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        logging.error(f"Error loading index page: {e}")
        return "500 Internal Server Error\nSomething went wrong on our end. Please try again later.", 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_id = session.get('user_id')
        prompt = request.form.get('message')

        if not user_id:
            return jsonify({'error': 'User session not found.'}), 400

        # Retrieve the chat session
        chat_session = ChatSession.query.filter_by(id=user_id).first()

        if not chat_session:
            return jsonify({'error': 'Chat session not found.'}), 404

        # Append the user's message
        chat_session.context += f"User: {prompt}\n"

        # Generate AI response using Ollama
        ai_response = get_ollama_response(prompt, chat_session.id)

        if ai_response:
            chat_session.context += f"AI: {ai_response}\n"
        else:
            ai_response = "I'm sorry, I couldn't process that request."

        # Commit changes
        db.session.commit()

        return jsonify({'response': ai_response})

    except Exception as e:
        logging.error(f"Error processing chat message: {e}")
        return jsonify({'error': 'An error occurred while processing your message.'}), 500

def get_ollama_response(message, chat_id):
    """
    Function to interact with the Ollama API.
    """
    try:
        # Retrieve all messages for this chat to build context
        chat_session = ChatSession.query.filter_by(id=chat_id).first()
        context = chat_session.context if chat_session else ""

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
                    "content": context + f"User: {message}\n"
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

# **7. Initialize a New Chat Session (Optional)**
# You might need a route to start a new chat session
@app.route('/start_chat', methods=['POST'])
def start_chat():
    try:
        user_id = str(uuid.uuid4())
        session['user_id'] = user_id  # Store user_id in session
        chat_name = request.form.get('name', 'Chat with AI')

        new_chat = ChatSession(
            id=str(uuid.uuid4()),
            user_id=user_id,
            name=chat_name,
            context=""
        )

        db.session.add(new_chat)
        db.session.commit()

        return redirect(url_for('index'))
    except Exception as e:
        logging.error(f"Error starting new chat: {e}")
        return jsonify({'error': 'Failed to start a new chat session.'}), 500

if __name__ == '__main__':
    print('the config directory ' + app.config['SQLALCHEMY_DATABASE_URI'])
    app.run()
