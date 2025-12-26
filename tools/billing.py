# tools/billing.py

def fetch_billing_snapshot(account_type: str) -> dict | None:
    """
    Mocked billing backend.
    In real systems, this hits BSS.
    """

    if account_type == "prepaid":
        return {
            "last_recharge": 199,
            "validity_days": 28,
            "addons": ["data_booster"],
            "balance": 12.5
        }

    if account_type == "postpaid":
        return {
            "monthly_rent": 499,
            "usage_charges": 87,
            "addons": ["international_roaming"],
            "total_due": 586
        }

    return None


def explain_charges(billing_data: dict, intent: str) -> str:
    """
    Deterministic explanation.
    No refunds. No promises. No negotiation.
    """

    if "total_due" in billing_data:
        return (
            f"Your current bill is ₹{billing_data['total_due']}. "
            f"This includes your monthly plan and additional usage or add-ons."
        )

    return (
        f"Your last recharge was ₹{billing_data['last_recharge']} "
        f"with {billing_data['validity_days']} days validity remaining. "
        f"Your current balance is ₹{billing_data['balance']}."
    )
