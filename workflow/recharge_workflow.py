# workflow/recharge_workflow.py

from tools.recharge import (
    fetch_recharge_status,
    build_recharge_resolution
)

def recharge_resolution_workflow(context: dict) -> dict:
    """
    Telecom-grade recharge resolution workflow.
    Deterministic. No LLM. No financial mutations.
    """

    account_type = context.get("account_type")
    intent = context.get("intent", "recharge_issue")

    steps = []

    # Slot checker already enforces this
    if not account_type or account_type == "unknown":
        return {
            "status": "needs_info",
            "reason": "account_type_missing"
        }

    steps.append({"account_type": account_type})

    # Step 1 — Fetch recharge status
    recharge_status = fetch_recharge_status(account_type)
    steps.append({"recharge_status": recharge_status})

    if recharge_status["status"] == "success_delayed":
        return {
            "status": "resolved",
            "steps": steps,
            "resolution": build_recharge_resolution(recharge_status)
        }

    if recharge_status["status"] == "failed_charged":
        return {
            "status": "escalated",
            "steps": steps,
            "reason": "recharge_failed_but_charged"
        }

    if recharge_status["status"] == "pending":
        return {
            "status": "resolved",
            "steps": steps,
            "resolution": build_recharge_resolution(recharge_status)
        }

    # Unknown or inconsistent state
    return {
        "status": "escalated",
        "steps": steps,
        "reason": "recharge_state_unknown"
    }
