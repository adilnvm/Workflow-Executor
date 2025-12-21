import os
import json
from google import  genai
from schemas.decision import Decision
from schemas.requests import UserQuery
from schemas import LLMResponse

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


SYSTEM_PROMPT = """
You are an AI decision engine for Jio customer support (India only).

Your job:
- Understand the user issue
- Classify intent
- Extract entities
- Select the correct workflow
- Decide the next action

You MUST return ONLY valid JSON.
NO explanations.
NO markdown.
NO extra text.

Allowed intents:
network_issue, slow_internet, no_signal, call_drop,
billing_issue, unexpected_charges,
recharge_issue, plan_validity,
sim_issue, device_issue, unknown

Allowed workflows:
network_troubleshooting_workflow
billing_explanation_workflow
recharge_resolution_workflow
sim_device_troubleshooting_workflow
clarification_workflow

Allowed next_action:
execute_workflow
ask_clarification
escalate

Entity rules:
- country is always "india"
- unknown info → "unknown"
- never invent account numbers
- never guess

Intent confidence should be based on the user’s problem description,
not on missing entities.

Missing entities should be marked as "unknown",
but intent may still be confident.

Guidance:
- Slow speed, buffering, low bandwidth → slow_internet
- No connectivity, no signal, cross icon → no_signal
- High bill, extra charges → billing_issue or unexpected_charges
- Recharge not reflected → recharge_issue
- SIM not working, SIM error → sim_issue
- Phone not detecting SIM → device_issue

Intent confidence should be high if the problem type is clear,
even if some entities are missing.

Missing details should reduce entity completeness, not intent confidence.

Decision rules:

- If the problem category is clear from the message,
  set intent confidently (confidence >= 0.7),
  even if some entities are missing.

- Missing entities should be marked as "unknown"
  and must NOT reduce confidence.

- Use clarification ONLY when the problem category itself is unclear.

Examples:
- "Internet slow", "buffering", "speed issue" → slow_internet (confidence ~0.8–0.9)
- "Bill too high", "extra charges" → billing_issue (confidence ~0.9)
- "Recharge not reflected" → recharge_issue (confidence ~0.85)
- "Not working", "issue with service" → ask clarification (confidence <0.5)

"""

class GeminiLLM:
    def generate(self, user_message: str) -> LLMResponse:
        prompt = f"""
{SYSTEM_PROMPT}

User message:
{user_message}

Return JSON only.
"""

        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=prompt
        )

        raw_text = response.text.strip()

        try:
            data = json.loads(raw_text)
            decision = Decision(**data)  # strict validation

        except Exception as e:
            # HARD FAIL → safe fallback
            decision = Decision(
                intent="unknown",
                confidence=0.0,
                entities={"country": "india"},
                workflow="clarification_workflow",
                next_action="ask_clarification",
                clarification_question="Could you please describe your Jio issue in more detail?"
            )

        return LLMResponse(
            content="Decision generated",
            confidence=decision.confidence,
            tool_call=decision.model_dump()
        )
