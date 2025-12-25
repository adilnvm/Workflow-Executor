# storage/redis_store.py

import json
import redis
from typing import Dict, Optional
from storage.ticket_store import TicketStore


class RedisTicketStore(TicketStore):
    def __init__(self, redis_url: str):
        self.client = redis.Redis.from_url(
            redis_url,
            decode_responses=True
        )

    def _key(self, ticket_id: str) -> str:
        return f"ticket:{ticket_id}"

    def get(self, ticket_id: str) -> Optional[Dict]:
        raw = self.client.get(self._key(ticket_id))
        if raw is None:
            return None
        return json.loads(raw)

    def set(self, ticket_id: str, data: Dict) -> None:
        self.client.set(
            self._key(ticket_id),
            json.dumps(data)
        )

    def exists(self, ticket_id: str) -> bool:
        return self.client.exists(self._key(ticket_id)) == 1

    def delete(self, ticket_id: str) -> None:
        self.client.delete(self._key(ticket_id))
