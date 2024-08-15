require 'discordrb'
require 'json'

# Replace 'your_token_here' with your bot's token
TOKEN = 'Your_Token_API'

# Command prefix, e.g., !hello
PREFIX = '!'

def generate_response(prompt)
  # Retrieve the context for the user
  user_context[prompt] ||= ""

  # Update the context with the new prompt
  user_context[prompt] += " User: #{prompt}\n"

  payload = {
    model: 'dolphin-llama3',
    messages: [
      {
        role: 'system',
        content: 'You are a role-playing AI. Your name is Ebba.'
      },
      {
        role: 'user',
        content: user_context[prompt]
      }
    ]
  }

  # Send a request to the Ollama server
  begin
    api_url = 'http://localhost:11434/api/chat'
    headers = { 'Content-Type' => 'application/json' }
    response = Net::HTTP.post(api_url, payload.to_json, headers)
    response.raise_request if response.error?
    response_body = JSON.parse(response.body)

    combined_response = ""
    response_body['messages'].each do |line|
      next unless line['message'] && line['content']
      combined_response += line['content']
    end

    # Update the context with the AI's response
    user_context[prompt] += " AI: #{combined_response.strip}\n"

    return combined_response.strip
  rescue JSON::ParserError => e
    puts "JSON decode error: #{e}"
  rescue StandardError => e
    puts "Error: #{e}"
  end
end

bot = Discordrb::Commands::CommandBot.new token: TOKEN, prefix: PREFIX

bot.command(:generate, description: 'Generate a response using the Ollama model') do |event|
  event.send('processing...')
  begin
    response = generate_response(event.message.text)
    event.send(response)
  rescue StandardError => e
    event.send("Error: #{e}")
  end
end

bot.run
