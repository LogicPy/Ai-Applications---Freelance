# models.py

from app import db
from datetime import datetime
import uuid

class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), nullable=False, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False, default="Chat with AI")
    context = db.Column(db.Text(), nullable=False, default="")
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)
