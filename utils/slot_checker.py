from utils.slot_questions import SLOT_QUESTIONS

def get_missing_slot(workflow_name: str, facts: dict) -> tuple[str | None, str | None]:
    REQUIRED_SLOTS = {
        "network_troubleshooting_workflow": ["region", "issue_type"],
        "billing_explanation_workflow": ["account_type"],
    }

    for slot in REQUIRED_SLOTS.get(workflow_name, []):
        if slot not in facts:
            return slot, SLOT_QUESTIONS[slot]

    return None, None
