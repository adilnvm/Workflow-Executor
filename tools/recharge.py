# tools/recharge.py

def fetch_recharge_status(account_type: str) -> dict:
    """
    Mocked recharge backend.
    In real systems, this hits payment + recharge systems.
    """

    # Simulated outcomes
    if account_type == "prepaid":
        return {
            "status": "success_delayed",
            "sla_minutes": 30
        }

    if account_type == "postpaid":
        return {
            "status": "failed_charged"
        }

    return {
        "status": "unknown"
    }


def build_recharge_resolution(recharge_status: dict) -> str:
    if recharge_status["status"] == "success_delayed":
        return (
            f"Your recharge was successful but is taking longer than usual. "
            f"It should reflect within {recharge_status.get('sla_minutes', 30)} minutes."
        )

    if recharge_status["status"] == "pending":
        return (
            "Your recharge is currently pending. Please wait a few minutes while we process it."
        )

    return "We are checking the status of your recharge."
