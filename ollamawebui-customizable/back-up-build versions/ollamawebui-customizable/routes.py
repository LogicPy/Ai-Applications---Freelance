from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from app.models import ChatSession
from app.ai_module import generate
from app.extensions import db
import uuid
import logging

main = Blueprint('main', __name__)
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app import app, db  # Import from app.py
from models import ChatSession
import uuid
import logging

main = Blueprint('main', __name__)

@main.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        logging.error(f"Error loading index page: {e}")
        return "500 Internal Server Error\nSomething went wrong on our end. Please try again later.", 500

@main.route('/create_chat', methods=['POST'])
def create_chat():
    try:
        # Determine the content type of the request
        if request.is_json:
            data = request.get_json()
            chat_name = data.get('name')
        else:
            chat_name = request.form.get('name', 'Chat with AI')

        if not chat_name:
            logging.error("No chat name provided in the request.")
            # Differentiate responses based on request type
            if request.is_json:
                return jsonify({'success': False, 'error': 'No chat name provided.'}), 400
            else:
                return "No chat name provided.", 400

        # Generate a unique chat ID
        chat_id = str(uuid.uuid4())
        logging.info(f"Created new chat session: {chat_name} with ID: {chat_id}")

        # Handle session
        user_id = session.get('user_id', str(uuid.uuid4()))
        session['user_id'] = user_id  # Ensure user_id is stored in session

        # Create and store the chat session
        new_chat = ChatSession(
            id=chat_id,
            user_id=user_id,
            name=chat_name,
            context=""  # Initialize context
        )
        db.session.add(new_chat)
        db.session.commit()

        logging.info(f"Chat session {chat_id} saved to database.")

        # Respond based on request type
        if request.is_json:
            return jsonify({'success': True, 'chat_id': chat_id, 'chat_name': chat_name}), 200
        else:
            return redirect(url_for('main.chat_page', chat_id=chat_id))
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating chat: {e}")
        # Differentiate responses based on request type
        if request.is_json:
            return jsonify({'success': False, 'error': 'Failed to create chat.'}), 500
        else:
            return "Failed to create chat.", 500

@main.route('/chat_page')
def chat_page():
    chat_id = request.args.get('chat_id')
    if not chat_id:
        return "Chat ID not provided.", 400
    return render_template('chat.html', chat_id=chat_id)


@main.route('/c/<chat_id>')
def chat_session(chat_id):
    # Check if the chat_id exists; if not, initialize it
    chat_session = ChatSession.query.get(chat_id)
    if not chat_session:
        new_chat = ChatSession(id=chat_id, name="Chat with Jarvis")
        db.session.add(new_chat)
        db.session.commit()

    # Fetch all chat sessions to display in the sidebar
    all_chats = ChatSession.query.all()

    # Pass the current chat's name to the template
    current_chat_name = chat_session.name

    return render_template("index.html", chat_id=chat_id, all_chats=all_chats, current_chat_name=current_chat_name)

@main.route('/chat', methods=['POST'])
def chat():
    try:
        # Retrieve the chat_id from the session
        chat_id = session.get('chat_id')
        prompt = request.form.get('message')

        logging.debug(f"Received message: {prompt} for chat_id: {chat_id}")

        if not chat_id:
            logging.warning("No chat_id found in session.")
            return jsonify({'error': 'Chat session not found in session.'}), 400

        # Retrieve the ChatSession using chat_id
        chat_session = ChatSession.query.filter_by(id=chat_id).first()

        if not chat_session:
            logging.warning(f"Chat session with id {chat_id} not found.")
            return jsonify({'error': 'Chat session not found.'}), 404

        # Append the user's message
        chat_session.context += f"User: {prompt}\n"

        # Generate AI response using Ollama
        ai_response = get_ollama_response(prompt, chat_session.id)

        if ai_response:
            chat_session.context += f"AI: {ai_response}\n"
        else:
            ai_response = "I'm sorry, I couldn't process that request."

        # Commit changes
        db.session.commit()

        logging.debug(f"AI response: {ai_response} for chat_id: {chat_id}")

        return jsonify({'response': ai_response})

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error processing chat message: {e}")
        return jsonify({'error': 'An error occurred while processing your message.'}), 500


def get_ollama_response(message, chat_id):
    """
    Function to interact with the Ollama API.
    """
    try:
        # Retrieve all messages for this chat to build context
        chat_session = ChatSession.query.filter_by(id=chat_id).first()
        context = chat_session.context if chat_session else ""

        # Define the API endpoint and headers
        api_url = "http://localhost:11434/api/chat"
        headers = {
            "Content-Type": "application/json"
        }

        # Create the JSON payload with context
        payload = {
            "model": "dolphin-llama3",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a role-playing AI. Your name is Britney. You're my AI best friend. Willing to help out your best friend master at any turn because you know I love you very much."
                },
                {
                    "role": "user",
                    "content": context + f"User: {message}\n"
                }
            ]
        }

        # Send a request to the Ollama server
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()

        # Process the response
        response_json = response.json()

        if 'message' in response_json and 'content' in response_json['message']:
            ai_message = response_json['message']['content']
            return ai_message.strip()
        else:
            logging.error("Ollama response format is unexpected.")
            return "I'm sorry, I couldn't process that request."

    except requests.exceptions.RequestException as e:
        logging.error(f"Ollama API request failed: {e}")
        return "I'm sorry, I'm having trouble connecting to my AI friend right now."
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {e}")
        return "I'm sorry, I received an unexpected response."
    except Exception as e:
        logging.error(f"Error generating Ollama response: {e}")
        return "I'm sorry, something went wrong while processing your request."

@main.route('/get_chat_history', methods=['GET'])
def get_chat_history():
    chat_id = request.args.get('chat_id')
    if not chat_id:
        return jsonify({"error": "No chat_id provided."}), 400

    chat_session = ChatSession.query.get(chat_id)
    if not chat_session:
        return jsonify({"error": "Chat session not found."}), 404

    # Split the context into messages
    context = chat_session.context
    messages = context.strip().split('\n')

    return jsonify({"messages": messages})
