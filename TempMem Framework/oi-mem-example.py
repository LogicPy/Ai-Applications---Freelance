import requests
import json
from datetime import datetime, timedelta
import threading
import time
# Optionally, import dateparser for parsing natural language dates
import dateparser
import parsedatetime
from threading import Lock
import dateparser.search
import dateparser
import dateparser.search
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
import threading
from plyer import notification
import smtplib
from email.mime.text import MIMEText
import spacy
import json

nlp = spacy.load('en_core_web_sm')

# In-memory storage for user contexts
# Dictionary to store user context
user_context = {}

# List to store scheduled events
scheduled_events = []

app = Flask(__name__)

scheduled_events_lock = Lock()
user_context_lock = Lock()


def save_scheduled_events():
    with scheduled_events_lock:
        with open('scheduled_events.json', 'w') as f:
            json.dump([{
                'user_id': event['user_id'],
                'description': event['description'],
                'event_time': event['event_time'].isoformat(),
                'created_time': event['created_time'].isoformat(),
                'recurrence': event['recurrence']
            } for event in scheduled_events], f)

def load_scheduled_events():
    global scheduled_events
    try:
        with open('scheduled_events.json', 'r') as f:
            events = json.load(f)
            with scheduled_events_lock:
                scheduled_events = [{
                    'user_id': event['user_id'],
                    'description': event['description'],
                    'event_time': datetime.fromisoformat(event['event_time']),
                    'created_time': datetime.fromisoformat(event['created_time']),
                    'recurrence': event.get('recurrence')
                } for event in events]
    except FileNotFoundError:
        scheduled_events = []

# Load events at startup
load_scheduled_events()

# Save events after adding/removing
def add_event(event):
    with scheduled_events_lock:
        scheduled_events.append(event)
        save_scheduled_events()

def send_reminder(event):
    try:
        # Existing reminder code...
        
        # Reschedule if recurring
        if event.get('recurrence') == 'daily':
            event['event_time'] += timedelta(days=1)
            with scheduled_events_lock:
                scheduled_events.append(event)
                save_scheduled_events()
    except Exception as e:
        print(f"Error in send_reminder: {e}")
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    with scheduled_events_lock:
        return render_template('index.html', events=scheduled_events)

@app.route('/add', methods=['POST'])
def add():
    description = request.form['description']
    time_str = request.form['time']
    event_time = dateparser.parse(time_str, settings={'PREFER_DATES_FROM': 'future'})
    if event_time:
        event = {
            "user_id": "default_user",
            "description": description,
            "event_time": event_time.replace(microsecond=0),
            "created_time": datetime.now().replace(microsecond=0),
            "recurrence": request.form.get('recurrence')
        }
        with scheduled_events_lock:
            scheduled_events.append(event)
            save_scheduled_events()
        return redirect(url_for('index'))
    else:
        return "Invalid time format", 400

def list_reminders(user_id):
    with scheduled_events_lock:
        user_events = [event for event in scheduled_events if event['user_id'] == user_id]
        for event in user_events:
            print(f"{event['description']} at {event['event_time']}")

def delete_reminder(user_id, description):
    with scheduled_events_lock:
        for event in scheduled_events:
            if event['user_id'] == user_id and event['description'] == description:
                scheduled_events.remove(event)
                # Also remove from persistent storage if implemented
                print(f"Deleted reminder: {description}")
                return
        print("Reminder not found.")


def send_email_reminder(event):
    try:
        msg = MIMEText(f"Reminder: {event['description']} (scheduled for {event['event_time']}) is due now.")
        msg['Subject'] = 'AI Reminder'
        msg['From'] = 'your_email@example.com'
        msg['To'] = 'user_email@example.com'

        with smtplib.SMTP('smtp.example.com', 587) as server:
            server.starttls()
            server.login('your_email@example.com', 'password')
            server.send_message(msg)

        print(f"Email sent for reminder: {event['description']}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def is_scheduling_request(prompt):
    keywords = ["remind me", "schedule", "set an alarm", "note to self", "set a reminder", "remind"]
    return any(keyword in prompt.lower() for keyword in keywords)

def extract_event_details(prompt):
    if 'remind me to' in prompt.lower():
        event_text = prompt.lower().split('remind me to', 1)[1].strip()
    else:
        event_text = prompt.lower()

    doc = nlp(event_text)
    event_time = None
    time_expression = ""

    for ent in doc.ents:
        if ent.label_ in ["TIME", "DATE"]:
            time_expression = ent.text
            event_time = dateparser.parse(ent.text, settings={'PREFER_DATES_FROM': 'future'})

    if event_time:
        event_description = event_text.replace(time_expression, '').strip()
        event_description = event_description.rstrip('.,;:!?')
        return event_description, event_time
    else:
        return event_text.rstrip('.,;:!?'), None

def send_reminder(event):
    try:
        # Existing code...
        print(f"\nAI: {reminder_message}")
    except Exception as e:
        print(f"Error in send_reminder: {e}")

def check_scheduled_events():
    print("Event checker thread started.")
    while True:
        current_time = datetime.now().replace(microsecond=0)
        with scheduled_events_lock:
            if scheduled_events:
                # print(f"Checking scheduled events at {current_time}.")
                pass
            due_events = [event for event in scheduled_events if event['event_time'] <= current_time]
            for event in due_events:
                print(f"Event due: {event}")
                send_reminder(event)
                scheduled_events.remove(event)
        time.sleep(1)  # Check every second
        

"""
Messages Table:
- id (primary key)
- timestamp (datetime)
- sender (text)
- content (text)
"""

def generate(user_id: str, prompt: str):
    # Initialize user's memory if not already present
    if user_id not in user_context:
        user_context[user_id] = []

    # Check if the prompt is a scheduling request
    if is_scheduling_request(prompt):
        event_description, event_time = extract_event_details(prompt)
        if event_time and event_time > datetime.now():
            # Store the event and confirm
            event = {
                "user_id": user_id,
                "description": event_description,
                "event_time": event_time.replace(microsecond=0),  # Remove microseconds
                "created_time": datetime.now().replace(microsecond=0),
                "recurrence": None  # Extend as needed
            }
            with scheduled_events_lock:
                scheduled_events.append(event)
                print(f"Scheduled events: {scheduled_events}")  # Debug statement

            confirmation_message = f"Got it! I'll remind you to {event_description} at {event_time.strftime('%Y-%m-%d %H:%M')}."
            ai_message = {
                "timestamp": datetime.now(),
                "role": "assistant",
                "content": confirmation_message
            }
            with user_context_lock:
                user_context[user_id].append(ai_message)
            print(f"\nAI: {confirmation_message}")
            return
        else:
            # Unable to parse time or time is in the past
            error_message = "I'm sorry, I couldn't understand the time you mentioned or it's in the past. Could you please specify it more clearly?"
            ai_message = {
                "timestamp": datetime.now(),
                "role": "assistant",
                "content": error_message
            }
            with user_context_lock:
                user_context[user_id].append(ai_message)
            print(f"\nAI: {error_message}")
            return

    # Existing code for handling regular user messages
    user_message = {
        "timestamp": datetime.now(),
        "role": "user",
        "content": prompt
    }
    with user_context_lock:
        user_context[user_id].append(user_message)

    # Retrieve the last N messages (e.g., 20)
    recent_messages = user_context[user_id][-20:]

    # Format messages for the AI prompt
    formatted_messages = ""
    for msg in recent_messages:
        timestamp = msg['timestamp'].strftime("%Y-%m-%d %H:%M")
        role = "User" if msg['role'] == "user" else "Assistant"
        formatted_messages += f"[{timestamp}] {role}: {msg['content']}\n"

    # Define the API endpoint and headers
    api_url = "http://localhost:11434/api/chat"
    headers = {
        "Content-Type": "application/json"
    }

    # Create the payload with context
    payload = {
        "model": "llama3",
        "messages": [
            {
                "role": "system",
                "content": "You are an AI assistant that keeps track of time in conversations. Use the timestamps provided to understand the timing of events and reference them in your responses when appropriate."
            },
            {
                "role": "user",
                "content": formatted_messages
            }
        ]
    }

    # Send a request to the AI server
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()

        # Process each line of the response
        combined_response = ""
        lines = response.text.strip().split('\n')
        for line in lines:
            try:
                data = json.loads(line)
                if 'response' in data:
                    combined_response += data['response']
                elif 'message' in data and 'content' in data['message']:
                    combined_response += data['message']['content']
            except json.JSONDecodeError:
                continue

        ai_content = combined_response.strip()

        # Add the AI's response to the user's memory
        ai_message = {
            "timestamp": datetime.now(),
            "role": "assistant",
            "content": ai_content
        }
        with user_context_lock:
            user_context[user_id].append(ai_message)

        print('\nAI: ' + ai_content)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")


def send_reminder(event):
    try:
        user_id = event['user_id']
        reminder_message = f"Reminder: {event['description']} (scheduled for {event['event_time'].strftime('%Y-%m-%d %H:%M')}) is due now."
        ai_message = {
            "timestamp": datetime.now(),
            "role": "assistant",
            "content": reminder_message
        }
        with user_context_lock:
            user_context[user_id].append(ai_message)
        print(f"\nAI: {reminder_message}")
    except Exception as e:
        print(f"Error in send_reminder: {e}")

def is_scheduling_request(prompt):
    keywords = ["remind me", "schedule", "set an alarm", "note to self"]
    return any(keyword in prompt.lower() for keyword in keywords)

def extract_event_details(prompt):
    # Remove 'Remind me to' from the prompt
    if 'remind me to' in prompt.lower():
        event_text = prompt.lower().split('remind me to', 1)[1].strip()
    else:
        event_text = prompt.lower()

    # Handle 'in X minutes/hours' phrases
    if 'in ' in event_text:
        parts = event_text.split('in ', 1)
        event_description = parts[0].strip().rstrip('.,;:!?')
        time_expression = parts[1].strip().rstrip('.,;:!?')
        # Parse the time expression
        if 'minute' in time_expression:
            number = int(''.join(filter(str.isdigit, time_expression)))
            event_time = datetime.now() + timedelta(minutes=number)
        elif 'hour' in time_expression:
            number = int(''.join(filter(str.isdigit, time_expression)))
            event_time = datetime.now() + timedelta(hours=number)
        else:
            event_time = None
    else:
        # Use search_dates to find date/time expressions
        search_result = dateparser.search.search_dates(
            event_text,
            settings={
                'PREFER_DATES_FROM': 'future',
                'RELATIVE_BASE': datetime.now()
            }
        )

        if search_result:
            # The last date found is assumed to be the event time
            time_expression, event_time = search_result[-1]
            # Remove the time expression from the event description
            event_description = event_text.replace(time_expression, '').strip()
            event_description = event_description.rstrip('.,;:!?')
        else:
            event_description = event_text.rstrip('.,;:!?')
            event_time = None

    return event_description, event_time


if __name__ == "__main__":
    # Start the scheduled event checker in a separate thread
    event_checker_thread = threading.Thread(target=check_scheduled_events, daemon=True)
    event_checker_thread.start()

    user_id = "default_user"
    while True:
        prompt = input("Enter your prompt: ")
        generate(user_id, prompt)

        

