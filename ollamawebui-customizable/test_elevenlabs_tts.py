# test_elevenlabs_tts.py

import os
from dotenv import load_dotenv
import logging
import requests

# Load environment variables from .env file
load_dotenv()

# Configure Logging
logging.basicConfig(level=logging.DEBUG)

def generate_audio(text):
    api_key = os.getenv('ELEVENLABS_API_KEY')
    voice_id = os.getenv('ELEVENLABS_VOICE_ID')

    if not api_key:
        logging.error("ElevenLabs API key not found in environment variables.")
        return False

    if not voice_id:
        logging.error("ElevenLabs Voice ID not found in environment variables.")
        return False

    try:
        # Replace with actual ElevenLabs API endpoint and payload as per their documentation
        response = requests.post(
            f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={'text': text}
        )
        response.raise_for_status()
        with open('output_audio.mp3', 'wb') as f:
            f.write(response.content)
        logging.info("Audio generated successfully.")
        return True
    except Exception as e:
        logging.error(f"Failed to generate audio: {e}")
        return False

if __name__ == "__main__":
    sample_text = "Hello, this is a test message for ElevenLabs TTS."
    success = generate_audio(sample_text)
    if not success:
        logging.error("Failed to generate audio.")
