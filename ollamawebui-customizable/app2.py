import re
import json
import requests
import logging
from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')  # Ensure you set a secret key

# Configure SQLAlchemy with absolute database path
basedir = os.path.abspath(os.path.dirname(__file__))
database_path = os.path.join(basedir, 'chats.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{database_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Configure Logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for more detailed logs
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app_debug.log"),  # Logs saved to app_debug.log
        logging.StreamHandler()  # Logs also output to the console
    ]
)

# Define Models
class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    id = db.Column(db.String(36), primary_key=True)  # 36-character UUID with hyphens
    name = db.Column(db.String(100), nullable=False)
    context = db.Column(db.Text, nullable=False, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    messages = db.relationship('ChatMessage', backref='chat', lazy=True, cascade="all, delete-orphan")

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.String(36), db.ForeignKey('chat_sessions.id'), nullable=False)
    sender = db.Column(db.String(10), nullable=False)  # 'user' or 'ai'
    content = db.Column(db.Text, nullable=False)
    sanitized = db.Column(db.Boolean, default=False)  # Flag to track sanitization

# Sanitization Functions
def sanitize_ai_message(message):
    """
    Remove unwanted spaces before apostrophes and fix specific split words without removing natural spaces.
    """
    # 1. Remove spaces before apostrophes (e.g., "I 'm" -> "I'm")
    message = re.sub(r"\s+'", "'", message)
    message = re.sub(r"'\s+", "'", message)
    
    # 2. Correct specific split words without affecting normal word spacing
    # Example: "ph er om one" -> "pheromone"
    message = re.sub(r"\bph\s+er\s+om\s+one\b", "pheromone", message, flags=re.IGNORECASE)
    message = re.sub(r"\bspr\s+ays\b", "sprays", message, flags=re.IGNORECASE)
    message = re.sub(r"\bsound\s+ly\b", "soundly", message, flags=re.IGNORECASE)
    
    # 3. Ensure AI's name is correctly formatted
    message = re.sub(r"\bJar\s+vis\b", "Jarvis", message, flags=re.IGNORECASE)
    
    # 4. Remove spaces before punctuation without affecting natural spaces
    message = re.sub(r'\s+([?.!,])', r'\1', message)
    
    return message

def post_process_ai_message(message):
    """
    Further corrects AI messages by fixing known space injection patterns.
    """
    # Correct specific known patterns
    corrections = {
        r"\bI\s+'m\b": "I'm",
        r"\byou\s+'re\b": "you're",
        r"\byou\s+'ve\b": "you've",
        r"\byou\s+'ll\b": "you'll",
        r"\bJar\s+vis\b": "Jarvis",
        r"\bph\s+er\s+om\s+one\b": "pheromone",
        r"\bspr\s+ays\b": "sprays",
        r"\bsound\s+ly\b": "soundly",
        # Add more as needed
    }

    for pattern, replacement in corrections.items():
        message = re.sub(pattern, replacement, message)

    # Aggressively remove spaces within words longer than 5 characters
    message = re.sub(r'\b(\w{2,})\s+(\w{2,})\b', lambda m: ''.join(m.groups()), message)
    
    # Remove any remaining single spaces within words
    message = re.sub(r'(?<=\w)\s+(?=\w)', '', message)
    
    # Remove spaces before punctuation
    message = re.sub(r'\s+([?.!,])', r'\1', message)

    return message

# AI Response Generation Function
def get_ollama_response(message, chat_id):
    """
    Function to interact with the Ollama API.
    """
    try:
        # Retrieve all messages for this chat to build context
        messages = ChatMessage.query.filter_by(chat_id=chat_id).order_by(ChatMessage.id.asc()).all()

        # Build context from messages with sanitized input
        context = ""
        for msg in messages:
            sender = msg.sender.capitalize().strip()
            content = msg.content.strip()
            if msg.sender.lower() == 'ai' and not msg.sanitized:
                content = sanitize_ai_message(content)
                msg.content = content
                msg.sanitized = True
                db.session.add(msg)
            context += f"{sender}: {content}\n"

        # Append the latest user message
        context += f"User: {sanitize_ai_message(message)}\n"

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
                    "content": "You are a kind and empathetic AI companion named Jarvis. Please ensure that your name is always spelled correctly as 'Jarvis' without any spaces. Avoid adding unnecessary spaces in your responses, especially within words and around apostrophes. Maintain proper grammar and punctuation to provide clear and concise assistance."
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

        # Log the raw response
        logging.debug(f"Ollama API raw response: {response.text}")

        # Handle multiple JSON objects separated by newlines
        responses = response.text.strip().split('\n')
        ai_messages = []
        for resp in responses:
            try:
                resp_json = json.loads(resp.strip())  # Strip spaces before parsing JSON
                if 'message' in resp_json and 'content' in resp_json['message']:
                    ai_message = resp_json['message']['content'].strip()
                    ai_message = sanitize_ai_message(ai_message)  # First sanitization
                    ai_message = post_process_ai_message(ai_message)  # Further sanitization
                    ai_messages.append(ai_message)
            except json.JSONDecodeError:
                logging.warning(f"Skipping invalid JSON response: {resp.strip()}")
                continue

        if ai_messages:
            # Concatenate all AI messages
            full_ai_message = '\n'.join(ai_messages)
            logging.debug(f"Sanitized AI response after post-processing: {full_ai_message}")
            return full_ai_message
        else:
            logging.error("No valid AI response found.")
            return "I'm sorry, I couldn't process that request."

    except requests.exceptions.RequestException as e:
        logging.error(f"Ollama API request failed: {e}")
        return "I'm sorry, I'm having trouble connecting to my AI friend right now."
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {e}")
        logging.debug(f"Response content: {response.text}")  # Log the response that caused the error
        return "I'm sorry, I received an unexpected response."
    except Exception as e:
        logging.error(f"Error generating Ollama response: {e}")
        return "I'm sorry, something went wrong while processing your request."

@app.route('/')
def index():
    try:
        # Fetch existing chats to display in the sidebar
        chats = ChatSession.query.all()
        return render_template('index.html', chats=chats)
    except Exception as e:
        logging.error(f"Error loading index page: {e}")
        return "500 Internal Server Error\nSomething went wrong on our end. Please try again later.", 500

# Chat Route
@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Retrieve and sanitize input data
        data = request.get_json()
        chat_id = session.get('chat_id')
        message = data.get('message', '').strip()  # Ensure the message is stripped
        ai_framework = data.get('ai_framework', 'ollama').strip()  # Default to 'ollama' and strip

        logging.debug(f"Received data: {data}")
        logging.info(f"Received message: {message} for chat_id: {chat_id}")

        if not chat_id:
            logging.warning("No chat_id found in session.")
            return jsonify({'error': 'Chat session not found.'}), 400

        if not message:
            logging.error("No message received from the user.")
            return jsonify({'error': 'No message provided.'}), 400

        # Retrieve the chat session
        chat_session = ChatSession.query.filter_by(id=chat_id).first()

        if not chat_session:
            logging.warning(f"Chat session with id {chat_id} not found.")
            return jsonify({'error': 'Chat session not found.'}), 404

        # Sanitize the user's message
        sanitized_message = sanitize_ai_message(message)
        chat_session.context += f"User: {sanitized_message}\n"

        # Save the sanitized user's message to ChatMessage
        user_message = ChatMessage(
            chat_id=chat_id,
            sender='user',
            content=sanitized_message,
            sanitized=True  # Since user messages don't need sanitization, mark as sanitized
        )
        db.session.add(user_message)

        # Generate AI response using the specified framework
        ai_response = get_ollama_response(message, chat_id)

        if ai_response:
            sanitized_ai_response = sanitize_ai_message(ai_response.strip())  # Ensure the AI response is stripped and sanitized
            sanitized_ai_response = post_process_ai_message(sanitized_ai_response)  # Further sanitize

            chat_session.context += f"AI: {sanitized_ai_response}\n"  # Append to context

            # Save the sanitized AI's message to ChatMessage
            ai_message = ChatMessage(
                chat_id=chat_id,
                sender='ai',
                content=sanitized_ai_response,
                sanitized=True  # Mark as sanitized to prevent double processing
            )
            db.session.add(ai_message)
        else:
            ai_response = "I'm sorry, I couldn't process that request."

        # Commit all changes to the database
        db.session.commit()

        logging.info(f"AI response: {ai_response} for chat_id: {chat_id}")

        # Return the AI response
        return jsonify({'response': ai_response})

    except Exception as e:
        # Rollback the session in case of an error
        db.session.rollback()
        logging.error(f"Error processing chat message: {e}")
        return jsonify({'error': 'An error occurred while processing your message.'}), 500

# Cleanup Function (Optional)
def clean_existing_messages():
    with app.app_context():
        try:
            chat_sessions = ChatSession.query.all()
            for session in chat_sessions:
                # Clean the context
                session.context = sanitize_ai_message(session.context)
                
                # Optionally, clean individual messages
                for msg in session.messages:
                    if not msg.sanitized:
                        sanitized_content = sanitize_ai_message(msg.content)
                        sanitized_content = post_process_ai_message(sanitized_content)
                        msg.content = sanitized_content
                        msg.sanitized = True
                        db.session.add(msg)
                
                db.session.add(session)
            db.session.commit()
            logging.info("Successfully cleaned all existing chat contexts and messages.")
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error cleaning chat contexts and messages: {e}")

# Run the App
if __name__ == "__main__":
    # Uncomment the following line to perform cleanup once
    # clean_existing_messages()
    
    # Paths to your SSL certificate and private key
    cert_file = 'SSL/certificate.crt'
    key_file = 'SSL/private.key'

    # Validate the existence of SSL files
    if not os.path.exists(cert_file):
        raise FileNotFoundError(f"Certificate file not found: {cert_file}")
    if not os.path.exists(key_file):
        raise FileNotFoundError(f"Private key file not found: {key_file}")

    print(f"Starting Flask app with SSL...\nCertificate: {cert_file}\nKey: {key_file}")
    
    clean_existing_messages()
    
    # Run the app with SSL in debug mode
    app.run(host='0.0.0.0', port=443, ssl_context=(cert_file, key_file), debug=True)