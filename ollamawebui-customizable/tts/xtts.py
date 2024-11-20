# tts/xtts.py

import requests
import os
import logging
from utils.helpers import generate_unique_filename

OUTPUT_DIR = os.path.join(os.getcwd(), "static", "audio")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def send_tts_request_xtts(text, speaker_wav="female", language="en", output_filename=None):
    """
    Send a POST request to xtts-api-server to generate speech from text.

    Args:
        text (str): The text to convert to speech.
        speaker_wav (str): The speaker ID to use.
        language (str): Language code.
        output_filename (str): Optional. The name of the output audio file.

    Returns:
        str: Path to the saved audio file or None if failed.
    """
    url = 'http://localhost:8020/tts_to_audio/'  # Update if different
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }
    data = {
        "text": text,
        "speaker_wav": speaker_wav,
        "language": language
    }

    try:
        response = requests.post(url, headers=headers, json=data, stream=True)
        response.raise_for_status()

        if not output_filename:
            output_filename = generate_unique_filename("wav")
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        logging.info(f"Audio file saved as {output_path}")
        return output_path

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to generate speech via xtts-api-server: {e}")
        return None
