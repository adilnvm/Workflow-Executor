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
        "india": "Operational",
        "us": "Degraded",
        "europe": "Down"
    }

    return {
        "region": region,
        "status": fake_status.get(region, "Unknown")
    }


def suggest_resolution(status: str) -> dict:
    if status == "Operational":
        return {"resolution": "Restart router and recheck"}
    if status == "Degraded":
        return {"resolution": "Issue under observation"}
    if status == "Down":
        return {"resolution": "Outage detected in your area. Contact ISP."}

    return {"resolution": "Unable to determine resolution"}
