from flask import Blueprint, request, jsonify, session
from extensions import db
from models import ChatSession, ChatMessage
import logging

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
def chat():
    try:
        # Retrieve and sanitize input data
        data = request.get_json()
        message = data.get('message', '').strip()
        ai_framework = data.get('ai_framework', 'ollama').strip()

        logging.debug(f"Received data: {data}")

        if not message:
            logging.error("No message received from the user.")
            return jsonify({'error': 'No message provided.'}), 400

        # Get the current chat_id from the session
        chat_id = session.get('current_chat_id')
        if not chat_id:
            return jsonify({'error': 'No active chat session. Please create or switch to a session first.'}), 400

        # Retrieve the chat session
        chat_session = ChatSession.query.filter_by(id=chat_id).first()

        if not chat_session:
            logging.warning(f"Chat session with id {chat_id} not found.")
            return jsonify({'error': 'Chat session not found.'}), 404

        # Sanitize the user's message
        sanitized_message = sanitize_ai_message(message)
        chat_session.context += f"User: {sanitized_message}\n"

        # Save the sanitized user's message to ChatMessage
        user_message = ChatMessage(
            chat_id=chat_id,
            sender='user',
            content=sanitized_message,
            sanitized=True  # User messages are marked as sanitized
        )
        db.session.add(user_message)

        # Generate AI response using the specified framework
        ai_response = get_ollama_response(message, chat_id)

        if ai_response:
            # Sanitize the AI's response
            sanitized_ai_response = sanitize_ai_message(ai_response.strip())
            sanitized_ai_response = post_process_ai_message(sanitized_ai_response)

            logging.debug(f"Sanitized AI response: {sanitized_ai_response}")

            chat_session.context += f"AI: {sanitized_ai_response}\n"

            # Save the sanitized AI's message to ChatMessage
            ai_message = ChatMessage(
                chat_id=chat_id,
                sender='ai',
                content=sanitized_ai_response,
                sanitized=True  # Mark as sanitized
            )
            db.session.add(ai_message)
        else:
            ai_response = "I'm sorry, I couldn't process that request."

        # Commit all changes to the database
        db.session.commit()

        logging.info(f"AI response: {ai_response} for chat_id: {chat_id}")

        # Return the sanitized AI response
        return jsonify({'response': ai_response})

    except Exception as e:
        # Rollback the session in case of an error
        db.session.rollback()
        logging.error(f"Error processing chat message: {e}", exc_info=True)
        return jsonify({'error': 'An error occurred while processing your message.'}), 500
