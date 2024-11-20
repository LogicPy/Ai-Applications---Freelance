# delete_chats.py

import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import logging

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///chats.db')
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
    __tablename__ = 'chat_sessions'  # Correct table name
    id = db.Column(db.String(32), primary_key=True)  # 32-character ID without hyphens
    name = db.Column(db.String(100), nullable=False)
    messages = db.relationship('ChatMessage', backref='chat', lazy=True, cascade="all, delete-orphan")

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.String(32), db.ForeignKey('chat_sessions.id'), nullable=False)
    sender = db.Column(db.String(10), nullable=False)  # 'user' or 'ai'
    content = db.Column(db.Text, nullable=False)

# Function to delete a chat session by ID
def delete_chat_by_id(chat_id):
    with app.app_context():  # Ensure we're within an application context
        try:
            # Validate chat_id length
            if len(chat_id) != 32:
                logging.warning(f"Invalid chat ID format (expected 32 characters): {chat_id}")
                return

            chat_to_delete = ChatSession.query.get(chat_id)  # Use query.get() for primary key
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

# python delete_chats.py 9dd4116f3d0243b9a1c8304af772764b 50733add82c240f9af5a60cb842344b0
