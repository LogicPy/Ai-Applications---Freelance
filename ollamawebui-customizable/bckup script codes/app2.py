from app import create_app
from waitress import serve

app = create_app()

if __name__ == '__main__':
    print("Starting Flask app with Waitress on port 5001")
    serve(app, host='0.0.0.0', port=5001)
