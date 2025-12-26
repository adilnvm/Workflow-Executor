# workflow/network_workflow.py

from tools.network import (
    check_outage_backend,
    check_congestion_backend,
    build_resolution_message
)

def network_troubleshooting_workflow(context: dict) -> dict:
    """
    Telecom-grade Tier-1 network troubleshooting.
    Deterministic. No LLM. No questions.
    """

    region = context.get("region")
    intent = context.get("intent", "unknown")

    steps = []

    # Step 1 — Region must exist (slot checker already enforced this)
    if not region or region == "unknown":
        return {
            "status": "needs_info",
            "reason": "region_missing"
        }

    steps.append({"region_validated": region})

    # Step 2 — Outage check
    outage = check_outage_backend(region)
    steps.append({"outage_check": outage})

    if outage["status"] == "outage":
        return {
            "status": "resolved",
            "steps": steps,
            "resolution": build_resolution_message(
                intent=intent,
                cause="outage",
                data=outage
            )
        }

    # Step 3 — Congestion check
    congestion = check_congestion_backend(region)
    steps.append({"congestion_check": congestion})

    if congestion["status"] == "congested":
        return {
            "status": "resolved",
            "steps": steps,
            "resolution": build_resolution_message(
                intent=intent,
                cause="congestion",
                data=congestion
            )
        }

    # Step 4 — Unknown → escalate
    return {
        "status": "escalated",
        "steps": steps,
        "reason": "no_known_network_issue"
    }
