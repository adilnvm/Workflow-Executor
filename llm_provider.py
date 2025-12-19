import os
from logger import logger
from mock.llm import MockLLM
from real.llm import GeminiLLM


def get_llm():
    if os.getenv("USE_REAL_LLM") == "true":
        logger.info("LLM MODE: REAL (Gemini)")
        return GeminiLLM()

    logger.info("LLM MODE: MOCK")
    return MockLLM()
