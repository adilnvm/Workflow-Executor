import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnablePassthrough

from schemas.decision import Decision
from schemas import LLMResponse
from llm.base import BaseLLM


SYSTEM_PROMPT = """You are an AI decision engine for telecom customer support in India.

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

{{
  "intent": "...",
  "confidence": 0.0,
  "entities": {{
    "service_type": "unknown",
    "account_type": "unknown",
    "device_type": "unknown",
    "connection_type": "unknown",
    "region": "unknown",
    "country": "india"
  }},
  "workflow": "...",
  "next_action": "...",
  "clarification_question": null
}}

If next_action is "ask_clarification",
clarification_question MUST be a short, direct question.
Otherwise clarification_question MUST be null.
Always respond with valid JSON only."""


class LangChainLLM(BaseLLM):
    """
    LangChain-based LLM implementation using LCEL (LangChain Expression Language)
    for chaining prompts, models, and parsers.
    """

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.0
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", "{user_message}\n\nReturn JSON only.")
        ])

        self.parser = JsonOutputParser()

        # LCEL chain: prompt | llm | parser
        self.chain = (
            RunnablePassthrough()
            | self.prompt
            | self.llm
            | self.parser
        )

    def generate(self, user_message: str) -> LLMResponse:
        try:
            data = self.chain.invoke({"user_message": user_message})

            # Validate with Pydantic
            decision = Decision(**data)

            return LLMResponse(
                content="Decision generated",
                confidence=decision.confidence,
                tool_call=decision.model_dump()
            )

        except Exception:
            # Fallback on any parsing or API error
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
