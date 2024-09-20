import requests
import json
from mem0 import MemoryClient

client = MemoryClient(api_key="m0-API_Key")

# Dictionary to store user context
user_context = {}

def generate(user_id: str, prompt: str):
    # Retrieve the context for the user
    context = user_context.get(user_id, "")
    
    # Update the context with the new prompt
    context += f" User: {prompt}\n"
    user_input = context
    user_message = {"role": "user", "content": user_input}
    client.add([user_message], user_id="ollama")

    # Define the API endpoint and headers
    api_url = "http://localhost:11434/api/chat"
    headers = {
        "Content-Type": "application/json"
    }

    # Create the JSON payload with context
    payload = {
        "model": "llama3",
        "messages": [
            {
                "role": "system",
                "content": ""
            },
            {
                "role": "user",
                "content": context
            }
        ]
    }

    # Send a request to the Ollama server
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        
        # Print the response text for debugging
       # print(response.text)
        
        # Process each line of the response
        lines = response.text.strip().split('\n')
        combined_response = ""
        for line in lines:
            try:
                data = json.loads(line)
                if 'message' in data and 'content' in data['message']:
                    combined_response += data['message']['content']
            except json.JSONDecodeError:
                continue

        # Update the context with the AI's response
        context += f" AI: {combined_response.strip()}\n"
        user_context[user_id] = context

        # Sort messages by timestamp (assuming there's a timestamp field)
        previous_messages = client.get_all(user_id="ollama")

    # Sort messages by timestamp (assuming there's a timestamp field)

        # Take the 20 most recent messages
        recent_messages = previous_messages[:20]
        print(recent_messages)
        # Iterate over recent messages and extract content
        messages = []
        for user_msg in recent_messages:
            if 'content' in user_msg:
                if user_msg['role'] == "user":
                    role = "User"
                else:
                    role = "Assistant"
                    continue  # Add this line to skip processing AI messages

                messages.append({"role": role, "content": user_msg['content'], user_id:"ollama"})

        # Format and concatenate previous messages
        formatted_messages = ""
        for msg in messages:
            formatted_messages += f"{msg['role']}: {msg['content']}\n"

        # Update the context with the AI's response and previous messages
        context += f"{formatted_messages}{combined_response.strip()}\n"
        user_message = {"role": "user", "content": user_input}
        user_context[user_id] = context


        print('\n\nAi: ' + combined_response.strip())
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    except ValueError as e:
        print(f"JSON decode error: {e}")

if __name__ == "__main__":
    user_id = "default_user"  # In a real application, you might want to use a unique ID for each user
    while True:
        prompt = input("Enter your prompt: ")
        generate(user_id, prompt)
