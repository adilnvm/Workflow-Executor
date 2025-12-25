from utils.slot_questions import SLOT_QUESTIONS

# utils/slot_checker.py

"""
Slot-based clarification logic.

RULES:
1. Intent is NEVER a slot
2. Derived slots must NOT be requested
3. Each clarification fills exactly ONE slot
4. Slot checker blocks execution ONLY if workflow cannot proceed
"""

# Workflow → required execution slots
REQUIRED_SLOTS = {
    "network_troubleshooting_workflow": [
        "region"
    ],
    "billing_explanation_workflow": [
        "account_type"
    ],
    "recharge_resolution_workflow": [
        "account_type"
    ],
    "sim_device_troubleshooting_workflow": [
        "device_type"
    ],
}


def get_missing_slot(workflow_name: str, facts: dict):
    """
    Returns:
        (missing_slot, clarification_question)
        or (None, None) if execution can proceed
    """

    required = REQUIRED_SLOTS.get(workflow_name, [])

    for slot in required:
        value = facts.get(slot)

        if value is None or value == "unknown":
            return slot, SLOT_QUESTIONS[slot]

    return None, None

