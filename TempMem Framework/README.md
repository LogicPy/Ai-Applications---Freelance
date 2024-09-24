![TempMem Logo](images/tempmem-logo.png)
![Alt text for the image](https://i.imgur.com/zoNadZ1.png)


# TempMem AI Framework

**TempMem** is an advanced AI framework designed to emulate temporal memory and spatial awareness. Built on Flask and the Ollama framework, TempMem offers AI the ability to recall events with a precise awareness of time, making it a highly versatile and efficient memory system.

## Features
- **Temporal Awareness**: The AI can recall sequential events with their associated time periods, offering a depth of understanding that goes beyond traditional memory frameworks like Mem0.
- **Real-time Event Tracking**: Log events and memories as they occur, with a user-friendly web UI for viewing scheduled events and reviewing memory logs.
- **Ollama Integration**: Powered by Ollama's AI models, providing fast and efficient interactions.

## Installation

1. **Run the Flask Web UI**:
   To launch the web UI, execute the following command in your terminal:
   ```bash
   python app.py
   ```

2. **Start AI Interaction**:
   Once the web UI is running, interact with your AI by executing:
   ```bash
   python ai-script.py
   ```
   Ensure your Ollama framework is installed and running, and that the endpoint in the AI script is set to:
   ```
   http://localhost:11434/api/chat
   ```

3. **Access the Web UI**:
   - **Event Viewer**: View scheduled events by navigating to:
     ```
     http://127.0.0.1:5000
     ```
   - **Memory Log**: To review your AI’s memory logs, navigate to:
     ```
     http://127.0.0.1:5000/memories
     ```

## Why TempMem?

TempMem offers a unique advantage by incorporating **temporal awareness**. Unlike other frameworks such as Mem0, TempMem enables AI to recall events with a clear understanding of when the event occurred, enhancing its ability to manage and reference past events with precision. 

### Key Highlights:
- **Time Awareness**: The AI doesn’t just remember events, but also understands the time context in which they happened.
- **Enhanced Memory Recall**: TempMem allows the AI to sequentially recall past messages and events, offering richer and more context-aware responses.

---
