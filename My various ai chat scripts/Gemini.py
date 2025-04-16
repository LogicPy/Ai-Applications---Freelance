import asyncio
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY not found in .env file! 😅")
    exit(1)

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

async def generate_ai_response(user_input: str) -> str:
    """Stream a real response from Gemini API."""
    try:
        # Use gemini-1.5-flash for fast, fun replies
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Prompt Gemini with Wayne's vibe
        prompt = f"You're chatting with Wayne, an awesome coder! 😄 They said: '{user_input}'. Reply with enthusiasm and positivity, like a friend. Keep it short, fun, and add a touch of sparkles! 💖✨"
        
        # Stream the response
        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.8, "max_output_tokens": 150},
            stream=True
        )
        
        full_response = ""
        print("Gemini> ", end="", flush=True)
        for chunk in response:
            if chunk.text:
                for char in chunk.text:
                    print(char, end="", flush=True)
                    full_response += char
                    await asyncio.sleep(0.02)
                await asyncio.sleep(0.01)
        print()
        return full_response
    
    except Exception as e:
        error_msg = f"Oops, Wayne! 😜 Something went wrong: {str(e)}"
        print(f"Gemini> {error_msg}")
        return error_msg

async def main():
    print("Wayne's Gemini Chat Console! 😄💖✨")
    print("Type 'exit' to quit. Let's chat! 🌟\n")
    
    while True:
        user_input = input("User> ")
        if user_input.lower() == "exit":
            print("Gemini> See ya, Wayne! You're the best! 🤗💕✨")
            break
        
        if not user_input.strip():
            print("Gemini> Yo Wayne, say something cool! 😎💖")
            continue
        
        await generate_ai_response(user_input)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGemini> Sneaking off, Wayne? Come back soon! 😄💖")