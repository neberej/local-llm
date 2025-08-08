##
##    Run local model using ollama 
##

import requests
import os
import time

with open(os.path.join(os.path.dirname(__file__), "Modelfile"), "r") as f:
    CONTEXT = f.read().strip()

def run_local_model(prompt: str, model="llama3:8b"):
    start = time.time()
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model, "prompt": prompt, "stream": False}
    )
    end = time.time()
    print(f"[DEBUG] Model inference took {end - start:.2f} seconds")
    return response.json()["response"]

