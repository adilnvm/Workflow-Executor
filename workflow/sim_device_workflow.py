# workflow/sim_device_workflow.py

from tools.sim_device import (
    check_sim_detection,
    check_device_compatibility,
    build_sim_resolution
)

def sim_device_troubleshooting_workflow(context: dict) -> dict:
    """
    Telecom-grade SIM & device troubleshooting workflow.
    Deterministic. No LLM. No guessing.
    """

    device_type = context.get("device_type")
    intent = context.get("intent", "sim_issue")

    steps = []

    # Slot checker enforces this
    if not device_type or device_type == "unknown":
        return {
            "status": "needs_info",
            "reason": "device_type_missing"
        }

    steps.append({"device_type": device_type})

    # Step 1 — SIM detection
    sim_status = check_sim_detection(device_type)
    steps.append({"sim_detection": sim_status})

    if sim_status["status"] == "not_detected":
        return {
            "status": "resolved",
            "steps": steps,
            "resolution": build_sim_resolution("sim_not_detected")
        }

    # Step 2 — Device compatibility
    compatibility = check_device_compatibility(device_type)
    steps.append({"device_compatibility": compatibility})

    if compatibility["status"] == "unsupported":
        return {
            "status": "resolved",
            "steps": steps,
            "resolution": build_sim_resolution("device_unsupported")
        }

    # Step 3 — Unknown issue → escalate
    return {
        "status": "escalated",
        "steps": steps,
        "reason": "sim_device_issue_unresolved"
    }
