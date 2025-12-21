from llm_provider import get_llm
from workflow.registry import WORKFLOW_REGISTRY
from executor.workflow_executor import execute_workflow
from logger import logger

import uuid

TICKET_STORE = {}


llm = get_llm()


def run_workflow(message: str, ticket_id: str | None = None) -> dict:
    logger.info(f"Incoming message: {message}")

    # ──────────────────────────────
    # 1. New ticket
    # ──────────────────────────────
    if ticket_id is None:
        ticket_id = str(uuid.uuid4())

        llm_output = llm.generate(message)
        decision = llm_output.tool_call

        # store decision for continuation
        TICKET_STORE[ticket_id] = {
            "last_decision": decision
        }

    # ──────────────────────────────
    # 2. Clarification reply
    # ──────────────────────────────
    else:
        prev = TICKET_STORE.get(ticket_id)

        if not prev:
            return {
                "summary": "Session expired. Please describe your issue again.",
                "workflow_result": {"status": "expired"},
                "confidence": 0.0
            }

        # merge clarification with original context
        combined_message = (
            prev["last_decision"].get("intent", "")
            + " | clarification: "
            + message
        )

        llm_output = llm.generate(combined_message)
        decision = llm_output.tool_call

        TICKET_STORE[ticket_id]["last_decision"] = decision

    logger.info(f"LLM decision: {decision}")

    # ──────────────────────────────
    # 3. Ask clarification
    # ──────────────────────────────
    CONFIDENCE_THRESHOLD = 0.6

# Ask clarification ONLY if confidence is low
    if (
        decision["next_action"] == "ask_clarification"
        and decision["confidence"] < CONFIDENCE_THRESHOLD
    ):
        return {
            "summary": decision["clarification_question"],
            "workflow_result": {
                "status": "needs_info",
                "ticket_id": ticket_id
            },
            "confidence": decision["confidence"]
        }

    # ──────────────────────────────
    # 4. Execute workflow
    # ──────────────────────────────
    workflow = WORKFLOW_REGISTRY[decision["workflow"]]

    # normalize context defensively
    context = decision["entities"]
    context.setdefault("region", context.get("city", "unknown"))


    #//////////////////////////////////////////////////////
    #-------------------safety net-------------------------
    # Force optimistic execution if intent is known
    if decision["intent"] != "unknown" and decision["confidence"] >= CONFIDENCE_THRESHOLD:
        decision["next_action"] = "execute_workflow"
    #------------------------------------------------------

    result = execute_workflow(workflow, context)

    return {
        "summary": "Troubleshooting completed",
        "workflow_result": {
            **result,
            "ticket_id": ticket_id
        },
        "confidence": decision["confidence"]
    }
