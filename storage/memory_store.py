from typing import Dict, Optional
from storage.ticket_store import TicketStore


class InMemoryTicketStore(TicketStore):
    def __init__(self):
        self._store: Dict[str, Dict] = {}

    def get(self, ticket_id: str) -> Optional[Dict]:
        return self._store.get(ticket_id)

    def set(self, ticket_id: str, data: Dict) -> None:
        self._store[ticket_id] = data

    def exists(self, ticket_id: str) -> bool:
        return ticket_id in self._store

    def delete(self, ticket_id: str) -> None:
        self._store.pop(ticket_id, None)
