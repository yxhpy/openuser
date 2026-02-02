"""Redis manager for caching and session management"""

import json
from typing import Any, Optional

import redis
from redis.connection import ConnectionPool


class RedisManager:
    """Redis connection and cache management"""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        decode_responses: bool = True,
        max_connections: int = 50,
    ) -> None:
        """
        Initialize Redis manager

        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            password: Redis password (optional)
            decode_responses: Whether to decode responses to strings
            max_connections: Maximum number of connections in pool
        """
        self.pool = ConnectionPool(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=decode_responses,
            max_connections=max_connections,
        )
        self.client = redis.Redis(connection_pool=self.pool)

    def get(self, key: str) -> Optional[str]:
        """
        Get value by key

        Args:
            key: Cache key

        Returns:
            Value or None if not found
        """
        return self.client.get(key)

    def set(
        self, key: str, value: str, ex: Optional[int] = None, nx: bool = False
    ) -> bool:
        """
        Set key-value pair

        Args:
            key: Cache key
            value: Value to store
            ex: Expiration time in seconds (optional)
            nx: Only set if key doesn't exist

        Returns:
            True if successful
        """
        return bool(self.client.set(key, value, ex=ex, nx=nx))

    def delete(self, *keys: str) -> int:
        """
        Delete one or more keys

        Args:
            keys: Keys to delete

        Returns:
            Number of keys deleted
        """
        return self.client.delete(*keys)

    def exists(self, *keys: str) -> int:
        """
        Check if keys exist

        Args:
            keys: Keys to check

        Returns:
            Number of existing keys
        """
        return self.client.exists(*keys)

    def expire(self, key: str, seconds: int) -> bool:
        """
        Set expiration time for a key

        Args:
            key: Cache key
            seconds: Expiration time in seconds

        Returns:
            True if successful
        """
        return bool(self.client.expire(key, seconds))

    def ttl(self, key: str) -> int:
        """
        Get time to live for a key

        Args:
            key: Cache key

        Returns:
            TTL in seconds, -1 if no expiration, -2 if key doesn't exist
        """
        return self.client.ttl(key)

    def get_json(self, key: str) -> Optional[Any]:
        """
        Get JSON value by key

        Args:
            key: Cache key

        Returns:
            Parsed JSON value or None
        """
        value = self.get(key)
        if value is None:
            return None
        return json.loads(value)

    def set_json(
        self, key: str, value: Any, ex: Optional[int] = None, nx: bool = False
    ) -> bool:
        """
        Set JSON value

        Args:
            key: Cache key
            value: Value to store (will be JSON serialized)
            ex: Expiration time in seconds (optional)
            nx: Only set if key doesn't exist

        Returns:
            True if successful
        """
        json_value = json.dumps(value)
        return self.set(key, json_value, ex=ex, nx=nx)

    def hget(self, name: str, key: str) -> Optional[str]:
        """
        Get hash field value

        Args:
            name: Hash name
            key: Field key

        Returns:
            Field value or None
        """
        return self.client.hget(name, key)

    def hset(self, name: str, key: str, value: str) -> int:
        """
        Set hash field value

        Args:
            name: Hash name
            key: Field key
            value: Field value

        Returns:
            1 if new field, 0 if updated
        """
        return self.client.hset(name, key, value)

    def hgetall(self, name: str) -> dict:
        """
        Get all hash fields

        Args:
            name: Hash name

        Returns:
            Dictionary of all fields
        """
        return self.client.hgetall(name)

    def hdel(self, name: str, *keys: str) -> int:
        """
        Delete hash fields

        Args:
            name: Hash name
            keys: Field keys to delete

        Returns:
            Number of fields deleted
        """
        return self.client.hdel(name, *keys)

    def ping(self) -> bool:
        """
        Test connection to Redis

        Returns:
            True if connected
        """
        try:
            return self.client.ping()
        except redis.ConnectionError:
            return False

    def flushdb(self) -> bool:
        """
        Clear current database

        Returns:
            True if successful
        """
        return bool(self.client.flushdb())

    def close(self) -> None:
        """Close Redis connection"""
        self.client.close()
