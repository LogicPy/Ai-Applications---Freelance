from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Import Flask-Migrate
import requests
import json
import uuid
import logging
import logging
import os
from waitress import serve
#from app import create_app  # Ensure this imports your Flask app correctly

#app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
#app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///chats.db')

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

@app.route('/')
def home():
    logging.debug("Home route accessed")
    return render_template('index.html')

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chats.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Initialize Flask-Migrate

class ChatSession(db.Model):
    id = db.Column(db.String(36), primary_key=True)  # UUID
    name = db.Column(db.String(100), nullable=False, default="Chat with Jarvis")
    context = db.Column(db.Text, nullable=False, default="")

def generate(chat_id: str, prompt: str):
    # Retrieve the context for the chat session
    chat_session = ChatSession.query.get(chat_id)
    if not chat_session:
        return "Chat session not found."

    context = chat_session.context
    context += f"User: {prompt}\n"
    
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
                "content": "You are a role-playing AI. Your name is Jarvis. You're a python and web coding AI model."
            },
            {
                "role": "user",
                "content": context
            }
        ]
    }
    
    # Send a request to the Ollama server
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        
        # Process response
        lines = response.text.strip().split('\n')
        combined_response = ""
        for line in lines:
            try:
                data = json.loads(line)
                if 'message' in data and 'content' in data['message']:
                    combined_response += data['message']['content']
            except json.JSONDecodeError:
                continue

        # Update context
        context += f"AI: {combined_response.strip()}\n"
        chat_session.context = context
        db.session.commit()

        return combined_response.strip()
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_migrate import Migrate
import requests
import json
import uuid

from flask import Flask, render_template

def create_app():
    app = Flask(__name__)

   # from .routes import main
   # app.register_blueprint(main)

    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chats.db'  # Update as needed
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_secret_key_here'  # Replace with a secure key

    # Initialize SQLAlchemy with the app
    db.init_app(app)

    # Import models after initializing db to avoid circular imports
    with app.app_context():
        db.create_all()

    # Define routes
    @app.route('/')
    def home():
        chats = ChatSession.query.all()
        return render_template('index.html', chats=chats)

    return app

@app.route('/')
def home():
    return render_template('index.html')  # Ensure you have an 'index.html' in the 'templates' folder

def add_emojis_to_response(response):
    # Simple rules to add emojis based on keywords
    if "happy" in response.lower() or "glad" in response.lower():
        response += " 😊"
    elif "love" in response.lower():
        response += " ❤️"
    elif "sorry" in response.lower():
        response += " 😔"
    elif "laugh" in response.lower() or "funny" in response.lower():
        response += " 😂"
    return response


@app.route('/')
def index():
    # Specify the chat_id you want to redirect to
    specific_chat_id = "ffbcbe59-d277-42f9-91b8-4b7e2fa2b97a"
    
    # Check if the specific chat session exists; if not, create it
    chat_session = ChatSession.query.get(specific_chat_id)
    if not chat_session:
        new_chat = ChatSession(id=specific_chat_id, name="Chat with Jarvis")
        db.session.add(new_chat)
        db.session.commit()
    
    # Redirect to the specific chat session
    return redirect(url_for('chat_session', chat_id=specific_chat_id))

@app.route('/test')
def test():
    return "Test route is working!"


@app.route('/c/<chat_id>')
def chat_session(chat_id):
    """
    Handle chat session routes.
    
    Parameters:
    - chat_id (str): The unique identifier for the chat session.
    
    Returns:
    - Rendered template with chat session details.
    """
    # Route logic here

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



@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    chat_id = data.get("chat_id")
    prompt = data.get("prompt")

    if not chat_id or not prompt:
        return jsonify({"response": "Invalid request parameters."}), 400

    response = generate(chat_id, prompt)
    return jsonify({"response": response})

@app.route('/get_chat_history', methods=['GET'])
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

if __name__ == '__main__':
    app = create_app()

    print("Starting Flask app with Waitress on port 5001")
    serve(app, host='0.0.0.0', port=5001)
    print("Starting Flask app on port 5001")
    app.run(debug=True, port=5001)
