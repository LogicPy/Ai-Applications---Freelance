# tts/elevenlabs.py

import requests
import os
import logging
from utils.helpers import generate_unique_filename

OUTPUT_DIR = os.path.join(os.getcwd(), "static", "audio")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def send_tts_request_elevenlabs(text, voice_id, output_filename=None):
    """
    Send a POST request to ElevenLabs API to generate speech from text.

    Args:
        text (str): The text to convert to speech.
        voice_id (str): The voice ID to use.
        output_filename (str): Optional. The name of the output audio file.

    Returns:
        str: Path to the saved audio file or None if failed.
    """
    XI_API_KEY = os.getenv("ELEVENLABS_API_KEY")
    if not XI_API_KEY:
        logging.error("ElevenLabs API key not found in environment variables.")
        return None

    sts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"

    headers = {
        "Accept": "audio/mpeg",
        "xi-api-key": XI_API_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    try:
        response = requests.post(sts_url, headers=headers, json=data, stream=True)
        response.raise_for_status()

        if not output_filename:
            output_filename = generate_unique_filename("mp3")
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        logging.info(f"Audio file saved as {output_path}")
        return output_path

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to generate speech via ElevenLabs: {e}")
        return None

def get_elevenlabs_voices():
    """
    Retrieve available voices from ElevenLabs.

    Returns:
        dict: Dictionary mapping voice names to their IDs.
    """
    XI_API_KEY = os.getenv("ELEVENLABS_API_KEY")
    if not XI_API_KEY:
        logging.error("ElevenLabs API key not found in environment variables.")
        return {}

    url = "https://api.elevenlabs.io/v1/voices"
    headers = {
        "xi-api-key": XI_API_KEY,
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        voices_data = response.json()
        voices = {voice['name']: voice['voice_id'] for voice in voices_data['voices']}
        return voices
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching voices from ElevenLabs API: {e}")
        return {}
