import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import logging
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure SQLAlchemy with absolute database path
basedir = os.path.abspath(os.path.dirname(__file__))
database_path = os.path.join(basedir, 'chats.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{database_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Configure Logging
logging.basicConfig(
    level=logging.INFO,  # Set to INFO or DEBUG for more verbosity
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("delete_chats.log"),  # Logs saved to delete_chats.log
        logging.StreamHandler()  # Logs also output to the console
    ]
)

# Define Models
class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    id = db.Column(db.String(36), primary_key=True)  # UUID with hyphens
    name = db.Column(db.String(100), nullable=False)
    context = db.Column(db.Text(), nullable=False, default="")
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)
    messages = db.relationship('ChatMessage', backref='chat', lazy=True, cascade="all, delete-orphan")

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.String(36), db.ForeignKey('chat_sessions.id'), nullable=False)
    sender = db.Column(db.String(10), nullable=False)  # 'user' or 'ai'
    content = db.Column(db.Text, nullable=False)

# Function to sanitize AI messages
def sanitize_ai_message(message):
    """
    Remove unwanted spaces before apostrophes, fix split words, and correct AI's name.
    """
    # Remove spaces before and after apostrophes (e.g., "I 'm" -> "I'm")
    message = re.sub(r"\s+'", "'", message)
    message = re.sub(r"'\s+", "'", message)
    
    # Remove spaces within contractions and possessives (e.g., "I 've" -> "I've")
    message = re.sub(r"(\w)\s+(\')\s+(\w)", r"\1\2\3", message)
    
    # Fix split words where a single character is followed by space and next character (e.g., "gl ad" -> "glad")
    message = re.sub(r"(\b\w)\s+(\w\b)", r"\1\2", message)
    
    # Ensure the AI's name is correctly formatted (e.g., "Jar vis" -> "Jarvis")
    message = re.sub(r"\bJar\s+vis\b", "Jarvis", message)
    
    # Remove multiple spaces
    message = re.sub(r"\s{2,}", " ", message)
    
    # Remove spaces before punctuation (e.g., "good !" -> "good!")
    message = re.sub(r"\s+([?.!,])", r"\1", message)
    
    # Replace specific mis-encodings if any (e.g., "ðŸ˜Š" should be "😊")
    message = message.replace("ðŸ˜Š", "😊").replace("ðŸ˜Œ", "😉")  # Add more as needed
    
    return message

# Function to delete a chat session by ID
def delete_chat_by_id(chat_id):
    with app.app_context():  # Ensure we're within an application context
        try:
            # Validate chat_id format
            if len(chat_id) != 36:
                logging.warning(f"Invalid chat ID format (expected 36-character UUID): {chat_id}")
                return

            # Use Session.get() to retrieve the chat session
            chat_to_delete = db.session.get(ChatSession, chat_id)
            if chat_to_delete:
                confirmation = input(f"Are you sure you want to delete chat session '{chat_to_delete.name}' with ID '{chat_id}'? (yes/no): ")
                if confirmation.lower() == 'yes':
                    db.session.delete(chat_to_delete)
                    db.session.commit()
                    logging.info(f"Deleted chat session with ID: {chat_id}")
                else:
                    logging.info(f"Skipped deletion for chat session with ID: {chat_id}")
            else:
                logging.warning(f"No chat session found with ID: {chat_id}")
        except Exception as e:
            logging.error(f"Error deleting chat session with ID {chat_id}: {e}")
            db.session.rollback()

# Main execution
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python delete_chats.py <chat_id1> <chat_id2> ...")
        sys.exit(1)

    chat_ids_to_delete = sys.argv[1:]

    for cid in chat_ids_to_delete:
        delete_chat_by_id(cid)
