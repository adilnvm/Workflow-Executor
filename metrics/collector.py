# ts is metrics/collector.py 
# ;)
# you take the man out of the city not the city out the man

from collections import defaultdict

class MetricsCollector:
    def __init__(self):
        self.total_tickets = 0
        self.resolved = 0
        self.escalated = 0
        self.slot_missing = defaultdict(int)

    def record(self, event_type: str, payload: dict):
        if event_type == "ticket_created":
            self.total_tickets += 1

        elif event_type == "workflow_resolved":
            self.resolved += 1

        elif event_type == "workflow_escalated":
            self.escalated += 1

        elif event_type == "slot_missing":
            slot = payload.get("slot")
            if slot:
                self.slot_missing[slot] += 1

    def snapshot(self):
        return {
            "total_tickets": self.total_tickets,
            "resolved": self.resolved,
            "escalated": self.escalated,
            "slot_missing_frequency": dict(self.slot_missing)
        }


metrics = MetricsCollector()
