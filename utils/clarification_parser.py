# utils/clarification_parser.py

def extract_slot_value(slot: str, message: str):
    """
    Deterministic clarification parser.
    NO LLM. NO MAGIC.
    """

    msg = message.lower().strip()

    if slot == "region":
        return msg

    if slot == "account_type":
        if "prepaid" in msg:
            return "prepaid"
        if "postpaid" in msg:
            return "postpaid"

    if slot == "device_type":
        return msg

    return None
