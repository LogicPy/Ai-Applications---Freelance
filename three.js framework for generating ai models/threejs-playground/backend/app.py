# app.py
from flask import Flask, send_from_directory, make_response
import os
# app.py
from flask_cors import CORS

app = Flask(__name__, static_folder='build', static_url_path='')
CORS(app)


@app.route('/')
def serve():
    response = make_response(send_from_directory(app.static_folder, 'index.html'))
    # Add Content Security Policy headers if needed
    # response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' https://cdnjs.cloudflare.com"
    return response

# app.py
@app.after_request
def set_csp(response):
    # app.py
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' https://cdnjs.cloudflare.com"
#    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' https://cdnjs.cloudflare.com"
    return response

# Serve static files
@app.route('/<path:path>')
def serve_static(path):
    if path.startswith('static/'):
        return send_from_directory(app.static_folder, path)
    else:
        # For client-side routing, serve index.html for all other routes
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
