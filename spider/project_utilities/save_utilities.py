"""Utilities for saving date to db."""

import json
from typing import Any

import redis

from apps.advertisements.handlers import adv_handlers
from apps.advertisements.schemas import CreateAdvIn
from apps.common.dependencies import get_session
from settings import Settings


def save_adv_data_to_db(adv_data: dict) -> None:
    """Save data to db."""
    session = next(get_session())
    schema = CreateAdvIn(**adv_data)
    adv_handlers.create_adv(session, schema)


def save_adv_data(adv_data: dict) -> str:
    """Save data with catching errors."""
    message = 'Successfully saved data to db.'
    try:
        save_adv_data_to_db(adv_data)
    except Exception as ex:
        message = str(ex)
    return message


class RedisStorage:
    """Redis storage functionality."""

    redis_instance = redis.StrictRedis(
        host=Settings.REDIS_HOST,
        port=Settings.REDIS_PORT,
        db=0,
    )

    def save_data(self, key: str, data_value: Any) -> None:
        """Save data to redis."""
        self.redis_instance.set(key, json.dumps(data_value))

    def get_data(self, key: str) -> Any:
        """Get value from redis."""
        key_data = self.redis_instance.get(key)
        if key_data is not None and isinstance(key_data, (str, bytes, bytearray)):
            return json.loads(key_data)
        return key_data

    def delete_data(self, key: str) -> None:
        """Delete value from redis."""
        self.redis_instance.delete(key)


class UrlRedisStorage(RedisStorage):
    """Redis storage with specific functionality."""

    def add_urls(self, url_list: list[str]) -> None:
        """Add url to 'urls' key."""
        urls = self.get_data('urls')
        if urls is not None:
            urls += url_list
        else:
            urls = url_list
        self.save_data('urls', urls)


url_redis_storage = UrlRedisStorage()
