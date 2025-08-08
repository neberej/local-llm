##
##    Collection of all possible actions the agent can take.
##

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
    def echo(params):
        """Just echoes the params for debugging."""
        logging.info(f"Echo action called with params: {params}")
        return {"echo": params}
