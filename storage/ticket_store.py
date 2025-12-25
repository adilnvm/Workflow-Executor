# storage/ticket_store.py

from abc import ABC, abstractmethod
from typing import Dict, Optional


class TicketStore(ABC):
    @abstractmethod
    def get(self, ticket_id: str) -> Optional[Dict]:
        pass

    @abstractmethod
    def set(self, ticket_id: str, data: Dict) -> None:
        pass

    @abstractmethod
    def exists(self, ticket_id: str) -> bool:
        pass

    @abstractmethod
    def delete(self, ticket_id: str) -> None:
        pass
