# inspect_db.py

from extensions import db
from models import ChatSession, ChatMessage
from utils.helpers import get_all_chat_sessions, get_messages_for_session

def main():
    # Initialize Flask application context
    from app import app
    with app.app_context():
        sessions = get_all_chat_sessions()
        for session_obj in sessions:
            print(f"Session Name: {session_obj.name}")
            messages = get_messages_for_session(session_obj.id)
            for message in messages:
                print(f"{message.sender}: {message.content}")
            print("-" * 40)  # Separator between sessions

if __name__ == "__main__":
    main()
