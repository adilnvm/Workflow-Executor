def check_network_status(region: str) -> dict:
    fake_db = {
        "india": "Operational",
        "us": "Degraded",
        "europe": "Down",
        "unknown": "Unknown"
    }

    return {
        "region": region,
        "status": fake_db.get(region, "Unknown")
    }
