# workflow/billing_workflow.py

from tools.billing import (
    fetch_billing_snapshot,
    explain_charges
)

def billing_explanation_workflow(context: dict) -> dict:
    """
    Telecom-grade Tier-1 billing explanation workflow.
    Deterministic. No LLM. No billing mutations.
    """

    account_type = context.get("account_type")
    intent = context.get("intent", "billing_issue")

    steps = []

    # Slot checker should already enforce this
    if not account_type or account_type == "unknown":
        return {
            "status": "needs_info",
            "reason": "account_type_missing"
        }

    steps.append({"account_type": account_type})

    # Step 1 — Fetch billing snapshot
    billing_data = fetch_billing_snapshot(account_type)
    steps.append({"billing_snapshot_fetched": True})

    if billing_data is None:
        return {
            "status": "escalated",
            "steps": steps,
            "reason": "billing_data_unavailable"
        }

    # Step 2 — Deterministic explanation
    explanation = explain_charges(
        billing_data=billing_data,
        intent=intent
    )

    return {
        "status": "resolved",
        "steps": steps,
        "resolution": explanation
    }
