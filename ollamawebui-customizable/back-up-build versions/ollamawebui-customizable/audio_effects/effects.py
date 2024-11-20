# audio_effects/effects.py

from pydub import AudioSegment
import logging
from utils.helpers import generate_unique_filename
import os

OUTPUT_DIR = os.path.join(os.getcwd(), "static", "audio")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def apply_reverb_effect(file_path):
    """
    Apply a reverb effect to the audio file using pydub.

    Args:
        file_path (str): Path to the input audio file.

    Returns:
        str: Path to the processed audio file or None if failed.
    """
    try:
        sound = AudioSegment.from_file(file_path)
        reverb = sound.overlay(sound, delay=500)  # Simple echo effect
        reverb_filename = generate_unique_filename("wav")
        reverb_file_path = os.path.join(OUTPUT_DIR, reverb_filename)
        reverb.export(reverb_file_path, format="wav")
        logging.info(f"Reverb effect applied. New file saved as {reverb_file_path}")
        return reverb_file_path

    except Exception as e:
        logging.error(f"Error applying reverb effect: {e}")
        return None

def apply_giantess_echo_effect(file_path):
    """
    Apply a Giantess Echo effect to the audio file using pydub.
    This effect lowers the pitch and adds a pronounced echo for a unique vocal quality.

    Args:
        file_path (str): Path to the input audio file.

    Returns:
        str: Path to the processed audio file or None if failed.
    """
    try:
        sound = AudioSegment.from_file(file_path)
        octaves = -0.5  # Pitch adjustment
        new_sample_rate = int(sound.frame_rate * (2.0 ** octaves))
        pitched_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
        pitched_sound = pitched_sound.set_frame_rate(44100)  # Standard frame rate

        echo = pitched_sound - 6  # Reduce volume of the echo by 6dB
        combined = pitched_sound.overlay(echo, position=500)  # Echo starts after 500ms

        giantess_filename = generate_unique_filename("wav")
        giantess_file_path = os.path.join(OUTPUT_DIR, giantess_filename)
        combined.export(giantess_file_path, format="wav")
        logging.info(f"Giantess Echo effect applied. New file saved as {giantess_file_path}")
        return giantess_file_path

    except Exception as e:
        logging.error(f"Error applying Giantess Echo effect: {e}")
        return None
