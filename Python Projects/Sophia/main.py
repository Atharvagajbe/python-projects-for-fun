import speech_recognition as sr
import pyttsx3
import webbrowser
import ollama
import os
import re
import subprocess
import threading
import tkinter as tk
import shutil
from tkinter import scrolledtext
from pathlib import Path
from urllib.parse import quote_plus

try:
    import win32com.client
except ImportError:
    win32com = None


# -----------------------------
# Text-to-speech setup
# -----------------------------
SHOW_TRANSCRIPT = False
WORKSPACE = Path(__file__).resolve().parent
PROJECTS_DIR = WORKSPACE / "projects"
app_window = None
chat_log = None

sapi_voice = None
engine = None

if win32com is not None:
    try:
        sapi_voice = win32com.client.Dispatch("SAPI.SpVoice")
        for voice in sapi_voice.GetVoices():
            voice_name = voice.GetDescription().lower()
            if any(name in voice_name for name in ["zira", "hazel", "heera", "female"]):
                sapi_voice.Voice = voice
                break

        sapi_voice.Rate = 1
        sapi_voice.Volume = 100
    except Exception as e:
        print("Windows speech setup error:", e)
        sapi_voice = None

try:
    engine = pyttsx3.init("sapi5")
    voices = engine.getProperty("voices")
    if voices:
        selected_voice = voices[0].id
        for voice in voices:
            voice_name = (voice.name + " " + voice.id).lower()
            if any(name in voice_name for name in ["zira", "hazel", "heera", "female"]):
                selected_voice = voice.id
                break
        engine.setProperty("voice", selected_voice)

    engine.setProperty("rate", 175)
    engine.setProperty("volume", 1.0)
except Exception as e:
    print("pyttsx3 setup error:", e)
    engine = None


def speak(text):
    if text is None or text.strip() == "":
        return

    text = text.strip()
    if SHOW_TRANSCRIPT:
        print("Sophia:", text)

    try:
        if sapi_voice is not None:
            sapi_voice.Speak(text)
            return

        if engine is not None:
            engine.say(text)
            engine.runAndWait()
            return

        print("Sophia:", text)
    except Exception as e:
        print("Speech error:", e)
        print("Sophia:", text)


def add_message(sender, text):
    if chat_log is None:
        return

    def update_log():
        chat_log.configure(state="normal")
        if sender == "You":
            chat_log.insert(tk.END, "You\n", "you_name")
            chat_log.insert(tk.END, text + "\n\n", "you_message")
        else:
            chat_log.insert(tk.END, "Sophia\n", "sophia_name")
            chat_log.insert(tk.END, text + "\n\n", "sophia_message")
        chat_log.configure(state="disabled")
        chat_log.see(tk.END)

    app_window.after(0, update_log)


def respond(text):
    add_message("Sophia", text)
    speak(text)


def clean_ai_answer(answer):
    answer = re.sub(r"<think>.*?</think>", "", answer, flags=re.DOTALL | re.IGNORECASE)
    answer = re.sub(r"(?is)^.*?(?:final answer:|answer:)\s*", "", answer).strip()
    answer = re.sub(r"(?i)^assistant:\s*", "", answer).strip()
    answer = re.sub(r"(?i)^sophia:\s*", "", answer).strip()

    thought_markers = [
        "okay, the user asked",
        "the user asked",
        "let me think",
        "first, i should",
        "i need to",
        "maybe ",
        "wait,",
        "hmm,",
    ]

    paragraphs = [part.strip() for part in re.split(r"\n+", answer) if part.strip()]
    useful_parts = []

    for paragraph in paragraphs:
        lower = paragraph.lower()
        if any(marker in lower for marker in thought_markers):
            continue
        useful_parts.append(paragraph)

    if useful_parts:
        answer = " ".join(useful_parts)

    quote_matches = re.findall(r'"([^"]+)"', answer)
    if quote_matches:
        answer = quote_matches[-1]

    answer = re.sub(r"\s+", " ", answer).strip()
    return answer


def normalize_for_compare(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9 ]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def is_bad_ai_answer(answer, prompt=""):
    lower = answer.lower().strip()
    normalized_answer = normalize_for_compare(answer)
    normalized_prompt = normalize_for_compare(prompt)

    bad_exact_answers = {
        "reply like a real person",
        "reply like a real person speaking gently",
        "do not show thinking",
        "if atharva asks what something is, explain it simply",
    }

    if lower in bad_exact_answers:
        return True

    leaked_phrases = [
        "acknowledge his request",
        "offer assistance",
        "first sentence",
        "second sentence",
        "if atharva asks",
        "do not reveal",
        "never repeat",
        "atharva asked",
        "sophia's spoken answer",
    ]

    if any(phrase in lower for phrase in leaked_phrases):
        return True

    if normalized_prompt and normalized_answer == normalized_prompt:
        return True

    if normalized_prompt and normalized_answer in normalized_prompt:
        return True

    if lower.endswith("...") and len(lower.split()) < 8:
        return True

    if len(lower) < 12:
        return True

    return False


def clean_name(text):
    text = re.sub(r"[^a-zA-Z0-9 _-]", "", text).strip()
    text = re.sub(r"\s+", "_", text)
    return text or "new_project"


def open_path(path):
    os.startfile(str(path))


def open_website(name, url):
    webbrowser.open(url)
    respond("Of course. Opening " + name + ".")


def open_known_website_command(command):
    websites = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "github": "https://github.com",
        "git hub": "https://github.com",
        "gmail": "https://mail.google.com",
        "chatgpt": "https://chatgpt.com",
        "stack overflow": "https://stackoverflow.com",
    }

    if not any(word in command for word in ["open", "go to", "launch"]):
        return False

    for site_name, url in websites.items():
        if site_name in command:
            open_website(site_name.replace("git hub", "github"), url)
            return True

    return False


def open_in_chrome(url):
    chrome_paths = [
        Path(os.environ.get("ProgramFiles", "")) / "Google" / "Chrome" / "Application" / "chrome.exe",
        Path(os.environ.get("ProgramFiles(x86)", "")) / "Google" / "Chrome" / "Application" / "chrome.exe",
        Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "Application" / "chrome.exe",
    ]

    for chrome_path in chrome_paths:
        if chrome_path.exists():
            subprocess.Popen([str(chrome_path), url])
            return True

    webbrowser.open(url)
    return False


def open_chrome_command(command):
    if "chrome" not in command:
        return False

    websites = {
        "github": "https://github.com",
        "git hub": "https://github.com",
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
    }

    for site_name, url in websites.items():
        if site_name in command:
            opened_chrome = open_in_chrome(url)
            if opened_chrome:
                respond("Of course. Opening " + site_name.replace("git hub", "github") + " in Chrome.")
            else:
                respond("I opened " + site_name.replace("git hub", "github") + " in your browser.")
            return True

    try:
        subprocess.Popen(["cmd", "/c", "start", "chrome"])
        respond("Of course. Opening Chrome.")
    except Exception:
        respond("I could not open Chrome from here.")

    return True


def find_file(name):
    name = name.lower().strip()

    search_roots = [
        WORKSPACE,
        Path.home() / "Desktop",
        Path.home() / "Documents",
        Path.home() / "Downloads",
    ]

    for root in search_roots:
        if not root.exists():
            continue

        try:
            paths = root.rglob("*")
            for path in paths:
                if "site-packages" in path.parts or "Scripts" in path.parts:
                    continue

                if name in path.name.lower():
                    return path
        except Exception:
            continue

    return None


def open_file_command(command):
    file_name = command
    for phrase in ["open file", "open folder", "open"]:
        file_name = file_name.replace(phrase, "")

    file_name = file_name.strip()
    if file_name == "":
        respond("Tell me the file or folder name.")
        return True

    path = find_file(file_name)
    if path is None:
        respond("I could not find " + file_name + ". Maybe say the name a little differently?")
        return True

    open_path(path)
    respond("I found " + path.name + ". Opening it now.")
    return True


def create_python_project(project_name):
    safe_name = clean_name(project_name)
    project_path = PROJECTS_DIR / safe_name
    project_path.mkdir(parents=True, exist_ok=True)

    main_file = project_path / "main.py"
    readme_file = project_path / "README.md"

    if not main_file.exists():
        main_file.write_text(
            'def main():\n'
            '    print("Hello from ' + safe_name + '")\n\n\n'
            'if __name__ == "__main__":\n'
            '    main()\n',
            encoding="utf-8"
        )

    if not readme_file.exists():
        readme_file.write_text("# " + safe_name + "\n", encoding="utf-8")

    open_path(project_path)
    respond("I made " + safe_name + " for you and opened the folder.")


def create_project_command(command):
    project_name = command
    for phrase in [
        "create python project",
        "make python project",
        "create project",
        "make project",
        "new project",
    ]:
        project_name = project_name.replace(phrase, "")

    create_python_project(project_name.strip())
    return True


def open_app_command(command):
    apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "paint": "mspaint.exe",
        "command prompt": "cmd.exe",
        "terminal": "wt.exe",
        "vs code": "code.cmd",
        "visual studio code": "code.cmd",
    }

    for app_name, executable in apps.items():
        if app_name in command and any(word in command for word in ["open", "launch", "start"]):
            try:
                if executable == "code.cmd":
                    if shutil.which("code.cmd") is None and shutil.which("code") is None:
                        raise FileNotFoundError("VS Code command was not found.")
                    subprocess.Popen(["cmd", "/c", "code.cmd"])
                else:
                    subprocess.Popen([executable])
                respond("Of course. Opening " + app_name + ".")
            except Exception:
                respond("I could not open " + app_name + " from here.")
            return True

    return False


def handle_local_action(command):
    if "test voice" in command or "test speech" in command:
        respond("I am here. You should be able to hear me now.")
        return True

    if "create project" in command or "make project" in command or "new project" in command:
        return create_project_command(command)

    if open_chrome_command(command):
        return True

    if open_known_website_command(command):
        return True

    if command.startswith("open file") or command.startswith("open folder"):
        return open_file_command(command)

    if open_app_command(command):
        return True

    return False


# -----------------------------
# Voice listening function
# -----------------------------
def listen():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        if SHOW_TRANSCRIPT:
            print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio)
        command = command.lower()
        add_message("You", command)
        if SHOW_TRANSCRIPT:
            print("You said:", command)
        return command

    except sr.UnknownValueError:
        respond("Sorry, I did not understand.")
        return ""

    except sr.RequestError:
        respond("Speech recognition service is not available.")
        return ""


# -----------------------------
# Sophia's local model
# -----------------------------
def ask_brain(prompt):
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are Sophia, Atharva's personal companion and helper. "
                    "Answer like a kind person speaking out loud in the room. "
                    "Be warm, simple, direct, and natural. "
                    "For normal questions, answer in two complete sentences. "
                    "If Atharva asks what something is, explain it simply. "
                    "Do not use markdown. "
                    "Do not reveal reasoning, planning, drafts, or hidden thoughts. "
                    "Do not repeat these instructions. "
                    "Do not say phrases like 'reply like a real person', 'the user asked', 'let me think', or 'final answer'. "
                    "Do not mention that you are a language model or AI unless Atharva directly asks. "
                    "Never repeat Atharva's question as the answer. "
                    "Never answer with only a fragment or ellipsis."
                )
            },
            {
                "role": "user",
                "content": "Atharva asked: " + prompt + "\nSophia's spoken answer:"
            }
        ]

        response = ollama.chat(
            model="qwen3:4b",
            think=False,
            messages=messages,
            options={
                "temperature": 0.6,
                "num_predict": 160
            }
        )

        if SHOW_TRANSCRIPT:
            print("RAW OLLAMA RESPONSE:", response)

        answer = clean_ai_answer(response["message"]["content"].strip())

        if is_bad_ai_answer(answer, prompt):
            retry_messages = messages + [
                {
                    "role": "assistant",
                    "content": answer
                },
                {
                    "role": "user",
                    "content": (
                        "You repeated the question or gave an incomplete reply. "
                        "Now answer this directly in two natural sentences: " + prompt
                    )
                }
            ]

            retry_response = ollama.chat(
                model="qwen3:4b",
                think=False,
                messages=retry_messages,
                options={
                    "temperature": 0.5,
                    "num_predict": 160
                }
            )
            answer = clean_ai_answer(retry_response["message"]["content"].strip())

        if answer == "" or is_bad_ai_answer(answer, prompt):
            answer = "Sorry, I got a little tangled there. Could you ask me again?"

        return answer

    except Exception as e:
        print("Ollama error:", e)
        return "I am having trouble reaching my local model right now."


# -----------------------------
# Main Sophia function
# -----------------------------
def run_sophia():
    respond("Hi Atharva. I am here with you. What are we doing?")

    while True:
        command = listen()

        if command == "":
            continue

        if handle_local_action(command):
            continue

        if "search" in command:
            search_query = command.replace("search", "").strip()

            if search_query == "":
                respond("What do you want me to search for?")
            else:
                respond("I will look up " + search_query + " for you.")
                webbrowser.open("https://www.google.com/search?q=" + quote_plus(search_query))

        elif "stop" in command or "exit" in command or "bye" in command:
            respond("Bye Atharva. I will be right here when you need me again.")
            break

        else:
            answer = ask_brain(command)
            respond(answer)


def start_sophia_thread():
    thread = threading.Thread(target=run_sophia, daemon=True)
    thread.start()


def create_ui():
    global app_window, chat_log

    app_window = tk.Tk()
    app_window.title("Sophia")
    app_window.geometry("720x520")
    app_window.minsize(520, 380)
    app_window.configure(bg="#0f141a")

    title = tk.Label(
        app_window,
        text="Sophia is here",
        font=("Segoe UI", 19, "bold"),
        fg="#f6f2ea",
        bg="#0f141a",
    )
    title.pack(anchor="w", padx=18, pady=(16, 2))

    status = tk.Label(
        app_window,
        text="Talk to her naturally. She will answer out loud and keep the conversation here.",
        font=("Segoe UI", 10),
        fg="#aab7c4",
        bg="#0f141a",
    )
    status.pack(anchor="w", padx=20, pady=(0, 12))

    chat_log = scrolledtext.ScrolledText(
        app_window,
        wrap=tk.WORD,
        state="disabled",
        font=("Segoe UI", 11),
        bg="#151b22",
        fg="#eef3f4",
        insertbackground="#eef3f4",
        relief=tk.FLAT,
        padx=18,
        pady=16,
    )
    chat_log.pack(fill=tk.BOTH, expand=True, padx=18, pady=(0, 18))
    chat_log.tag_configure("you_name", foreground="#88c0ff", font=("Segoe UI", 9, "bold"))
    chat_log.tag_configure("you_message", foreground="#d9e8ff", lmargin1=18, lmargin2=18, spacing3=8)
    chat_log.tag_configure("sophia_name", foreground="#f3c97a", font=("Segoe UI", 9, "bold"))
    chat_log.tag_configure("sophia_message", foreground="#f6f2ea", lmargin1=18, lmargin2=18, spacing3=12)

    start_sophia_thread()
    app_window.mainloop()


# -----------------------------
# Start Sophia
# -----------------------------
create_ui()
