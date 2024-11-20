# utils/helpers.py

import uuid
import html
import os

def generate_unique_filename(extension="mp3"):
    """Generate a unique filename with the given extension."""
    unique_id = uuid.uuid4().hex[:8]
    return f"output-{unique_id}.{extension}"

def escape_html(text):
    """Escape HTML characters in text."""
    return html.escape(text)
