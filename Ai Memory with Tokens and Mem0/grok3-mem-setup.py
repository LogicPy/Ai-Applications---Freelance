import requests
import json
import re
import os
from collections import deque
import uuid
from mem0 import MemoryClient

# Configuration
API_KEY = "xai-******"
BASE_URL = "https://api.x.ai/v1/chat/completions"
MEM0_API_KEY = "m0-*****"  # Set your Mem0 API key
os.environ['MEM0_API_KEY'] = MEM0_API_KEY

# Initialize clients
mem0_client = MemoryClient()
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

class MemoryManager:
    """Manages memory storage and name extraction."""
    
    def __init__(self):
        self.memory_store = {}
        self.chat_buffer = deque(maxlen=5)
        self.user_name = None
        self._load_memory()

    def _load_memory(self):
        """Load persistent memory from file and search Mem0 for user name."""
        try:
            with open('memory.json', 'r') as f:
                memory_data = json.load(f)
                self.memory_store = memory_data.get('store', {})
                self.user_name = memory_data.get('user_name')
                if not self.user_name:
                    self._search_name_from_mem0()
        except FileNotFoundError:
            self._search_name_from_mem0()

    def _search_name_from_mem0(self):
        """Search Mem0 for user's name if not already set."""
        try:
            memories = mem0_client.search(query="What is the user's name?", user_id="current_user", limit=1)
            if memories and 'results' in memories and memories['results']:
                for mem in memories['results']:
                    extracted = self.extract_name_from_prompt(mem.get('memory', ''))
                    if extracted:
                        self.user_name = extracted
                        print(f"Loaded user_name '{self.user_name}' from Mem0.")
                        break
        except Exception as e:
            print(f"Error loading name from Mem0: {e}")

    def extract_name_from_prompt(self, prompt):
        """Extract name from prompt using regex patterns."""
        patterns = [
            r"(?:my name is|i'm|i am)\s+([A-Za-z]+(?:\s[A-Za-z]+)*)",
            r"(?:'|\")([A-Za-z]+)(?:'|\") here"
        ]
        for pattern in patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def save_chat(self, token, prompt, response):
        """Save chat to memory and update user name if detected."""
        self.memory_store[token] = {"prompt": prompt, "response": response}
        self.chat_buffer.append(token)
        if not self.user_name:
            extracted_name = self.extract_name_from_prompt(prompt)
            if extracted_name:
                self.user_name = extracted_name
        with open('memory.json', 'w') as f:
            json.dump({'store': self.memory_store, 'user_name': self.user_name}, f)

class GrokChat:
    """Handles interaction with the Grok-3 API and Mem0 integration."""
    
    def __init__(self, memory_manager):
        self.memory_manager = memory_manager

    def _fetch_context(self, prompt):
        """Fetch relevant context from Mem0."""
        messages = []
        if self.memory_manager.user_name:
            messages.append({"role": "system", "content": f"The user's name is {self.memory_manager.user_name}."})
        try:
            memories = mem0_client.search(query=prompt, user_id="current_user", limit=5)
            if memories and 'results' in memories:
                messages.append({"role": "system", "content": "Past context from memories:"})
                for mem in memories['results']:
                    role = mem.get('metadata', {}).get('type', 'system').replace('_message', '').replace('_response', '')
                    content = mem.get('memory', '')
                    if role in ['user', 'assistant']:
                        messages.append({"role": role, "content": content})
                    else:
                        messages.append({"role": "system", "content": content})
        except Exception as e:
            print(f"Error fetching context from Mem0: {e}")
        messages.append({"role": "user", "content": prompt})
        return messages

    def chat(self, prompt):
        """Interact with Grok-3 and save to Mem0."""
        data = {"model": "grok-3", "messages": self._fetch_context(prompt), "max_tokens": 28000}
        try:
            response = requests.post(BASE_URL, headers=HEADERS, json=data)
            response.raise_for_status()
            response_data = response.json()
            content = response_data['choices'][0]['message']['content']
            token = str(uuid.uuid4())
            self.memory_manager.save_chat(token, prompt, content)
            mem0_client.add([{"role": "user", "content": prompt}, {"role": "assistant", "content": content}], user_id="current_user")
            print("Messages added to Mem0.")
            response_text = f"Hey {self.memory_manager.user_name}!" if self.memory_manager.user_name else "Hey friend!"
            response_text += f" {content.strip()}"
            print("Grok 3 Response:", response_text)
            return token, response_text
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            return None, "Sorry, couldn’t connect to Grok-3."
        except Exception as e:
            print(f"Unexpected Error: {e}")
            return None, "Something went wrong."

def main():
    """Main loop to run the chatbot."""
    memory_manager = MemoryManager()
    chat_bot = GrokChat(memory_manager)
    
    print("Welcome to the Grok-3 Chatbot!")
    if memory_manager.user_name:
        print(f"It's great to see you again, {memory_manager.user_name}!")
    else:
        print("I don’t recall your name yet. Say 'My name is [Your Name]' to introduce yourself.")

    while True:
        prompt = input("Enter your prompt (or 'quit' to exit): ")
        if prompt.lower() == 'quit':
            print("Goodbye!")
            break
        _, _ = chat_bot.chat(prompt)
        print("-" * 30)

if __name__ == "__main__":
    main()
