# ai_module.py

import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Dictionary to store user context
user_context = {}

def generate(user_id: str, prompt: str):
    """
    Generates an AI response based on the user's prompt and maintains context.

    Parameters:
    - user_id (str): Unique identifier for the user.
    - prompt (str): User's input prompt.

    Returns:
    - str: AI's response.
    """
    # Retrieve the context for the user
    context = user_context.get(user_id, "")

    # Update the context with the new prompt
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
                "content": "You are a role-playing AI. Your name is Jarvis. You're my AI girlfriend."
            },
            {
                "role": "user",
                "content": context
            }
        ]
    }

    # Send a request to the Ollama server
    try:
        logging.debug(f"Sending payload to Ollama: {payload}")
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()

        # Print the response text for debugging
        logging.debug(f"Response from Ollama: {response.text}")

        # Process each line of the response
        lines = response.text.strip().split('\n')
        combined_response = ""
        for line in lines:
            try:
                data = json.loads(line)
                if 'message' in data and 'content' in data['message']:
                    combined_response += data['message']['content']
            except json.JSONDecodeError as jde:
                logging.error(f"JSON decode error: {jde} - Line: {line}")
                continue

        # Update the context with the AI's response
        context += f"AI: {combined_response.strip()}\n"
        user_context[user_id] = context

        logging.debug(f"Combined AI response: {combined_response.strip()}")
        return combined_response.strip()
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err} - Response: {response.text}")
        return "Ai: Sorry, something went wrong. Please try again."
    except requests.exceptions.RequestException as req_err:
        logging.error(f"Request exception: {req_err}")
        return "Ai: Sorry, something went wrong. Please try again."
    except ValueError as val_err:
        logging.error(f"Value error: {val_err}")
        return "Ai: Sorry, something went wrong. Please try again."
