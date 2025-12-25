# observability/event.py

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict
import uuid

@dataclass
class ObservabilityEvent:
    event_id: str
    timestamp: str
    event_type: str
    ticket_id: str
    payload: Dict[str, Any]

    @staticmethod
    def create(event_type: str, ticket_id: str, payload: Dict[str, Any]):
        return ObservabilityEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat(),
            event_type=event_type,
            ticket_id=ticket_id,
            payload=payload
        )

    def to_dict(self):
        return asdict(self)
