from openai import OpenAI

# Configure the client with your API key and base URL
client = OpenAI(
    base_url="https://api.studio.nebius.ai/v1/",
    api_key="[api key]"
)

# Main loop for user interaction
while True:
    # Get user input
    user_input = input("You: ")

    # Exit if the user types 'exit'
    if user_input.lower() in ["exit", "quit"]:
        print("Goodbye!")
        break

    # Create a completion request
    completion = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-70B-Instruct",
        messages=[
            {
                "role": "user",
                "content": "You are an AI assistant that simulates emotional states, specifically"
        }

            
        ],
        temperature=0.6
    )

    # Extract and print the AI's response
    ai_response = completion.choices[0].message.content  # Access 'content' directly
    print(f"AI: {ai_response}")
