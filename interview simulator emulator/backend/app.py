# app.py

import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Initialize Groq client
api_key = os.getenv('GROQ_API_KEY')
if not api_key:
    raise ValueError("GROQ_API_KEY not found in environment variables.")

groq_api_url = "https://api.groq.com/openai/v1/chat/completions"

def get_groq_response(user_message: str) -> str:
    payload = {
        "messages": [
            {
                "role": "system",
                "content": "You are an AI-powered job interviewer. Ask relevant interview questions to assess the candidate's qualifications, skills, and fit for the position. Maintain a professional and encouraging tone throughout the interview."
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        "model": "llama3-8b-8192",
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    response = requests.post(groq_api_url, json=payload, headers=headers)
    
    if response.status_code != 200:
        return f"Error: {response.text}"
    
    try:
        ai_response = response.json()['choices'][0]['message']['content']
        return ai_response
    except (KeyError, IndexError) as e:
        return "Invalid response format from Groq API."

@app.route('/interview', methods=['GET'])
def interview():
    return render_template('index.html')

@app.route('/get-response', methods=['POST'])
def get_response():
    data = request.get_json()
    user_message = data.get('message', '')
    if not user_message:
        return jsonify({"response": "No message provided."}), 400
    
    ai_response = get_groq_response(user_message)
    return jsonify({"response": ai_response})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
