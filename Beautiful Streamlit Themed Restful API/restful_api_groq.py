
from flask import Flask, request, jsonify, render_template
import os
import requests

app = Flask(__name__)

# Set up API environment
os.environ['GROQ_API_KEY'] = 'GROQ_API_KEY'
api_key = os.environ.get('GROQ_API_KEY')
groq_api_url = "https://api.groq.com/openai/v1/chat/completions"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/groq', methods=['POST'])
def converse_with_groq():
    data = request.get_json()
    user_message = data.get('message')
    model = data.get('model', 'llama3-8b-8192')  # Default to 'llama3-8b-8192' if no model specified.

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        groq_response = get_groq_response(user_message, model)
        return jsonify({"response": groq_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_groq_response(message, model):
    payload = {
        "messages": [{"role": "user", "content": message}],
        "model": model
    }
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.post(groq_api_url, json=payload, headers=headers)
    response.raise_for_status()
    groq_response = response.json()['choices'][0]['message']['content']
    formatted_response = f"<pre><code>{groq_response}</code></pre>"
    return formatted_response
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)