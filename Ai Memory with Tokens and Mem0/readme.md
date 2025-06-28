# Grok-3 Chatbot with Mem0 Memory

A beautifully crafted chatbot integrating Grok-3 API with Mem0 for persistent memory, designed by Wayne with coding assistance from Grok 3 (xAI).

## Features
- Remembers your name across sessions using Mem0 and local JSON storage.
- Modular design with `MemoryManager` and `GrokChat` classes.
- Supports context-aware responses with Mem0 search.

## Setup
1. Install dependencies: `pip install requests mem0`
2. Replace `API_KEY` and `MEM0_API_KEY` with your xAI and Mem0 API keys (static for this demo).
3. Run: `python3 grok3_mem_clean.py`

## Usage
- Introduce yourself with "My name is [Your Name]" to set your name.
- Chat away! Use "quit" to exit.

## Credits
- **Wayne**: Concept, design, and primary development.
- **Grok 3 (xAI)**: Coding assistance and optimization.

## Notes
- API keys are static for demo purposes. For production, use environment variables.
- Memory persists in `memory.json` and Mem0 cloud.

Enjoy your chat experience! 🍉
