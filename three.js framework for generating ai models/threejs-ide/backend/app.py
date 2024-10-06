# backend/app.py

import os
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from groq import Groq  # Ensure Groq SDK is installed
import bleach
import logging

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Retrieve API keys from environment variables
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
API_KEY = os.getenv('API_KEY')

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

def extract_code(response):
    """
    Extracts code enclosed within triple backticks and specified language.
    """
    code_pattern = r'```javascript\s([\s\S]*?)```'
    match = re.search(code_pattern, response)
    if match:
        return match.group(1).strip()
    return None

# Route to handle prompt from query string
@app.route('/query', methods=['GET'])
def handle_query():
    # Extract the prompt from the query string
    prompt = request.args.get('prompt', default='', type=str)

    if not prompt:
        return jsonify({"error": "No prompt provided!"})

    try:
        # Generate the Three.js code from the prompt
        three_js_code = your_prompt_processing_function(prompt)
        generate_threejs()
        # Pass the generated Three.js code to the frontend via render_template or jsonify depending on the UI.
        return render_template('threejs_renderer.html', code=three_js_code)  # This is assuming you have a front-end page for rendering the Three.js code.

    except Exception as e:
        return jsonify({"error": f"Failed to generate scene: {str(e)}"})


@app.route('/api/generate-threejs', methods=['POST'])
def generate_threejs():
    """
    Endpoint to generate Three.js code based on user prompts.
    """
    # Verify API Key
    client_api_key = request.headers.get('x-api-key')
    if client_api_key != API_KEY:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    prompt = bleach.clean(data.get('prompt', ''))

    # Define the AI prompt for Groq
    ai_prompt = f"""
    You are an AI expert in creating 3D scenes using Three.js within a React environment. When given a description of a 3D environment or specific objects, generate the corresponding Three.js code to render it. Ensure the code is functional, well-commented, uses proper JavaScript syntax, and is compatible with being executed inside a React component using the Function constructor. Do not include import statements, DOM manipulations, or redefine 'scene', 'camera', or 'renderer'. Assume that Three.js is already imported and that a scene, camera, and renderer are available.

    Always ensure compatibility with the latest version of Three.js. Specifically:
   - **Prefix all Three.js objects with the `THREE.` namespace**. For example, use `THREE.BoxGeometry`, `THREE.Mesh`, etc., instead of `BoxGeometry` or `Mesh`.
   - **Avoid using deprecated methods**, such as `SplineCurve3`. Replace them with modern equivalents, such as `CatmullRomCurve3` when constructing curves or similar geometries.
   - **Filter and handle outdated functionalities**. If any deprecated methods are encountered in the description, automatically substitute them with the appropriate alternative from the latest Three.js documentation.

    For example:
    - `BoxBufferGeometry` should be replaced with `THREE.BoxGeometry`.
    - `SplineCurve3` should be replaced with `THREE.CatmullRomCurve3`.

    Automatically detect and replace these outdated keywords in the generated Three.js code to ensure compatibility with the latest version.

    Description: {prompt}

    Please provide only the Three.js code enclosed within triple backticks and specify the language as JavaScript. Do not include any additional text or explanations.

    Three.js Code:
    ```javascript
    """


    try:
        # Generate response from Groq
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": ai_prompt
                }
            ],
            model="llama3-70b-8192",  # Replace with the appropriate model if different
        )

        # Extract the generated code from the AI response
        full_response = chat_completion.choices[0].message.content.strip()
        logger.info(f"AI Response:\n{full_response}")
        code = extract_code(full_response)

        if not code:
            logger.error("Failed to extract code from AI response.")
            return jsonify({'error': 'Failed to extract code from AI response.'}), 500

        logger.info(f"Extracted Code:\n{code}")
        return jsonify({'code': code})
    except Exception as e:
        logger.exception("Error generating Three.js code")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Run the Flask app on port 5210
    app.run(host='0.0.0.0', port=5210, debug=True)
