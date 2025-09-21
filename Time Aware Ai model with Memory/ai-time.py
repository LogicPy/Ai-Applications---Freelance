# -- Config --
API_KEY = ""
from openai import OpenAI
from datetime import datetime
import threading
import time
import re
from circular_buffer import CircularBuffer
from playsound import playsound

# -- Config --
# Please replace with your actual API key and other details as needed.
# It is recommended to use environment variables for sensitive data like API keys.
API_KEY = "[API_Key]"  # IMPORTANT: Replace with your actual API key
BASE_URL = "https://api.studio.nebius.ai/v1/"
MODEL_ID = "deepseek-ai/DeepSeek-V3-0324-fast"
SOUND_FILE = "alert_sound.mp3"

# -- AI Client Setup --
client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY
)

# -- Circular Buffer Setup --
conversation_buffer = CircularBuffer(capacity=10)  # Adjust capacity as needed

# -- System Prompt Builder --
def build_system_prompt():
    current_time = datetime.now().strftime("%I:%M %p")
    conversation_history = "\n".join(conversation_buffer.get_all())
    return f"""
You are an emotionally expressive AI assistant with time awareness.
The current time is {current_time}.
If the user asks about the time, respond naturally using this info. Examples:
- 'Sure! It's currently {current_time}.'
- 'Right now, it's {current_time}—feel free to set a reminder or ask for help.'
Avoid saying you lack real-time capabilities.

Conversation History:
{conversation_history}
"""

def parse_time_delay(user_input):
    """
    Parses the user input to extract the delay and convert it to seconds.

    :param user_input: The user input string.
    :return: The delay in seconds.
    """
    # Regex to capture the delay and unit
    pattern = r"remind me in (\d+) (seconds?|minutes?|hours?|days?|weeks?) to (.+)"
    match = re.match(pattern, user_input, re.IGNORECASE)

    if not match:
        raise ValueError("Invalid reminder format.")

    delay = int(match.group(1))
    unit = match.group(2).lower()
    reminder_message = match.group(3)

    # Convert delay to seconds based on the unit
    if unit.startswith("second"):
        pass  # Already in seconds
    elif unit.startswith("minute"):
        delay *= 60
    elif unit.startswith("hour"):
        delay *= 3600
    elif unit.startswith("day"):
        delay *= 86400
    elif unit.startswith("week"):
        delay *= 604800
    else:
        raise ValueError("Unknown time unit.")

    return delay, reminder_message

def schedule_alert(message, delay_seconds):
    def alert():
        time.sleep(delay_seconds)
        print(f"\n[ALERT] 🔔 Reminder: {message}\nYou: ", end='')
        try:
            playsound(SOUND_FILE)  # Play the sound file
        except Exception as e:
            print(f"[Sound Error] Could not play sound: {e}")
    threading.Thread(target=alert, daemon=True).start()

# -- Main Loop --
while True:
    user_input = input("You: ")

    # Exit condition
    if user_input.lower() in ["exit", "quit"]:
        print("Goodbye!")
        break

    # Check for alert scheduling command
    if user_input.lower().startswith("remind me in"):
        try:
            delay, reminder_message = parse_time_delay(user_input)
            schedule_alert(reminder_message, delay)
            print(f"[Scheduler] Set reminder in {delay} seconds: '{reminder_message}'")
            continue  # Skip the rest of the loop for reminder commands
        except Exception as e:
            print(f"[Scheduler Error] Could not parse reminder: {e}")
            continue  # Skip the rest of the loop if there's an error

    # Add user input to conversation buffer
    conversation_buffer.add(f"You: {user_input}")

    # Create system prompt dynamically
    system_prompt = build_system_prompt()

    # --- MODIFICATION START: Enabled streaming ---
    # Send request to AI with stream=True
    stream = client.chat.completions.create(
        model=MODEL_ID,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        temperature=0.6,
        stream=True,  # This is the key change to enable streaming
    )

    # --- MODIFICATION START: Handle streamed response ---
    ai_response_chunks = []
    print("AI: ", end="", flush=True)
    for chunk in stream:
        # The actual text content is in choices[0].delta.content
        if chunk.choices[0].delta.content is not None:
            response_chunk = chunk.choices[0].delta.content
            print(response_chunk, end="", flush=True)
            ai_response_chunks.append(response_chunk)
    print() # for a new line after the full response has been printed

    # Join the chunks to form the full response for the conversation buffer
    ai_response = "".join(ai_response_chunks)
    # --- MODIFICATION END ---


    # Add AI response to conversation buffer
    conversation_buffer.add(f"AI: {ai_response}")
    
    
