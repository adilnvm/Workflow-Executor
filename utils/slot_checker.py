from workflow.slots import WORKFLOW_SLOTS


def get_missing_slot(workflow_name: str, facts: dict):
    workflow = WORKFLOW_SLOTS.get(workflow_name)

    if not workflow:
        return None, None

    for slot in workflow["required"]:
        if slot not in facts or facts[slot] == "unknown":
            question = workflow["questions"].get(slot)
            return slot, question

    return None, None
