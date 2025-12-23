from llm_provider import get_llm
from workflow.registry import WORKFLOW_REGISTRY
from executor.workflow_executor import execute_workflow
from logger import logger

from utils.slot_checker import get_missing_slot   # ← ADDED (Phase-3.2)
from utils.decision_context import build_decision_context # ← ADDED (Phase-3.3)

from llm.local.phi3_llm import Phi3LLM
from llm.real.gemini_llm import QuotaExceededError

from utils.inference_engine import infer_facts


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

STABLE_FACTS = {
    "service_type",
    "account_type",
    "device_type",
    "connection_type",
    "region"
}

llm = get_llm()


# woah woah woah woah hey hey hey
# try:
#     llm_output = llm.generate(combined_message)
# except QuotaExceededError:   #ERROR : "QuotaExceededError" is not defined
#     logger.warning("Gemini quota exhausted → falling back to Phi-3")
#     llm_output = Phi3LLM().generate(combined_message)  #ERROR : "Phi3LLM" is not defined , combined_message is not defined

def run_workflow(message: str, ticket_id: str | None = None) -> dict:
    logger.info(f"Incoming message: {message}")

    # ──────────────────────────────
    # 🔒 SAFETY: handle lost in-memory tickets (reload / crash)
    # ──────────────────────────────
    if ticket_id is not None and ticket_id not in TICKET_STORE:
        logger.warning("Unknown ticket_id (store reset) → starting new session")
        ticket_id = None


    # ──────────────────────────────
    # 1. New ticket
    # ──────────────────────────────
    if ticket_id is None:
        ticket_id = str(uuid.uuid4())


        llm_output = llm.generate(message)
        decision = llm_output.tool_call

        # INITIALIZE MEMORY FIRST
        TICKET_STORE[ticket_id] = {
            "facts": {},
            "history": [message],
            "last_decision": decision
        }
        
        # ──────────────────────────────
        # Phase-5 inference (SAFE, reversible)
        # ──────────────────────────────
        inferred = infer_facts(
            intent=decision["intent"],
            entities=decision["entities"],
            history=TICKET_STORE[ticket_id]["history"]
        )

        # Merge inferred facts (do NOT override real facts)
        for k, v in inferred.items():
            if k not in TICKET_STORE[ticket_id]["facts"]:
                TICKET_STORE[ticket_id]["facts"][k] = v
        
        #inference end
        # ──────────────────────────────
        # ──────────────────────────────

        
        # store stable facts only
        for key, value in decision["entities"].items():
            if key in STABLE_FACTS and value != "unknown":
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

        # LLM decision
        llm_output = llm.generate(combined_message)
        decision = llm_output.tool_call

        # normalize issue_type from intent
        if "issue_type" not in decision["entities"]:
            decision["entities"]["issue_type"] = decision["intent"]
        # ──────────────────────────────
        # Phase-4.1: Persist stable facts
        # ──────────────────────────────
        facts = prev["facts"]

        for key, value in decision["entities"].items():
            if key in STABLE_FACTS and value != "unknown":
                facts[key] = value

        prev["last_decision"] = decision

    logger.info(f"LLM decision: {decision}")

    #oh god

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
