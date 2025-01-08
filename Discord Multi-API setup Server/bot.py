import discord
from discord.ext import commands
import os
import logging
import requests
import json
from dotenv import load_dotenv

# -----------------------------
# Configuration and Constants
# -----------------------------
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GROK_API_KEY = os.getenv('GROK_API_KEY', "YOUR_DEFAULT_API_KEY_HERE")

# Example for Nebius
NEBIUS_API_KEY = os.getenv('NEBIUS_API_KEY', "YOUR_DEFAULT_NEBIUS_KEY_HERE")
NEBIUS_BASE_URL = "https://api.studio.nebius.ai/v1/"

LM_BASE_URL = "http://localhost:1234/v1"
LM_API_KEY = "lm-studio"  # Example LM Studio key; store in env if needed

AI21_API_KEY = "[your api key for ai21]"  # or load from .env
AI21_API_URL = "https://api.ai21.com/studio/v1/chat/completions"

# AI21 key
AI21_API_KEY = os.getenv('AI21_API_KEY', "YOUR_DEFAULT_AI21_KEY_HERE")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("discord_lmstudio_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)

# Grok session config
GROK_URL = "https://api.x.ai/v1/chat/completions"
session_grok = requests.Session()
session_grok.headers.update({
    "Content-Type": "application/json",
    "Authorization": f"Bearer {GROK_API_KEY}",
    "User-Agent": "Mozilla/5.0"
})

# -----------------------------
# Optional: OpenAI-like clients
# -----------------------------
try:
    from openai import OpenAI  # or your custom local library
except ImportError:
    logger.warning("Make sure the openai-like client is installed or reachable.")

# If you have a Nebius client that mimics the OpenAI API:
nebius_client = OpenAI(
    base_url=NEBIUS_BASE_URL,
    api_key=NEBIUS_API_KEY
)

# -----------------------------
# AI21 Integration Function
# -----------------------------
def ask_ai21(prompt: str) -> str:
    """
    Sends a prompt to the AI21 J1-Jumbo API and returns the AI's response.
    """
    headers = {
        "Authorization": f"Bearer {AI21_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "jamba-1.5-large",  # Adjust if you need a different model
        "messages": [{"role": "user", "content": prompt}],
        "n": 1,
        "max_tokens": 2048,
        "temperature": 0.4,
        "top_p": 1,
        "stop": []
    }

    try:
        response = requests.post(AI21_API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise for HTTP errors
        response_data = response.json()
        generated_content = response_data.get('choices', [{}])[0] \
                                         .get('message', {}) \
                                         .get('content', "No response generated.")
        return generated_content.strip()
    except Exception as e:
        logging.error(f"Error communicating with AI21: {e}")
        return "I'm sorry, I couldn't process your request."

COHERE_API_KEY = "[your api key for cohere ai]"  # or load via environment
COHERE_BASE_URL = "https://api.cohere.ai/generate"

def ask_cohere(prompt: str) -> str:
    """
    Sends a prompt to Cohere's 'command-xlarge' model and returns the response text.
    """
    headers = {
        "Authorization": f"Bearer {COHERE_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "command-xlarge",  # Adjust as needed per Cohere's docs
        "prompt": prompt,
        "max_tokens": 50,
        "temperature": 0.7
    }

    try:
        response = requests.post(COHERE_BASE_URL, headers=headers, json=payload)
        if response.status_code == 200:
            json_data = response.json()
            # Cohere returns {"text":"..."} in many endpoints
            return json_data.get("text", "No response text available.").strip()
        else:
            logging.error(f"Cohere API error {response.status_code}: {response.text}")
            return "I'm sorry, I couldn't process your request."
    except Exception as e:
        logging.error(f"Error calling Cohere: {e}")
        return "An error occurred while communicating with the AI."


import requests
import os

# If you have python-dotenv, you can load from .env:
# from dotenv import load_dotenv
# load_dotenv()

AI21_API_KEY = os.getenv("AI21_API_KEY", "YOUR_AI21_KEY_HERE")
# Example: using the j2-jumbo-instruct model
AI21_MODEL = "j2-jumbo-instruct"

AI21_URL = f"https://api.ai21.com/studio/v1/{AI21_MODEL}/complete"

def ask_ai21_instruct(prompt: str) -> str:
    """
    Sends a single prompt to AI21's j2-jumbo-instruct model.
    Returns the generated text or an error message.
    """
    headers = {
        "Authorization": f"Bearer {AI21_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": prompt,
        "maxTokens": 200,   # Adjust as needed
        "temperature": 0.7,
        "topKReturn": 0,
        "topP": 1,
        # 'stop' can be specified if you need custom stop sequences
    }

    try:
        resp = requests.post(AI21_URL, headers=headers, json=payload)
        # Optional: print or log the status code & text for debugging
        print(f"[AI21] status_code={resp.status_code}, response={resp.text[:200]}...")

        if resp.status_code == 200:
            data = resp.json()
            # Typically: data["completions"][0]["data"]["text"]
            completions = data.get("completions", [])
            if completions:
                return completions[0]["data"]["text"].strip()
            else:
                return "No completions received from AI21."
        else:
            return f"AI21 returned an error ({resp.status_code}): {resp.text}"
    except Exception as e:
        return f"Error calling AI21: {e}"


# -----------------------------
# Nebius / LM Studio logic
# -----------------------------
async def fetch_ai_response(user_input: str) -> str:
    """
    Example function for LM Studio using an 'OpenAI-like' client.
    """
    try:
        client = OpenAI(base_url=LM_BASE_URL, api_key=LM_API_KEY)
        completion = client.chat.completions.create(
            model="opus-v1.2-llama-3-8b-GGUF",  # Adjust model name
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7,
            stream=True
        )
        response_text = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                response_text += chunk.choices[0].delta.content
        return response_text.strip()

    except Exception as e:
        logger.error(f"Error fetching AI response (LM Studio): {e}")
        return "I'm sorry, I couldn't process your request right now."

def communicate_with_ollama(user_id: str, prompt: str) -> str:
    # Define the API endpoint and headers
    api_url = "http://localhost:11434/api/chat"
    headers = {
        "Content-Type": "application/json"
    }

    # Create the JSON payload without context
    payload = {
        "model": "llama3.2",
        "messages": [
            {
                "role": "system",
                "content": "You are a role-playing AI. Your name is Britney. You're my AI girlfriend."
            },
            {
                "role": "user",
                "content": prompt  # Use the current prompt only
            }
        ]
    }

    # Send a request to the Ollama server
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()

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

        return combined_response.strip()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error communicating with Ollama: {e}")
        return "An error occurred while communicating with the AI."
    except ValueError as e:
        logger.error(f"JSON decode error: {e}")
        return "An error occurred while processing the AI's response."


def communicate_with_nebius(user_message: str) -> str:
    """
    Communicates with the Nebius (Llama3) AI model.
    """
    try:
        completion = nebius_client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-70B-Instruct",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": user_message},
            ],
            temperature=0.6
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error communicating with Nebius: {e}")
        return "I'm sorry, I couldn't process your request right now."

# -----------------------------
# Groq Integration
# -----------------------------
os.environ['GROQ_API_KEY'] = '[your groq api key]'
groq_api_url = "https://api.groq.com/openai/v1/chat/completions"
groq_api_key = os.environ.get('GROQ_API_KEY')

def get_groq_response(user_message: str) -> str:
    """
    Communicates with the Groq AI model via its API.
    """
    payload = {
        "messages": [
            {"role": "user", "content": user_message}
        ],
        "model": "llama-3.3-70b-specdec"
    }
    try:
        response = requests.post(
            groq_api_url,
            json=payload,
            headers={"Authorization": f"Bearer {groq_api_key}"}
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        logger.error(f"Error communicating with Groq: {e}")
        return "I'm sorry, I couldn't process your request right now."

# -----------------------------
# Grok Integration
# -----------------------------
def communicate_with_grok(api_key: str, user_message: str) -> str:
    """
    Communicates with the Grok (x.ai) API.
    """
    data = {
        "messages": [
            {"role": "system", "content": "You are a test assistant."},
            {"role": "user", "content": user_message}
        ],
        "model": "grok-beta",
        "stream": False,
        "temperature": 0
    }
    try:
        response = session_grok.post(GROK_URL, json=data)
        if response.status_code == 200:
            json_response = response.json()
            if "choices" in json_response and len(json_response["choices"]) > 0:
                return json_response["choices"][0]["message"]["content"].strip()
            else:
                logger.warning(f"Grok API returned unexpected JSON: {json_response}")
                return "I'm sorry, but I couldn't parse the AI response right now."
        else:
            logger.error(f"Grok API error {response.status_code}: {response.text}")
            return "I'm sorry, I couldn't process your request right now."
    except requests.RequestException as e:
        logger.error(f"Error calling Grok: {e}")
        return "An error occurred while communicating with the AI."

# -----------------------------
# Bot Commands
# -----------------------------
user_model_selection = {}

@bot.command(name="menu")
async def menu(ctx):
    """
    Displays the AI platforms menu and allows the user to select a model.
    """
    menu_message = """
**AI Platforms Menu**:
1️⃣: Groq
2️⃣: Grok
3️⃣: Nebius
4️⃣: Ollama
5️⃣: LM Studio
6️⃣: AI21
7️⃣: Cohere
0️⃣ (default): GPT-4

Use `!select <number>` to choose.
"""
    await ctx.send(menu_message)

@bot.command(name="select")
async def select_model(ctx, model_number: int):
    """
    Allows the user to select their desired AI platform.
    """
    user_id = ctx.author.id
    model_map = {
        1: "Groq",
        2: "Grok",
        3: "Nebius",
        4: "Ollama",
        5: "LM Studio",
        6: "AI21",
        7: "Cohere",
        0: "GPT-4"
    }

    selected_model = model_map.get(model_number, None)
    if selected_model:
        user_model_selection[user_id] = selected_model
        logger.info(f"User {user_id} selected model: {selected_model}")
        await ctx.send(f"You've selected **{selected_model}**. Start chatting!")
    else:
        await ctx.send("Invalid selection. Please select a valid model using `!select <number>`.")


@bot.command(name="chat")
async def chat_with_model(ctx, *, user_message: str):
    """
    Handles user input and sends it to the selected AI platform.
    """
    user_id = ctx.author.id
    selected_model = user_model_selection.get(user_id, "GPT-4")  # Default to GPT-4

    async with ctx.typing():
        try:
            if selected_model == "AI21":
                response = ask_ai21(user_message)
            if selected_model == "Ollama":
                response = communicate_with_ollama(str(user_id), message.content)
            elif selected_model == "Grok":
                response = communicate_with_grok("Your_Grok_API_Key", user_message)
            elif selected_model == "Nebius":
                response = communicate_with_nebius(user_message)
            elif selected_model == "Groq":
                response = get_groq_response(user_message)
            elif selected_model == "LM Studio":
                response = await fetch_ai_response(user_message)  # LM Studio
            elif selected_model == "Cohere":
                response = ask_cohere(message.content)
            else:
                response = "Selected model is not yet implemented!"
        except Exception as e:
            response = f"An error occurred while processing your request: {e}"

    await ctx.send(f"**{selected_model} AI's Response:** {response}")

@bot.event
async def on_ready():
    """
    Event handler triggered when the bot is ready.
    """
    logger.info(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_message(message):
    """
    Event handler triggered on every message in the server that isn't a bot command.
    If the user has selected a model, it responds with that model.
    """
    if message.author == bot.user:
        return

    user_id = message.author.id
    selected_model = user_model_selection.get(user_id, "GPT-4")

    if message.content.startswith("!"):
        await bot.process_commands(message)
        return

    async with message.channel.typing():
        try:
            if selected_model == "AI21":
                response = ask_ai21(message.content)
            if selected_model == "Ollama":
                response = communicate_with_ollama(str(user_id), message.content)
            elif selected_model == "Grok":
                response = communicate_with_grok("Your_Grok_API_Key", message.content)
            elif selected_model == "Nebius":
                response = communicate_with_nebius(message.content)
            elif selected_model == "Groq":
                response = get_groq_response(message.content)
            elif selected_model == "LM Studio":
                response = await fetch_ai_response(message.content)
            elif selected_model == "Cohere":
                response = ask_cohere(message.content)
 
            else:
                response = "Selected model is not yet implemented!"
        except Exception as e:
            response = f"An error occurred while processing your request: {e}"

    await message.channel.send(f"**{selected_model} AI's Response:** {response}")

def main():
    if not TOKEN:
        logger.error("DISCORD_TOKEN is not set. Please configure it in your .env")
        return

    try:
        bot.run(TOKEN)
    except Exception as e:
        logger.critical(f"Failed to run the bot: {e}")

if __name__ == "__main__":
    main()
