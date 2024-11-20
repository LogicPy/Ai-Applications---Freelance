# clean_messages.py

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import logging
import re

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure SQLAlchemy with absolute path
basedir = os.path.abspath(os.path.dirname(__file__))
database_path = os.path.join(basedir, 'chats.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{database_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("clean_messages.log"),
        logging.StreamHandler()
    ]
)

# Define Models
class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    context = db.Column(db.Text(), nullable=False, default="")
    created_at = db.Column(db.DateTime(), default=db.func.current_timestamp())
    messages = db.relationship('ChatMessage', backref='chat_session', lazy=True, cascade="all, delete-orphan")

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.String(36), db.ForeignKey('chat_sessions.id'), nullable=False)
    sender = db.Column(db.String(10), nullable=False)  # 'user' or 'ai'
    content = db.Column(db.Text, nullable=False)

# Function to clean message content
def clean_message_content(content):
    # Example cleaning: Remove extra spaces and ensure proper spacing
    # This regex replaces multiple spaces with a single space
    content = re.sub(r'\s+', ' ', content)
    # Ensure space after punctuation if missing
    content = re.sub(r'([.,!?])([^\s])', r'\1 \2', content)
    return content.strip()

# Function to clean all messages
def clean_all_messages():
    with app.app_context():
        messages = ChatMessage.query.all()
        for msg in messages:
            original_content = msg.content
            cleaned_content = clean_message_content(original_content)
            if original_content != cleaned_content:
                logging.info(f"Cleaning message ID {msg.id}: '{original_content}' -> '{cleaned_content}'")
                msg.content = cleaned_content
        db.session.commit()
        logging.info("All messages have been cleaned and updated.")

if __name__ == "__main__":
    clean_all_messages()
