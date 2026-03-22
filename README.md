# AI Coder Studio (Hybrid Edition v5)

**The Ultimate GUI Launcher for Local & Cloud AI Coding (Ollama + Gemini + Groq + Aider)**

AI Coder Studio is a professional, lightweight Graphical User Interface (GUI) written in Python that acts as a mission control for your AI-assisted development. It orchestrates local LLMs via Ollama and world-class Cloud LLMs via Google Gemini and Groq, launching [Aider](https://aider.chat/) with a perfectly tuned "Architect/Editor" configuration.

## What's New in v5

- **Hybrid Cloud Integration:** Use top-tier Cloud models (Google Gemini 1.5 Pro/Flash, Groq Llama 3.3) as the "Architect" while keeping your code local.
- **Unified API Key Management:** Secure, persistent storage for Gemini and Groq API keys directly in the UI.
- **Smart Ollama Management:** Real-time detection of Ollama status. Includes a "Reload Models" feature to sync your local models without restarting the app.
- **Zero-Emoji Professional UI:** A clean, minimalist interface designed for serious development environments.
- **Integrated Repo Map Setup:** One-click Git initialization with smart `.gitignore` templates for Android, Python, and Web projects.

## Core Features

- **Architect / Dual AI Mode:** Assign a high-reasoning Cloud model (e.g., Gemini 1.5 Pro) to plan the logic and a fast local model (e.g., Qwen 2.5 Coder 32B) to execute the code changes.
- **Auto-Discovery & Categorization:** Automatically sorts your Ollama library and Cloud endpoints into logical groups.
- **Favorites & History:** Save complex multi-model setups and access a history of your last 20 project sessions.
- **Bilingual Support:** Full UI localization for English and Greek.
- **Safe Environment:** Cloud models only receive your prompts and repo map; the actual code editing is performed locally.



## Prerequisites

1. **[Python 3.10+](https://www.python.org/downloads/)**
2. **[Ollama](https://ollama.com/)**: Required for local model support.
3. **[Aider](https://aider.chat/)**: Install via pip:
   ```bash
   pip install aider-chat
   ```
4. **API Keys (Optional):** Obtain a free [Google AI Studio Key](https://aistudio.google.com/) or [Groq API Key](https://console.groq.com/) for Cloud features.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/hackerw32/Local-Ai-launcher.git
   cd ai-coder-studio
   ```
2. Run the launcher:
   ```bash
   python "AI Launcher v5 .py"
   ```

## Hybrid Workflow Guide

For the best experience, we recommend the **"Hybrid Power Setup"**:
1. **Architect:** Select `gemini-1.5-pro` (Cloud). It has a massive context window to "understand" your whole project.
2. **Editor:** Select `qwen2.5-coder:32b` (Local). It writes code with surgical precision on your machine.
3. **Launch:** Click Launch Aider. You can now talk to Gemini in your terminal, and it will command your local Ollama to edit your files.



## License

This project is licensed under the MIT License.
