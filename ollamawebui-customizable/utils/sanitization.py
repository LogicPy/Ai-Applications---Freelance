# utils/sanitization.py

import re

def sanitize_ai_message(message):
    """
    Remove unwanted spaces before apostrophes and fix specific split words without removing natural spaces.
    """
    # 1. Remove spaces before apostrophes (e.g., "I 'm" -> "I'm")
    message = re.sub(r"\s+'", "'", message)
    message = re.sub(r"'\s+", "'", message)

    # 2. Correct specific split words without affecting normal word spacing
    # Example: "ph er om one" -> "pheromone"
    message = re.sub(r"\bph\s+er\s+om\s+one\b", "pheromone", message, flags=re.IGNORECASE)
    message = re.sub(r"\bspr\s+ays\b", "sprays", message, flags=re.IGNORECASE)
    message = re.sub(r"\bsound\s+ly\b", "soundly", message, flags=re.IGNORECASE)

    # 3. Ensure AI's name is correctly formatted
    message = re.sub(r"\bJar\s+vis\b", "Jarvis", message, flags=re.IGNORECASE)

    # 4. Remove spaces before punctuation without affecting natural spaces
    message = re.sub(r'\s+([?.!,])', r'\1', message)

    return message

def post_process_ai_message(message):
    """
    Further corrects AI messages by fixing known space injection patterns.
    """
    # Correct specific known patterns
    corrections = {
        r"\bI\s+'m\b": "I'm",
        r"\byou\s+'re\b": "you're",
        r"\byou\s+'ve\b": "you've",
        r"\byou\s+'ll\b": "you'll",
        r"\bJar\s+vis\b": "Jarvis",
        r"\bph\s+er\s+om\s+one\b": "pheromone",
        r"\bspr\s+ays\b": "sprays",
        r"\bsound\s+ly\b": "soundly",
        # Add more as needed
    }

    for pattern, replacement in corrections.items():
        message = re.sub(pattern, replacement, message)

    # Removed overly aggressive space removal to prevent over-sanitization
    # Ensure spaces within words remain intact

    # Remove spaces before punctuation
    message = re.sub(r'\s+([?.!,])', r'\1', message)

    return message
