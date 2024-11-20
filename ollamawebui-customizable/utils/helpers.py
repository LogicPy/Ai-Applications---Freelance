# utils/helpers.py

from extensions import db
from models import ChatSession, ChatMessage

def get_all_chat_sessions():
    return ChatSession.query.all()

def get_messages_for_session(chat_id):
    return ChatMessage.query.filter_by(chat_id=chat_id).all()
