import re
from schemas import LLMResponse


class MockLLM:
    """
    Deterministic, rule-based LLM mock.
    Designed to simulate:
    - intent detection
    - tool calling
    - fallbacks
    - confidence scoring
    """

    def generate(self, prompt: str) -> LLMResponse:
        prompt = prompt.strip().lower()

        # --- Network status intent ---
        if self._is_network_query(prompt):
            region = self._extract_region(prompt)
            return LLMResponse(
                content="Decision generated",
                confidence=0.9,
                tool_call={
                    "intent": "slow_internet",
                    "confidence": 0.9,
                    "entities": {
                        "service_type": "Jio Fiber",
                        "connection_type": "prepaid",
                        "region": region,
                        "country": "india"
                    },
                    "workflow": "network_troubleshooting_workflow",
                    "next_action": "execute_workflow",
                    "clarification_question": None
                }
            )

        # --- General question ---
        if len(prompt) < 5:
            return LLMResponse(
                content="Decision generated",
                confidence=0.3,
                tool_call={
                    "intent": "unknown",
                    "confidence": 0.3,
                    "entities": {"country": "india"},
                    "workflow": "clarification_workflow",
                    "next_action": "ask_clarification",
                    "clarification_question": "Please provide more details about your Jio issue."
                }
            )

        # --- Default fallback ---
        return LLMResponse(
            content="Decision generated",
            confidence=0.6,
            tool_call={
                "intent": "unknown",
                "confidence": 0.6,
                "entities": {"country": "india"},
                "workflow": "clarification_workflow",
                "next_action": "ask_clarification",
                "clarification_question": "Could you clarify your problem?"
            }
        )

    # ------------------ helpers ------------------

    def _is_network_query(self, text: str) -> bool:
        keywords = ["network", "internet", "connectivity", "status", "down", "slow"]
        return any(k in text for k in keywords)

    def _extract_region(self, text: str) -> str:
        match = re.search(r"(mumbai|delhi|bangalore|india)", text)
        return match.group(1) if match else "unknown"
