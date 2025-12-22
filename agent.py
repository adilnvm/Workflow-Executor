from llm_provider import get_llm
from workflow.registry import WORKFLOW_REGISTRY
from executor.workflow_executor import execute_workflow
from logger import logger

from utils.slot_checker import get_missing_slot   # ← ADDED (Phase-3.2)

from utils.decision_context import build_decision_context # ← ADDED (Phase-3.3)

import uuid

TICKET_STORE = {}
# Structure:
# {
#   ticket_id: {
#     "facts": {},
#     "history": [],
#     "last_decision": {}
#   }
# }


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
        # INITIALIZING MEMORY
        TICKET_STORE[ticket_id] = {
            "facts": {},
            "history": [message],
            "last_decision": decision
        }

        # store known facts
        for key, value in decision["entities"].items():
            if value != "unknown":
                TICKET_STORE[ticket_id]["facts"][key] = value

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

        prev["history"].append(message)

        # merge clarification with original context
        combined_message = build_decision_context(prev, message)


        llm_output = llm.generate(combined_message)
        decision = llm_output.tool_call

        # merge new facts
        for key, value in decision["entities"].items():
            if value != "unknown":
                prev["facts"][key] = value

        prev["last_decision"] = decision

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
    # 3.2 SLOT-BASED CLARIFICATION (Phase-3.2)
    # ──────────────────────────────

    facts = TICKET_STORE[ticket_id]["facts"]
    workflow_name = decision["workflow"]

    missing_slot, question = get_missing_slot(workflow_name, facts)

    if missing_slot:
        return {
            "summary": question,
            "workflow_result": {
                "status": "needs_info",
                "missing_slot": missing_slot,
                "ticket_id": ticket_id
            },
            "confidence": decision["confidence"]
        }

    # ──────────────────────────────
    # 4. Execute workflow
    # ──────────────────────────────
    workflow = WORKFLOW_REGISTRY[decision["workflow"]]

    # ──────────────────────────────
    # 4. REGION-MAPPING (Phase-3)
    # ──────────────────────────────

    from utils.region_mapper import normalize_region

    context = facts.copy()

    city = (
        context.get("location")
        or context.get("city")
        or context.get("region")
    )

    context["region"] = normalize_region(city)

    # ──────────────────────────────
    # ──────────────────────────────

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
