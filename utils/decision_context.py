def build_decision_context(ticket: dict, new_message: str) -> str:
    """
    thiss builds a stable, (cumulative )context for decision re-evaluation........
    """

    facts = ticket.get("facts", {})
    history = ticket.get("history", [])
    last_decision = ticket.get("last_decision", {})

    context = f"""
Original user issue:
{history[0] if history else ""}

Known facts:
{facts}

Previous decision:
{last_decision}

New user message:
{new_message}
"""

    return context.strip()
