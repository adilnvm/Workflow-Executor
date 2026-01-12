
from llm.llm_provider import get_llm
from workflow.registry import WORKFLOW_REGISTRY
from logger import logger

from utils.slot_checker import get_missing_slot
from utils.decision_context import build_decision_context
from utils.inference_engine import infer_facts
from utils.region_mapper import normalize_region

import copy
import uuid

from observability.bus import bus
from observability.event import ObservabilityEvent


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

            # Emit observability event

            bus.emit(ObservabilityEvent.create(
                event_type="ticket_created",
                ticket_id=ticket_id,
                payload={"message": message}
            ))

            llm_output = llm.generate(message)
            decision = llm_output.tool_call  # expect JSON response ....dis is whre the LLM decision is made
            bus.emit(ObservabilityEvent.create(
                event_type="llm_decision_made",
                ticket_id=ticket_id,
                payload={
                    "intent": decision["intent"],
                    "confidence": decision["confidence"],
                    "workflow": decision["workflow"]
                }
            ))

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
        # 2. Clarification reply (NO LLM CALL)
        # ──────────────────────────────
        else:
            ticket = ticket_store.get(ticket_id)

            if not ticket:
                return {
                    "summary": "Session expired. Please describe your issue again.",
                    "workflow_result": {"status": "expired"},
                    "confidence": 0.0
                }

            ticket["history"].append(message)

            logger.info(f"[CLARIFICATION] message='{message}'")

            # 🔑 FILL SLOT BEFORE ANY CHECK
            workflow_name = ticket["last_decision"]["workflow"]
            missing_slot, _ = get_missing_slot(workflow_name, ticket["facts"])

            if missing_slot:
                from utils.clarification_parser import extract_slot_value

                value = extract_slot_value(missing_slot, message)
                logger.info(f"[CLARIFICATION] extracted {missing_slot}={value}")

                if value:
                    ticket["facts"][missing_slot] = value

            ticket_store.set(ticket_id, ticket)

            decision = ticket["last_decision"]


        logger.info(f"Decision in effect: {decision}")

        # ──────────────────────────────
        # 3. Normalize region BEFORE slot checking
        # ──────────────────────────────
        facts = ticket_store.get(ticket_id)["facts"]

        city = (
            facts.get("location")
            or facts.get("city")
            or facts.get("region")
        )

        if city:
            facts["region"] = normalize_region(city)

        ticket_store.set(ticket_id, ticket_store.get(ticket_id))

        # ──────────────────────────────
        # 4. Slot-based clarification
        # ──────────────────────────────
        workflow_name = decision["workflow"]
        missing_slot, question = get_missing_slot(workflow_name, facts)

        if missing_slot:
            bus.emit(ObservabilityEvent.create(
                event_type="slot_missing",
                ticket_id=ticket_id,
                payload={
                    "workflow": workflow_name,
                    "slot": missing_slot
                }
            ))


            return {
                "summary": question,
                "workflow_result": {
                    "status": "needs_info",
                    "missing_slot": missing_slot,
                    "ticket_id": ticket_id
                },
                "confidence": decision["confidence"]
            }
        logger.info(f"Decision in effect: {decision}")

        # ──────────────────────────────
        # 5. Execute workflow (DETERMINISTIC)
        # ──────────────────────────────
        workflow_fn = WORKFLOW_REGISTRY.get(workflow_name)

        if workflow_fn is None:
            return {
                "summary": "This issue needs human support.",
                "workflow_result": {
                    "status": "escalated",
                    "ticket_id": ticket_id
                },
                "confidence": decision["confidence"]
            }
        
        # yapping tiiimeee
        bus.emit(ObservabilityEvent.create(
            event_type="workflow_selected",
            ticket_id=ticket_id,
            payload={
                "workflow": workflow_name,
                "context": facts
            }
        ))

        result = workflow_fn(facts)

        summary = result.get("resolution")

        if not summary:
            if result["status"] == "escalated":
                summary = "We could not identify a known network issue in your area. This has been escalated for further investigation."
            else:
                summary = "We checked network conditions in your area."

        return {
            "summary": summary,
            "workflow_result": {
                **result,
                "ticket_id": ticket_id
            },
            "confidence": decision["confidence"]
        }


    except Exception:
        logger.exception("Phase-5 failure → rolling back ticket state")

        if ticket_snapshot is not None:
            ticket_store.set(ticket_id, ticket_snapshot)
        else:
            ticket_store.delete(ticket_id)

        bus.emit(ObservabilityEvent.create(
            event_type="rollback_triggered",
            ticket_id=ticket_id,
            payload={"error": "unhandled_exception"}
        ))

        return {
            "summary": "Something went wrong while processing your request. Please try again.",
            "workflow_result": {
                "status": "retry",
                "ticket_id": ticket_id
            },
            "confidence": 0.0
        }


# meh
