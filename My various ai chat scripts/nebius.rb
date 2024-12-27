require 'net/http'
require 'json'

# API configuration
BASE_URL = "https://api.studio.nebius.ai/v1/"
API_KEY = "[api key]"

# Function to send a completion request
def get_ai_response(user_input)
  uri = URI("#{BASE_URL}chat/completions")
  http = Net::HTTP.new(uri.host, uri.port)
  http.use_ssl = true

  # Request body
  request_body = {
    model: "meta-llama/Meta-Llama-3.1-70B-Instruct",
    messages: [
      {
        role: "user",
        content: "You are an AI assistant that simulates emotional states, specifically #{user_input}"
      }
    ],
    temperature: 0.6
  }

  # HTTP POST request
  request = Net::HTTP::Post.new(uri)
  request["Authorization"] = "Bearer #{API_KEY}"
  request["Content-Type"] = "application/json"
  request.body = request_body.to_json

  # Send the request and handle the response
  response = http.request(request)
  if response.code.to_i == 200
    result = JSON.parse(response.body)
    return result["choices"][0]["message"]["content"]
  else
    puts "Error: #{response.code} - #{response.message}"
    return nil
  end
end

# Main loop for user interaction
loop do
  print "You: "
  user_input = gets.chomp
  break if user_input.downcase == "exit" || user_input.downcase == "quit"

  ai_response = get_ai_response(user_input)
  if ai_response
    puts "AI: #{ai_response}"
  else
    puts "An error occurred. Please try again."
  end
end
