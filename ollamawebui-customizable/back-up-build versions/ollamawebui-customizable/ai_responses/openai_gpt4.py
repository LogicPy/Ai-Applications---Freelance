# ai_responses/openai_gpt4.py

import os
import openai
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    logging.error("OpenAI API key not found in environment variables.")

openai.api_key = OPENAI_API_KEY

def get_gpt4_response(prompt):
    """
    Generate a response using OpenAI GPT-4.
    
    Args:
        prompt (str): The user input prompt.
    
    Returns:
        str: The AI-generated response or None if failed.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7,
        )
        ai_response = response['choices'][0]['message']['content'].strip()
        return ai_response
    except Exception as e:
        logging.error(f"Error generating GPT-4 response: {e}")
        return None
