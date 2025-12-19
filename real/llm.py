import os
import google.generativeai as genai
from schemas import LLMResponse

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


class GeminiLLM:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def generate(self, prompt: str) -> LLMResponse:
        response = self.model.generate_content(prompt)

        return LLMResponse(
            content=response.text,
            confidence=0.95
        )
