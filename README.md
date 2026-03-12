# AI Coder Studio

**The Ultimate GUI Launcher for Local AI Coding (Ollama + Aider)**

AI Coder Studio is a lightweight, smart Graphical User Interface (GUI) written in Python that acts as a control center for your local LLMs. It dynamically scans your installed Ollama models, categorizes them automatically based on their capabilities, and launches [Aider](https://aider.chat/) in a dedicated terminal for your specific project folder.

![AI Coder Studio Screenshot](https://prnt.sc/RS8-98NX3Cmm) 

## Features

- **Smart Auto-Discovery:** Automatically detects installed Ollama models and sorts them into logical categories (Android, Web, Python, Reasoning, etc.) based on customizable keyword rules.
- **Architect / Dual AI Mode:** Harness the power of two models at once! Assign a massive reasoning model (e.g., DeepSeek-R1 or Llama 3.3) to act as the "Architect" to plan the code, and a fast coding model (e.g., Qwen 2.5 Coder) as the "Editor" to write the files.
- **Favorites System:** Save your most-used setups (Model + Architect + Project Folder) and launch them with a single click.
- **Launch History:** Keeps track of your last 20 sessions for quick resuming.
- **Bilingual Support:** Instantly toggle between English and Greek UI.
- **Persistent Data:** Saves your preferences, history, and favorites in a local `.json` file.

## Prerequisites

Before using AI Coder Studio, ensure you have the following installed on your system:

1. **[Python 3.x](https://www.python.org/downloads/)** (The `tkinter` library is included by default).
2. **[Ollama](https://ollama.com/)**: Must be installed and running in the background.
3. **[Aider](https://aider.chat/)**: Install it globally via pip:
   ```bash
   pip install aider-chat
   ```
4. **Local Models:** You need at least one model pulled in Ollama (e.g., `ollama pull qwen2.5-coder:32b`).

## Installation & Usage

1. Clone this repository:
   ```bash
   git clone [https://github.com/hackerw32/Local-Ai-launcher.git](https://github.com/hackerw32/Local-Ai-launcher.git)
   cd ai-coder-studio
   ```
2. Run the application:
   ```bash
   python AI_Studio.py
   ```
3. Select your project category, pick your AI model, browse for your project folder, and click **LAUNCH AIDER**!

## Customizing Categories

The app uses a smart keyword-based dictionary to categorize your models. You can easily edit the `CATEGORY_RULES` inside `AI_Studio.py` to match your personal workflow. 

```python
CATEGORY_RULES = {
    "Android / Mobile (Kotlin/Java)": ["android", "java", "swift", "deepseek-coder-v2"],
    "Web Development (HTML/CSS/JS)": ["web", "html", "javascript", "react", "starcoder"],
    "Python / Data Science": ["python", "codellama"],
    "Reasoning / Complex Logic": ["deepseek-r1", "qwq", "reasoning", "llama3.3", "llama3.1", "phi4"],
    "General Coding / Multi-language": ["coder", "phind", "wizard"],
    "General Chat & Text": ["llama", "mistral", "gemma", "phi", "qwen", "deepseek"]
}
```

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page if you want to contribute.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
