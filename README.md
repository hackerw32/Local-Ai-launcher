#  AI Coder Studio

**The Ultimate GUI Launcher for Local AI Coding (Ollama + Aider)**

AI Coder Studio is a lightweight, smart Graphical User Interface (GUI) written in Python that acts as a control center for your local LLMs. It dynamically scans your installed Ollama models, categorizes them automatically based on their capabilities, and launches [Aider](https://aider.chat/) in a dedicated terminal for your specific project folder.

![AI Coder Studio Screenshot](link_to_your_screenshot_here.png) *(Note: Replace this with a screenshot of your app!)*

##  Features

- ** Smart Auto-Discovery:** Automatically detects installed Ollama models and sorts them into logical categories (Android, Web, Python, Reasoning, etc.) based on customizable keyword rules.
- ** Architect / Dual AI Mode:** Harness the power of two models at once! Assign a massive reasoning model (e.g., DeepSeek-R1 or Llama 3.3) to act as the "Architect" to plan the code, and a fast coding model (e.g., Qwen 2.5 Coder) as the "Editor" to write the files.
- ** Favorites System:** Save your most-used setups (Model + Architect + Project Folder) and launch them with a single click.
- ** Launch History:** Keeps track of your last 20 sessions for quick resuming.
- ** Bilingual Support:** Instantly toggle between English and Greek UI.
- ** Persistent Data:** Saves your preferences, history, and favorites in a local `.json` file.

##  Prerequisites

Before using AI Coder Studio, ensure you have the following installed on your system:

1. **[Python 3.x](https://www.python.org/downloads/)** (The `tkinter` library is included by default).
2. **[Ollama](https://ollama.com/)**: Must be installed and running in the background.
3. **[Aider](https://aider.chat/)**: Install it globally via pip:
   ```bash
   pip install aider-chat
