import requests

# Replace 'YOUR_API_KEY' with your actual API key
api_key = "[api key]"
url = "https://api.ai21.com/studio/v1/chat/completions"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# Get user input for the message
user_message = input("You: ")

# Prepare the payload
data = {
    "model": "jamba-1.5-large",
    "messages": [
        {
            "role": "user",
            "content": user_message
        }
    ],
    "documents": [],
    "tools": [],
    "n": 1,
    "max_tokens": 2048,
    "temperature": 0.4,
    "top_p": 1,
    "stop": [],
    "response_format": {"type": "text"}
}

# Make the POST request
response = requests.post(url, headers=headers, json=data)

# Handle the response
if response.ok:
    print("Assistant:", response.json().get("choices")[0]["message"]["content"])
else:
    print(f"HTTP Error {response.status_code}:", response.text)
