import requests

API_KEY = "[api key]"
BASE_URL = "https://api.cohere.ai/generate"

def ask_cohere(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "command-xlarge",  # Adjust to Cohere's model offerings
        "prompt": prompt,
        "max_tokens": 50,
        "temperature": 0.7,
    }
    response = requests.post(BASE_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json().get("text", "No response text available.")
    else:
        print(f"Error: {response.status_code} - {response.json()}")
        return None

if __name__ == "__main__":
    user_input = input("You: ")
    response = ask_cohere(user_input)
    if response:
        print(f"AI (Cohere): {response}")
