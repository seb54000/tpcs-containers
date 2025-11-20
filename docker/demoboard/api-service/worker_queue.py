import json
import os
from typing import Any, Dict

import redis


REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
QUEUE_NAME = os.getenv("REDIS_QUEUE", "jobs")


def _get_client() -> redis.Redis:
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)


def publish_job(payload: Dict[str, Any]) -> None:
    client = _get_client()
    client.rpush(QUEUE_NAME, json.dumps(payload))
