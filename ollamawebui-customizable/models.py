# models.py

from extensions import db

class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    id = db.Column(db.String(36), primary_key=True)  # UUID
    name = db.Column(db.String(100), nullable=False)  # Session name
    context = db.Column(db.Text, nullable=False)

    messages = db.relationship('ChatMessage', backref='chat_session', lazy=True)

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.String(36), db.ForeignKey('chat_sessions.id'), nullable=False)
    sender = db.Column(db.String(10), nullable=False)  # 'user' or 'ai'
    content = db.Column(db.Text, nullable=False)
    sanitized = db.Column(db.Boolean, default=False)  # Sanitization flag
