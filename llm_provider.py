import os
from llm.mock.llm import MockLLM
from llm.local.phi3_llm import Phi3LLM
from llm.real.gemini_llm import GeminiLLM, QuotaExceededError
from llm.langchain.langchain_llm import LangChainLLM

def get_llm():
    mode = os.getenv("LLM_MODE", "mock")
    print(f"[LLM_PROVIDER] Using LLM_MODE={mode}")

    if mode == "mock":
        return MockLLM()

    if mode == "local":
        return Phi3LLM()

    if mode == "prod":
        return GeminiLLM()

    if mode == "langchain":
        return LangChainLLM()

    raise ValueError(f"Unknown LLM_MODE: {mode}")

