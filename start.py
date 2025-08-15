import subprocess
import sys
import platform
import threading
import time
import socket
import webbrowser
import psutil

def is_port_in_use(port, host="127.0.0.1"):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0

def is_ollama_running():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        try:
            s.connect(("127.0.0.1", 11434))
            return True
        except socket.error:
            return False

def start_ollama():
    print("Starting Ollama server...")
    try:
        process = subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
        )
        # Wait briefly and check if the process is still running
        time.sleep(3)
        if process.poll() is not None:
            raise RuntimeError("Ollama failed to start.")
        return process
    except FileNotFoundError:
        print("Error: 'ollama' command not found. Ensure Ollama is installed.")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting Ollama: {e}")
        sys.exit(1)

def run_api():
    if is_port_in_use(8000):
        print("API server already running on port 8000")
        return None
    try:
        # Explicitly bind to 0.0.0.0 to support both IPv4 and IPv6
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"],
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
        )
        time.sleep(2)
        if process.poll() is not None:
            raise RuntimeError("Uvicorn failed to start.")
        return process
    except FileNotFoundError:
        print("Error: 'uvicorn' not found. Ensure Uvicorn is installed.")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting Uvicorn: {e}")
        sys.exit(1)

def open_browser():
    url = "http://127.0.0.1:8000" 
    print(f"Launching browser at {url}")
    # webbrowser.open(url)

def check_host_resolution():
    try:
        resolved = socket.gethostbyname("localhost")
        if resolved != "127.0.0.1":
            print(f"Warning: 'localhost' resolves to {resolved}, not 127.0.0.1. Use 127.0.0.1:8000.")
    except socket.gaierror:
        print("Warning: Could not resolve 'localhost'. Use 127.0.0.1:8000.")

if __name__ == "__main__":
    print("Application Starting.")

    # Check localhost resolution
    check_host_resolution()

    # Start Ollama if not running
    ollama_process = None
    if not is_ollama_running():
        print("Starting Ollama...")
        ollama_process = start_ollama()
    else:
        print("Ollama already running.")

    # Start API server
    server = run_api()
    if server:
        threading.Thread(target=open_browser, daemon=True).start()
        try:
            server.wait()
        except KeyboardInterrupt:
            print("Shutting down...")
            if server:
                server.terminate()
                server.wait()
            if ollama_process:
                ollama_process.terminate()
                ollama_process.wait()