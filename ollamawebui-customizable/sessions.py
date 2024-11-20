from flask import Blueprint, request, jsonify, session
from extensions import db
from models import ChatSession, ChatMessage
import uuid
import logging

sessions_bp = Blueprint('sessions', __name__)

@sessions_bp.route('/create_session', methods=['POST'])
def create_session():
    try:
        data = request.get_json()
        session_name = data.get('session_name', f"Session {len(session.get('chat_ids', [])) + 1}")

        new_chat_id = str(uuid.uuid4())
        new_chat_session = ChatSession(id=new_chat_id, name=session_name, context="")
        db.session.add(new_chat_session)
        db.session.commit()

        # Add the new chat_id to the client's session
        session['chat_ids'].append(new_chat_id)
        session['current_chat_id'] = new_chat_id

        logging.info(f"Created new chat session: {session_name} with id: {new_chat_id}")

        return jsonify({'success': True, 'chat_id': new_chat_id, 'session_name': session_name}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating new chat session: {e}", exc_info=True)
        return jsonify({'error': 'Failed to create a new chat session.'}), 500

@sessions_bp.route('/switch_session', methods=['POST'])
def switch_session():
    try:
        data = request.get_json()
        chat_id = data.get('chat_id')

        # Verify that the chat_id exists in the client's session
        if 'chat_ids' not in session or chat_id not in session['chat_ids']:
            return jsonify({'error': 'Chat session not found or not authorized.'}), 404

        # Set the new chat_id as the current session
        session['current_chat_id'] = chat_id

        logging.info(f"Switched to chat session with id: {chat_id}")

        return jsonify({'success': True, 'chat_id': chat_id}), 200
    except Exception as e:
        logging.error(f"Error switching chat session: {e}", exc_info=True)
        return jsonify({'error': 'Failed to switch chat session.'}), 500

@sessions_bp.route('/list_sessions', methods=['GET'])
def list_sessions():
    try:
        if 'chat_ids' not in session:
            return jsonify({'sessions': []}), 200

        chat_ids = session['chat_ids']
        chat_sessions = ChatSession.query.filter(ChatSession.id.in_(chat_ids)).all()
        sessions_list = [{'chat_id': cs.id, 'name': cs.name} for cs in chat_sessions]

        return jsonify({'sessions': sessions_list}), 200
    except Exception as e:
        logging.error(f"Error listing chat sessions: {e}", exc_info=True)
        return jsonify({'error': 'Failed to list chat sessions.'}), 500
