#dont edit or remove any comments although you may or maynot add your own comments

from llm_provider import get_llm
from workflow.registry import WORKFLOW_REGISTRY
from executor.workflow_executor import execute_workflow
from logger import logger

from utils.slot_checker import get_missing_slot   # ← ADDED (Phase-3.2)
from utils.decision_context import build_decision_context # ← ADDED (Phase-3.3)

from llm.local.phi3_llm import Phi3LLM
from llm.real.gemini_llm import QuotaExceededError

from utils.inference_engine import infer_facts

import copy
import uuid

# ──────────────────────────────
# this was moved to storage/store_provider.py for persistence 
# after phase-5 redis is used for ticket storage (persistence across restarts)
# NOTE - InMemoryTicketStore is still used as a fallback if Redis is unavailable
# ──────────────────────────────

# TICKET_STORE = {}
# # Structure:
# # {
# #   ticket_id: {
# #     "facts": {},
# #     "history": [],
# #     "last_decision": {}
# #   }
# # }

# ──────────────────────────────
# ──────────────────────────────
from storage.store_provider import get_ticket_store

ticket_store = get_ticket_store()


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
    # 🔒 SAFETY: snapshot ticket before processing 
    # ──────────────────────────────
    ticket_snapshot = copy.deepcopy(
        ticket_store.get(ticket_id) if ticket_id else None
    )

    try:
        # ──────────────────────────────
        # 🔒 SAFETY: handle lost tickets (restart / TTL / crash) ...gpt you rock!!
        # ──────────────────────────────
        if ticket_id is not None and not ticket_store.exists(ticket_id):
            logger.warning("Unknown ticket_id → starting new session")
            ticket_id = None

        # ──────────────────────────────
        # 1. New ticket
        # ──────────────────────────────
        if ticket_id is None:
            ticket_id = str(uuid.uuid4())

            llm_output = llm.generate(message)
            decision = llm_output.tool_call

            # INITIALIZE MEMORY FIRST
            ticket_store.set(ticket_id, {
                "facts": {},
                "history": [message],
                "last_decision": decision
            })

            ticket = ticket_store.get(ticket_id)

            # ──────────────────────────────
            # Phase-5 inference (SAFE, reversible)
            # ──────────────────────────────
            inferred = infer_facts(
                intent=decision["intent"],
                entities=decision["entities"],
                history=ticket["history"]
            )

            # Merge inferred facts (do NOT override real facts)
            for k, v in inferred.items():
                if k not in ticket["facts"]:
                    ticket["facts"][k] = v

            # store stable facts only
            for key, value in decision["entities"].items():
                if key in STABLE_FACTS and value != "unknown":
                    ticket["facts"][key] = value

            ticket_store.set(ticket_id, ticket)

        # ──────────────────────────────
        # 2. Clarification reply
        # ──────────────────────────────
        else:
            prev = ticket_store.get(ticket_id)

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

            # normalize issue_type from intent
            if "issue_type" not in decision["entities"]:
                decision["entities"]["issue_type"] = decision["intent"]

            # ──────────────────────────────
            # Phase-4.1: Persist stable facts
            # ──────────────────────────────
            for key, value in decision["entities"].items():
                if key in STABLE_FACTS and value != "unknown":
                    prev["facts"][key] = value

            prev["last_decision"] = decision
            ticket_store.set(ticket_id, prev)

        logger.info(f"LLM decision: {decision}")

        #oh god

        # ──────────────────────────────
        # 3. Ask clarification
        # ──────────────────────────────
        CONFIDENCE_THRESHOLD = 0.6

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
        ticket = ticket_store.get(ticket_id)
        facts = ticket["facts"]
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

    except Exception:
        # ──────────────────────────────
        # Phase-5 rollback on failure
        # ──────────────────────────────
        logger.exception("Phase-5 failure → rolling back ticket state")

        if ticket_snapshot is not None:
            ticket_store.set(ticket_id, ticket_snapshot)
        else:
            ticket_store.delete(ticket_id)

        return {
            "summary": "Something went wrong while processing your request. Please try again.",
            "workflow_result": {
                "status": "retry",
                "ticket_id": ticket_id
            },
            "confidence": 0.0
        }


# meh
