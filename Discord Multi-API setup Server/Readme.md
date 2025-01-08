# Multi-API Discord Bot
A powerful and versatile Discord bot that integrates multiple AI platforms for dynamic conversations. This bot allows users to seamlessly switch between AI models like **GPT-4**, **Groq**, **Grok**, **Nebius (Llama3)**, **AI21 J1 Jumbo**, **LM Studio**, and **Cohere**, enabling a unique and customizable AI experience.

## Features
- Supports **7 AI platforms** with seamless model switching.
- User-friendly commands for model selection and interaction.
- Dynamic responses tailored to each AI model's strengths.
- Easy-to-configure API keys for each platform.

## Supported AI Platforms
1. **GPT-4** (default)
2. **Groq**
3. **Grok**
4. **Nebius (Llama3)**
5. **AI21 J1 Jumbo**
6. **LM Studio**
7. **Cohere**

## Setup and Installation

### Prerequisites
- Python 3.8+
- A Discord bot token ([create one here](https://discord.com/developers/applications)).
- API keys for each AI platform you want to use:
  - OpenAI (GPT-4)
  - Groq
  - Grok
  - Nebius (Llama3)
  - AI21
  - Cohere

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/multi-api-discord-bot.git
   cd multi-api-discord-bot

pip install -r requirements.txt

DISCORD_TOKEN=your_discord_bot_token
GPT4_API_KEY=your_gpt4_api_key
GROQ_API_KEY=your_groq_api_key
GROK_API_KEY=your_grok_api_key
NEBIUS_API_KEY=your_nebius_api_key
AI21_API_KEY=your_ai21_api_key
COHERE_API_KEY=your_cohere_api_key


python bot.py
