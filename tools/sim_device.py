# tools/sim_device.py

def check_sim_detection(device_type: str) -> dict:
    """
    Mocked SIM detection logic.
    """

    if device_type.lower() in {"iphone_12", "iphone_13"}:
        return {"status": "detected"}

    if device_type.lower() == "unknown_device":
        return {"status": "not_detected"}

    return {"status": "detected"}


def check_device_compatibility(device_type: str) -> dict:
    """
    Mocked compatibility check.
    """

    UNSUPPORTED = {"old_android_5"}

    if device_type.lower() in UNSUPPORTED:
        return {"status": "unsupported"}

    return {"status": "supported"}


def build_sim_resolution(issue_type: str) -> str:
    if issue_type == "sim_not_detected":
        return (
            "Your SIM is not being detected. Please reinsert the SIM and restart your device. "
            "If the issue persists, visit a nearby service center."
        )

    if issue_type == "device_unsupported":
        return (
            "Your device may not be fully compatible with this network. "
            "Please check supported device lists or contact support."
        )

    return "We are checking SIM and device compatibility."
