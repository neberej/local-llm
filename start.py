import subprocess
import sys
import platform
import threading
import time
import requests

def is_ollama_running():
    try:
        r = requests.get("http://localhost:11434")
        return r.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

def start_ollama():
    print("Starting Ollama server...")
    return subprocess.Popen(
        ["ollama", "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
    )

def run_api():
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api:app"],
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
    )

def open_browser():
    time.sleep(2)
    print("Launch http://localhost:8000 to access the UI")

if __name__ == "__main__":
    print("Starting...")

    # Start Ollama if not running
    if not is_ollama_running():
        ollama_process = start_ollama()
        time.sleep(2)  # Give it time to boot
    else:
        print("Ollama already running.")

    server = run_api()
    open_browser()

    try:
        server.wait()
    except KeyboardInterrupt:
        print("\nExiting...")
        server.terminate()
        server.wait()
