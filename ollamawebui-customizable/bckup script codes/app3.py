from flask import Flask, render_template, request, jsonify
import requests
import json
import secrets
print(secrets.token_hex(16))

app = Flask(__name__)

# Dictionary to store user context
user_context = {}

def generate(user_id: str, prompt: str):
    # Retrieve the context for the user
    context = user_context.get(user_id, "")
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
        user_context[user_id] = context

        return combined_response.strip()
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/chat', methods=['POST'])
def chat():
    user_id = "default_user"
    prompt = request.json.get("prompt")
    response = generate(user_id, prompt)
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)
