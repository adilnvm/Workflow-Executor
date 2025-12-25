NETWORK_TROUBLESHOOTING_WORKFLOW = {
    "name": "network_troubleshooting",
    "steps": [
        "validate_region",
        "check_network_status",
        "suggest_resolution"
    ]
}


# workflow/network_workflow.py

def network_troubleshooting_workflow(context: dict) -> dict:
    """
    Realistic telecom network troubleshooting flow.

    Required:
        region (already validated by slot checker)
    Optional:
        intent
        service_type
        account_type
        device_type
    """

    steps = []

    region = context.get("region")
    intent = context.get("intent", "unknown")

    # ──────────────────────────────
    # Step 1: Validate region
    # ──────────────────────────────
    if region == "unknown":
        return {
            "status": "failed",
            "reason": "region_not_provided"
        }

    steps.append({
        "validate_region": {
            "valid": True,
            "region": region
        }
    })

    # ──────────────────────────────
    # Step 2: Check known network issues
    # (mocked for now)
    # ──────────────────────────────
    network_status = "degraded"  # simulated

    steps.append({
        "check_network_status": {
            "region": region,
            "status": network_status
        }
    })

    # ──────────────────────────────
    # Step 3: Intent-based branching
    # ──────────────────────────────
    if intent == "call_drop":
        resolution = (
            "Call drops are being reported in your area. "
            "Ensure VoLTE is enabled on your phone. "
            "If the issue persists, our engineers are working on it."
        )

    elif intent == "slow_internet":
        resolution = (
            "Network congestion detected in your area. "
            "Please try again after some time. "
            "Restarting your device may help."
        )

    elif intent == "no_signal":
        resolution = (
            "No signal issue detected in your region. "
            "Please toggle airplane mode or restart your device."
        )

    else:
        resolution = (
            "We are checking network conditions in your area. "
            "Please try basic troubleshooting steps."
        )

    steps.append({
        "suggest_resolution": {
            "resolution": resolution
        }
    })

    return {
        "status": "resolved",
        "steps": steps
    }
