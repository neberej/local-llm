##
##    The brain - LLM decides what tasks to run and also summarizes request and response.
##

import json
import datetime
import logging
from model import run_local_model
from actions import Actions

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(levelname)s - %(message)s"
)

class AgentManager:
    def __init__(self, user_input: str):
        self.user_input = user_input

    async def run(self):
        logging.info(f"AgentManager started with input: {self.user_input}")

        # 1. Get a plan from the LLM
        plan_prompt = f"""
You are an AI assistant for a large e-commerce company.

The user says:
{self.user_input}

"""
        plan_raw = run_local_model(plan_prompt)
        logging.debug(f"Raw LLM plan output: {plan_raw}")

        try:
            plan = json.loads(plan_raw)
            if not isinstance(plan, list):
                plan = [plan]
        except json.JSONDecodeError as e:
            logging.error(f"Could not parse LLM plan: {str(e)}")
            return {"error": "Could not parse LLM plan", "raw": plan_raw}

        results = []

        # 2. Execute each action
        for step in plan:
            action_name = step.get("action")
            params = step.get("params", {})

            if hasattr(Actions, action_name):
                logging.info(f"Executing action: {action_name}")
                method = getattr(Actions, action_name)
                result = method(params)
            else:
                logging.error(f"Unknown action: {action_name}")
                result = {"error": f"Unknown action '{action_name}'"}

            results.append({
                "action": action_name,
                "params": params,
                "result": result
            })

        # 3. Ask LLM to interpret results
        interpretation_prompt = f"""
The user asked: {self.user_input}

Actions taken and results:
{json.dumps(results, indent=2)}

Today's date is {datetime.date.today().isoformat()}.

If an action failed (error present), explain briefly why and suggest next steps if possible.
If it succeeded, provide a concise, direct answer to the user.
Do not include explanations or confirmations, only the essential answer the user expects based on the actions.
Output ONLY valid JSON with this schema:
{{
  "message": "<short user-facing answer>"
}}
"""
        final_answer = run_local_model(interpretation_prompt).strip()
        logging.info(f"Final interpreted answer: {final_answer}")

        return {
            "plan": plan,
            "results": results,
            "answer": final_answer
        }
