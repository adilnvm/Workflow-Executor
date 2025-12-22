def validate_region(region: str) -> dict:
    if region == "unknown":
        return {
            "valid": False,
            "message": "Unable to identify region"
        }

    return {
        "valid": True,
        "region": region
    }


def check_network_status(region: str) -> dict:
    fake_status = {
        "west_india": "Degraded",
        "north_india": "Operational",
        "south_india": "Operational",
        "east_india": "Down",
        "east_india": "Down",
        "east_india": "Down",
    }

    return {
        "region": region,
        "status": fake_status.get(region, "Unknown")
    }


def suggest_resolution(status: str) -> dict:
    if status == "Operational":
        return {"resolution": "No major outage detected. Restart router and recheck speed."}
    if status == "Degraded":
        return {"resolution": "Network congestion detected in your area. Engineers are working on it."}
    if status == "Down":
        return {"resolution": "Outage confirmed in your area. Expected resolution within 24 hours."}

    return {"resolution": "We are unable to determine the issue. Please contact support."}

