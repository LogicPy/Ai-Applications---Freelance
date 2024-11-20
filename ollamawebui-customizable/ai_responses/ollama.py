# ai_responses/ollama.py

import subprocess
import json
import logging

def get_ollama_response(prompt):
    """
    Generate a response using Ollama Local AI.
    
    Args:
        prompt (str): The user input prompt.
    
    Returns:
        str: The AI-generated response or None if failed.
    """
    try:
        # Replace 'your_model_name' with the actual model name installed in Ollama
        result = subprocess.run(
            ["ollama", "run", "your_model_name", prompt],
            capture_output=True,
            text=True,
            check=True
        )
        ai_response = result.stdout.strip()
        return ai_response
    except subprocess.CalledProcessError as e:
        logging.error(f"Error generating Ollama response: {e}")
        return None
    except FileNotFoundError:
        logging.error("Ollama CLI not found. Ensure Ollama is installed and added to PATH.")
        return None
