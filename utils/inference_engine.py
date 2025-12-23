# utils/inference_engine.py

METRO_CITIES = {
    "mumbai", "delhi", "bangalore", "chennai", "hyderabad", "pune"
}

def infer_facts(intent: str, entities: dict, history: list) -> dict:
    """
    Phase-5 Inference Engine
    Produces reversible, derived facts ONLY.
    """

    inferred = {}

    # ──────────────────────────────
    # Rule 1: Issue type derivation
    # ──────────────────────────────
    if intent in {"slow_internet", "network_issue", "no_signal"}:
        inferred["issue_type"] = intent

    # ──────────────────────────────
    # Rule 2: Service category
    # ──────────────────────────────
    service = entities.get("service_type", "").lower()

    if "fiber" in service:
        inferred["service_category"] = "fixed_line"
    elif "sim" in service or "mobile" in service:
        inferred["service_category"] = "mobile"

    # ──────────────────────────────
    # Rule 3: Congestion hypothesis
    # ──────────────────────────────
    region = entities.get("region", "").lower()
    text = " ".join(history).lower()

    if (
        intent == "slow_internet"
        and region in METRO_CITIES
        and any(t in text for t in ["evening", "night", "peak"])
    ):
        inferred["possible_cause"] = "congestion"
        inferred["reversible"] = True

    return inferred
