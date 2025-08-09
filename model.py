##
##    Run local model using ollama 
##

import requests
import os
import time
import json
import re
import logging


logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(levelname)s - %(message)s"
)

with open(os.path.join(os.path.dirname(__file__), "Modelfile"), "r") as f:
    CONTEXT = f.read().strip()

def run_local_model(prompt: str, model: str = "llama3:8b", max_retries: int = 3, temperature: float = 0.3) -> str:
    
    start = time.time()
    json_prompt = f"""
{prompt}

CRITICAL: Output ONLY valid JSON. Do NOT include ANY text, explanations, or comments before or after the JSON, such as "Here's my response" or "Let me know if this is correct." Non-JSON content will cause a system failure.
"""
    
    attempt = 0
    while attempt < max_retries:
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model,
                    "prompt": json_prompt,
                    "stream": False,
                    "temperature": temperature
                },
                timeout=30
            )
            response.raise_for_status()  # Raise exception for HTTP errors
            raw_response = response.json()["response"]
            logging.debug(f"Raw LLM response: {raw_response}")
            
            # Try to validate if the response is JSON
            try:
                json.loads(raw_response)
                end = time.time()
                logging.debug(f"Model inference took {end - start:.2f} seconds")
                return raw_response
            except json.JSONDecodeError:
                # Extract JSON array from response (handles preamble/trailing text)
                json_match = re.search(r'\[\s*{.*?}\s*\]', raw_response, re.DOTALL)
                if json_match:
                    extracted_json = json_match.group(0)
                    # Verify extracted JSON is valid
                    try:
                        json.loads(extracted_json)
                        end = time.time()
                        logging.debug(f"Extracted valid JSON: {extracted_json}")
                        logging.debug(f"Model inference took {end - start:.2f} seconds")
                        return extracted_json
                    except json.JSONDecodeError:
                        logging.warning(f"Attempt {attempt + 1}: Extracted JSON is invalid, retrying...")
                else:
                    logging.warning(f"Attempt {attempt + 1}: No JSON found in response, retrying...")
                attempt += 1
                continue
        except requests.RequestException as e:
            logging.error(f"Attempt {attempt + 1}: Request failed: {str(e)}")
            attempt += 1
            if attempt == max_retries:
                logging.error("Max retries reached, returning empty response")
                return ""
            time.sleep(1)  # Brief delay before retrying
    
    end = time.time()
    logging.debug(f"Model inference took {end - start:.2f} seconds")
    logging.error("All retries failed, returning empty response")
    return ""