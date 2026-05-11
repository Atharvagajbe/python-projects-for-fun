# Sophia

Sophia is a Python voice assistant with a simple desktop chat UI. It listens through the microphone, answers out loud with a female Windows voice when available, and stores the conversation in the app window while it responds.

## What It Does

- Listens to your voice commands using `speech_recognition`.
- Speaks replies out loud using Windows SAPI or `pyttsx3`.
- Shows your conversation history in a Tkinter desktop UI.
- Uses a local Ollama model, `qwen3:4b`, for general questions.
- Opens websites like YouTube, Google, GitHub, Gmail, ChatGPT, and Stack Overflow.
- Opens local apps like VS Code, Notepad, Calculator, Paint, Terminal, and Command Prompt.
- Searches Google from voice commands.
- Finds and opens files or folders by name.
- Creates starter Python projects inside a local `projects` folder.

## Example Commands

```text
what is docker
open youtube
open github
open github in chrome
open vs code
open notepad
search python project ideas
open file main
create project weather app
test voice
bye
```

## Requirements

Install the Python packages used by the project:

```powershell
pip install speechrecognition pyttsx3 ollama pywin32
```

You also need:

- A working microphone.
- Internet access for Google speech recognition.
- Ollama installed and running locally.
- The `qwen3:4b` Ollama model pulled locally.

To pull the model:

```powershell
ollama pull qwen3:4b
```

## How To Run

From this project folder, run:

```powershell
python main.py
```

Sophia will open a desktop window, greet you, listen in the background, speak responses out loud, and display the conversation in the UI.

## Notes

Sophia is designed for Windows because it uses Windows SAPI voice support and Windows app launch commands. If a female voice such as Microsoft Zira is installed, Sophia will try to use it automatically.
