import random
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
                content=f"Checking network status for {region}.",
                tool_call={
                    "name": "check_network_status",
                    "arguments": {"region": region}
                },
                confidence=0.92
            )

        # --- General question ---
        if len(prompt) < 5:
            return LLMResponse(
                content="Your input is too short. Please provide more details.",
                confidence=0.30
            )

        # --- Default fallback ---
        return LLMResponse(
            content="I understood your request but no actionable tool is required.",
            confidence=0.60
        )

    # ------------------ helpers ------------------

    def _is_network_query(self, text: str) -> bool:
        keywords = ["network", "internet", "connectivity", "status", "down"]
        return any(k in text for k in keywords)

    def _extract_region(self, text: str) -> str:
        match = re.search(r"(india|us|usa|europe|asia)", text)
        return match.group(1) if match else "unknown"
