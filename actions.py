##
##    Collection of all possible actions the agent can take.
##

from urllib.parse import urlparse
import requests
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(levelname)s - %(message)s"
)

class Actions:

    @staticmethod
    def api_call(params):
        method = params.get("method", "GET").upper()
        url = params.get("url")
        body = params.get("body", None)
        key = params.get("key")

        logging.info(f"API Call requested: method={method}, url={url}, key={key}")

        if not url:
            logging.error("API call missing URL")
            return {"error": "Missing URL parameter"}

        # Normalize URL: add https:// if missing
        parsed = urlparse(url)
        if not parsed.scheme:
            url = "https://" + url
            logging.info(f"Normalized URL to: {url}")

        try:
            if method == "GET":
                resp = requests.get(url, timeout=10)
            elif method == "POST":
                resp = requests.post(url, json=body, timeout=10)
            else:
                logging.error(f"Unsupported HTTP method: {method}")
                return {"error": f"Unsupported HTTP method: {method}"}

            try:
                data = resp.json()
            except ValueError:
                data = resp.text

            # Optional: search for the key in the response
            if key:
                found = str(key).lower() in str(data).lower()
                logging.info(f"Keyword '{key}' found: {found}")
                return {
                    "status_code": resp.status_code,
                    "found": found,
                    "data_preview": str(data)[:200]  # avoid huge dumps
                }

            return {
                "status_code": resp.status_code,
                "data_preview": str(data)[:200]
            }

        except requests.exceptions.Timeout:
            logging.warning(f"Timeout calling {url}")
            return {"error": f"Could not get data from {url}: request timed out"}

        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
            return {"error": f"Could not get data from {url}: {e}"}


    @staticmethod
    def general_query(params):
        """
        Handles general knowledge or reasoning tasks that don't require
        an API call or other structured action.
        """
        question = params.get("question")
        if not question:
            return {"error": "Missing 'question' parameter"}

        # Call the local LLM directly
        from model import run_local_model
        logging.info(f"General query: {question}")
        answer = run_local_model(question)
        return {"answer": answer.strip()}


    @staticmethod
    def echo(params):
        logging.info(f"Echo action called with params: {params}")
        # return {"echo": params}
        return params
