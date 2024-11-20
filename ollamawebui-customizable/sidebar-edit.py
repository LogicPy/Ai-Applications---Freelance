# delete_chats.py

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
    id = db.Column(db.String(32), primary_key=True)  # 32-character ID
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
            chat_to_delete = ChatSession.query.get(chat_id)  # Use query.get() for primary key
            if chat_to_delete:
                db.session.delete(chat_to_delete)
                db.session.commit()
                logging.info(f"Deleted chat session with ID: {chat_id}")
            else:
                logging.warning(f"No chat session found with ID: {chat_id}")
        except Exception as e:
            logging.error(f"Error deleting chat session with ID {chat_id}: {e}")
            db.session.rollback()

# List of chat IDs to delete
chat_ids_to_delete = [
    "0ded8fb3b3224abc9ebe98a49e709e5a",
    "50733add82c240f9af5a60cb842344b0",
    "07deda8b8503451ca879222940e56e47",
    "07deda8b 8503 451c a879 222940e56e47",
    "4444fb08037441c6aa018e951f603d23",
    "d9d51c88194144bd9f4769144c540292",
    "f391eb798a534c028e3a8cc7dcce6a4c",
    "17c96557251341f28b1a090c55f3c98e",
    "b84d23d10f5848e2a32e3e7b0359bc60",
    "5e1cbc7c82d84ef498fd66e21b890563",
    "05758e3a3b3e4f4199b38960b40a241c",
    "e063e354e4e442d995de7d830835931a",
    "b631d202a4114c3db4581ff466eec778",
    "a41fc43ab2244e4695d626ff43dcaff8",
    "ffbcbe59d277429191b84b7e2fa2b97a"
]

# Run the delete function for each chat ID
if __name__ == "__main__":
    for cid in chat_ids_to_delete:
        delete_chat_by_id(cid)
