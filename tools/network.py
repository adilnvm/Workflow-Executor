# tools/network.py

def check_outage_backend(region: str) -> dict:
    OUTAGES = {
        "east_india": {"status": "outage", "eta": "4 hours"},
    }

    return OUTAGES.get(region, {"status": "none"})


def check_congestion_backend(region: str) -> dict:
    METRO_REGIONS = {"west_india", "north_india"}

    if region in METRO_REGIONS:
        return {"status": "congested", "window": "peak hours"}

    return {"status": "clear"}


def build_resolution_message(intent: str, cause: str, data: dict) -> str:
    if cause == "outage":
        return f"Network outage detected in your area. Expected resolution in {data.get('eta', 'some time')}."

    if cause == "congestion":
        if intent == "slow_internet":
            return "Network congestion detected. Speeds may improve after peak hours."
        return "Temporary congestion detected in your area."

    return "We are checking network conditions in your area."
