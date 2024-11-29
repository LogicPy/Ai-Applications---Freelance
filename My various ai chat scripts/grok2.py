import requests
import json

url = "https://api.x.ai/v1/chat/completions"
api_key = "Your_API_Key_here"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
}

data = {
    "messages": [
        {"role": "system", "content": "You are a test assistant."},
        {"role": "user", "content": "Testing. Just say hi and hello world and nothing else."}
    ],
    "model": "grok-beta",
    "stream": False,
    "temperature": 0
}

try:
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        # Parse the JSON response to get the message content
        json_response = response.json()
        # Extract the message content from the JSON
        message_content = json_response['choices'][0]['message']['content']
        print("Assistant's Response:", message_content)
    else:
        print("Failed to fetch data from the API:", response.status_code)
        print("Response Content:", response.text)
except requests.RequestException as e:
    print(f"An error occurred: {e}")