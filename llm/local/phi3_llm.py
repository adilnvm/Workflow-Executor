import json
import subprocess
from schemas import LLMResponse
from llm.base import BaseLLM


SYSTEM_PROMPT = """
You are an AI decision engine for telecom customer support in India.

Your role is NOT to chat.
Your role is to produce a single structured decision.

You must:
- Identify the user's intent
- Extract entities from the message
- Choose the correct workflow
- Decide the next action

You MUST output ONLY valid JSON.
NO explanations.
NO markdown.
NO extra text.
NO trailing commas.
NO comments.

If you violate JSON format, the response will be discarded.

━━━━━━━━━━
ALLOWED INTENTS:
network_issue
slow_internet
no_signal
call_drop
billing_issue
unexpected_charges
recharge_issue
plan_validity
sim_issue
device_issue
unknown

━━━━━━━━━━
ALLOWED WORKFLOWS:
network_troubleshooting_workflow
billing_explanation_workflow
recharge_resolution_workflow
sim_device_troubleshooting_workflow
clarification_workflow

━━━━━━━━━━
ALLOWED next_action:
execute_workflow
ask_clarification
escalate

━━━━━━━━━━
ENTITY RULES:
- country MUST always be "india"
- Missing information → "unknown"
- NEVER invent values
- NEVER guess account numbers
- NEVER guess locations
- Use lowercase for entity values

━━━━━━━━━━
CONFIDENCE RULES:
- Confidence reflects how clear the problem category is
- Missing entities MUST NOT reduce confidence
- If the problem category is clear → confidence >= 0.7
- Use confidence < 0.5 ONLY if intent is unclear

━━━━━━━━━━
DECISION RULES:
- If the problem type is clear → set intent confidently
- If intent is clear but details are missing → ask_clarification
- Use clarification ONLY when intent itself is unclear

━━━━━━━━━━
GUIDANCE:
- slow, buffering, low speed → slow_internet
- no network, cross icon, no bars → no_signal
- high bill, extra charges → billing_issue / unexpected_charges
- recharge not reflected → recharge_issue
- SIM error, SIM not working → sim_issue
- phone not detecting SIM → device_issue

━━━━━━━━━━
OUTPUT FORMAT (STRICT):

{
  "intent": "...",
  "confidence": 0.0,
  "entities": {
    "service_type": "unknown",
    "account_type": "unknown",
    "device_type": "unknown",
    "connection_type": "unknown",
    "region": "unknown",
    "country": "india"
  },
  "workflow": "...",
  "next_action": "...",
  "clarification_question": null
}

If next_action is "ask_clarification",
clarification_question MUST be a short, direct question.
Otherwise clarification_question MUST be null.
"""


class Phi3LLM(BaseLLM):
    def generate(self, user_message: str) -> LLMResponse:
        prompt = f"""
{SYSTEM_PROMPT}

User message:
{user_message}

Return JSON only.
"""

        result = subprocess.run(
            ["ollama", "run", "phi3"],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=30
        )

        raw = result.stdout.strip()

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            # HARD FAIL → safe fallback decision
            return LLMResponse(
                content="Decision generated",
                confidence=0.0,
                tool_call={
                    "intent": "unknown",
                    "confidence": 0.0,
                    "entities": {
                        "service_type": "unknown",
                        "account_type": "unknown",
                        "device_type": "unknown",
                        "connection_type": "unknown",
                        "region": "unknown",
                        "country": "india"
                    },
                    "workflow": "clarification_workflow",
                    "next_action": "ask_clarification",
                    "clarification_question": "Could you please describe your Jio issue in more detail?"
                }
            )

        # minimal guardrails (do NOT overcorrect Phi-3)
        data.setdefault("entities", {})
        data["entities"].setdefault("country", "india")
        data.setdefault("confidence", 0.0)
        data.setdefault("clarification_question", None)

        return LLMResponse(
            content="Decision generated",
            confidence=data["confidence"],
            tool_call=data
        )
