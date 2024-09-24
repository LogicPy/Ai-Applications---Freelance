from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import spacy
import time

# Initialize the app and set up the database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///temp_mem.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Load Spacy NLP model
nlp = spacy.load('en_core_web_sm')

# Define the Memory model
class Memory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))
    created_time = db.Column(db.DateTime, default=datetime.utcnow)

# Define the Event model
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    event_time = db.Column(db.DateTime, nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.utcnow)
    recurrence = db.Column(db.String(50))

# Helper function to retrieve user events
def get_user_events(user_id):
    return Event.query.filter_by(user_id=user_id).all()

# Helper function to add events to the database
def add_event_to_db(user_id, description, event_time, recurrence=None):
    new_event = Event(user_id=user_id, description=description, event_time=event_time, recurrence=recurrence)
    db.session.add(new_event)
    db.session.commit()
    print(f"Event added: {new_event}")

# Event reminder check function
def check_and_send_reminders():
    while True:
        current_time = datetime.now()
        due_events = Event.query.filter(Event.event_time <= current_time).all()
        for event in due_events:
            send_reminder(event)
            if event.recurrence is None:
                db.session.delete(event)
        db.session.commit()
        time.sleep(60)

# Routes for interacting with events and memories
@app.route('/api/get_messages/<user_id>', methods=['GET'])
def get_messages(user_id):
    messages = Message.query.filter_by(user_id=user_id).all()
    return {
        'messages': [
            {'content': message.content, 'timestamp': message.timestamp.isoformat()} 
            for message in messages
        ]
    }, 200

@app.route('/')
def dashboard():
    user_events = get_user_events("default_user")
    return render_template('dashboard.html', events=user_events)

@app.route('/api/add_event', methods=['POST'])
def add_event():
    data = request.json
    try:
        new_event = Event(
            user_id=data['user_id'],
            description=data['description'],
            event_time=datetime.fromisoformat(data['event_time']),
            recurrence=data.get('recurrence')
        )
        db.session.add(new_event)
        db.session.commit()
        return {'message': 'Event added successfully'}, 200
    except Exception as e:
        print(f"Error adding event: {e}")
        return {'message': 'Error adding event'}, 500

@app.route('/api/get_events/<user_id>', methods=['GET'])
def get_events(user_id):
    events = Event.query.filter_by(user_id=user_id).all()
    event_list = [
        {
            'description': event.description,
            'event_time': event.event_time.isoformat(),
            'created_time': event.created_time.isoformat(),
            'recurrence': event.recurrence
        }
        for event in events
    ]
    return {'scheduled_events': event_list}, 200

@app.route('/memories')
def view_memories():
    memories = Memory.query.all()
    return render_template('memories.html', memories=memories)

@app.route('/api/add_memory', methods=['POST'])
def add_memory():
    data = request.json
    try:
        new_memory = Memory(
            user_id=data['user_id'],
            description=data['description'],
            category=data.get('category', 'general')
        )
        db.session.add(new_memory)
        db.session.commit()
        return {'message': 'Memory logged successfully'}, 200
    except Exception as e:
        print(f"Error logging memory: {e}")
        return {'message': 'Error logging memory'}, 500

if __name__ == "__main__":
    app.run(debug=True)
