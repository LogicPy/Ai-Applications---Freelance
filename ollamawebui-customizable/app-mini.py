import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import uuid

app = Flask(__name__, instance_relative_config=True)

# Set the SECRET_KEY
app.config['SECRET_KEY'] = 'this_should_be_a_secure_and_unique_secret_key'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/chats.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Define a simple model
class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), nullable=False, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False, default="Chat with AI")
    context = db.Column(db.Text(), nullable=False, default="")
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)

if __name__ == '__main__':
    app.run()
