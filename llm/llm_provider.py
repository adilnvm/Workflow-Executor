import os
from llm.mock.llm import MockLLM
from llm.local.phi3_llm import Phi3LLM
from llm.real.gemini_llm import GeminiLLM, QuotaExceededError

def get_llm():
    mode = os.getenv("LLM_MODE", "mock")
    print(f"[LLM_PROVIDER] Using LLM_MODE={mode}")

    if mode == "mock":
        return MockLLM()

    if mode in ["local", "phi3", "test", "dev"]:
        return Phi3LLM()

    if mode in ["prod", "real", "gemini"]:
        return GeminiLLM()

    raise ValueError(f"Unknown LLM_MODE: {mode}")

