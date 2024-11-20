# utils/emotion.py

from textblob import TextBlob

def detect_emotion(text):
    """
    Detect emotion from text using TextBlob's sentiment analysis.

    Args:
        text (str): The input text.

    Returns:
        str: Detected emotion.
    """
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    if polarity > 0.5:
        return 'excited'
    elif polarity > 0:
        return 'happy'
    elif polarity == 0:
        return 'neutral'
    elif polarity > -0.5:
        return 'sad'
    else:
        return 'angry'
