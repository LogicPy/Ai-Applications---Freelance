from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Flask is working!"

if __name__ == '__main__':
    app.run(debug=True, port=5001)

def create_app():
    app = Flask(__name__)

    # Configuration using environment variables
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///chats.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')

    # Initialize extensions with the app
    db.init_app(app)
    migrate = Migrate(app, db)

    # Ensure the database tables are created
    with app.app_context():
        db.create_all()

    # Define routes...

    return app
