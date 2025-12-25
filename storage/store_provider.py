# storage/store_provider.py

import os
from storage.memory_store import InMemoryTicketStore
from storage.redis_store import RedisTicketStore
from logger import logger


_store = None


def get_ticket_store():
    global _store
    if _store is not None:
        return _store

    redis_url = os.getenv("REDIS_URL")

    if not redis_url:
        logger.warning("REDIS_URL not set → using in-memory store")
        _store = InMemoryTicketStore()
        return _store

    try:
        store = RedisTicketStore(redis_url)
        # sanity check
        store.client.ping()
        logger.info("Connected to Redis ticket store")
        _store = store
        return _store
    except Exception as e:
        logger.warning(f"Redis unavailable → falling back to memory ({e})")
        _store = InMemoryTicketStore()
        return _store
