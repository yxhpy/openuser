"""Tests for Redis manager"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock

from src.core.redis_manager import RedisManager


@pytest.fixture
def mock_redis() -> Mock:
    """Create mock Redis client"""
    with patch("src.core.redis_manager.redis.Redis") as mock:
        client = Mock()
        mock.return_value = client
        yield client


@pytest.fixture
def redis_manager(mock_redis: Mock) -> RedisManager:
    """Create RedisManager with mocked Redis"""
    with patch("src.core.redis_manager.ConnectionPool"):
        manager = RedisManager()
        manager.client = mock_redis
        return manager


class TestRedisManager:
    """Test RedisManager class"""

    def test_init(self) -> None:
        """Test RedisManager initialization"""
        with patch("src.core.redis_manager.ConnectionPool") as mock_pool:
            with patch("src.core.redis_manager.redis.Redis") as mock_redis:
                manager = RedisManager(
                    host="testhost",
                    port=6380,
                    db=1,
                    password="testpass",
                    max_connections=100,
                )

                mock_pool.assert_called_once_with(
                    host="testhost",
                    port=6380,
                    db=1,
                    password="testpass",
                    decode_responses=True,
                    max_connections=100,
                )
                mock_redis.assert_called_once()

    def test_get(self, redis_manager: RedisManager, mock_redis: Mock) -> None:
        """Test get method"""
        mock_redis.get.return_value = "test_value"

        result = redis_manager.get("test_key")

        assert result == "test_value"
        mock_redis.get.assert_called_once_with("test_key")

    def test_get_none(self, redis_manager: RedisManager, mock_redis: Mock) -> None:
        """Test get method when key doesn't exist"""
        mock_redis.get.return_value = None

        result = redis_manager.get("nonexistent")

        assert result is None

    def test_set(self, redis_manager: RedisManager, mock_redis: Mock) -> None:
        """Test set method"""
        mock_redis.set.return_value = True

        result = redis_manager.set("test_key", "test_value")

        assert result is True
        mock_redis.set.assert_called_once_with("test_key", "test_value", ex=None, nx=False)

    def test_set_with_expiration(
        self, redis_manager: RedisManager, mock_redis: Mock
    ) -> None:
        """Test set method with expiration"""
        mock_redis.set.return_value = True

        result = redis_manager.set("test_key", "test_value", ex=3600)

        assert result is True
        mock_redis.set.assert_called_once_with("test_key", "test_value", ex=3600, nx=False)

    def test_set_nx(self, redis_manager: RedisManager, mock_redis: Mock) -> None:
        """Test set method with nx flag"""
        mock_redis.set.return_value = True

        result = redis_manager.set("test_key", "test_value", nx=True)

        assert result is True
        mock_redis.set.assert_called_once_with("test_key", "test_value", ex=None, nx=True)

    def test_delete(self, redis_manager: RedisManager, mock_redis: Mock) -> None:
        """Test delete method"""
        mock_redis.delete.return_value = 2

        result = redis_manager.delete("key1", "key2")

        assert result == 2
        mock_redis.delete.assert_called_once_with("key1", "key2")

    def test_exists(self, redis_manager: RedisManager, mock_redis: Mock) -> None:
        """Test exists method"""
        mock_redis.exists.return_value = 1

        result = redis_manager.exists("test_key")

        assert result == 1
        mock_redis.exists.assert_called_once_with("test_key")

    def test_expire(self, redis_manager: RedisManager, mock_redis: Mock) -> None:
        """Test expire method"""
        mock_redis.expire.return_value = True

        result = redis_manager.expire("test_key", 3600)

        assert result is True
        mock_redis.expire.assert_called_once_with("test_key", 3600)

    def test_ttl(self, redis_manager: RedisManager, mock_redis: Mock) -> None:
        """Test ttl method"""
        mock_redis.ttl.return_value = 3600

        result = redis_manager.ttl("test_key")

        assert result == 3600
        mock_redis.ttl.assert_called_once_with("test_key")

    def test_get_json(self, redis_manager: RedisManager, mock_redis: Mock) -> None:
        """Test get_json method"""
        test_data = {"key": "value", "number": 42}
        mock_redis.get.return_value = json.dumps(test_data)

        result = redis_manager.get_json("test_key")

        assert result == test_data
        mock_redis.get.assert_called_once_with("test_key")

    def test_get_json_none(self, redis_manager: RedisManager, mock_redis: Mock) -> None:
        """Test get_json when key doesn't exist"""
        mock_redis.get.return_value = None

        result = redis_manager.get_json("nonexistent")

        assert result is None

    def test_set_json(self, redis_manager: RedisManager, mock_redis: Mock) -> None:
        """Test set_json method"""
        test_data = {"key": "value", "number": 42}
        mock_redis.set.return_value = True

        result = redis_manager.set_json("test_key", test_data)

        assert result is True
        mock_redis.set.assert_called_once()
        call_args = mock_redis.set.call_args
        assert call_args[0][0] == "test_key"
        assert json.loads(call_args[0][1]) == test_data

    def test_hget(self, redis_manager: RedisManager, mock_redis: Mock) -> None:
        """Test hget method"""
        mock_redis.hget.return_value = "field_value"

        result = redis_manager.hget("test_hash", "field_key")

        assert result == "field_value"
        mock_redis.hget.assert_called_once_with("test_hash", "field_key")

    def test_hset(self, redis_manager: RedisManager, mock_redis: Mock) -> None:
        """Test hset method"""
        mock_redis.hset.return_value = 1

        result = redis_manager.hset("test_hash", "field_key", "field_value")

        assert result == 1
        mock_redis.hset.assert_called_once_with("test_hash", "field_key", "field_value")

    def test_hgetall(self, redis_manager: RedisManager, mock_redis: Mock) -> None:
        """Test hgetall method"""
        test_hash = {"field1": "value1", "field2": "value2"}
        mock_redis.hgetall.return_value = test_hash

        result = redis_manager.hgetall("test_hash")

        assert result == test_hash
        mock_redis.hgetall.assert_called_once_with("test_hash")

    def test_hdel(self, redis_manager: RedisManager, mock_redis: Mock) -> None:
        """Test hdel method"""
        mock_redis.hdel.return_value = 2

        result = redis_manager.hdel("test_hash", "field1", "field2")

        assert result == 2
        mock_redis.hdel.assert_called_once_with("test_hash", "field1", "field2")

    def test_ping_success(self, redis_manager: RedisManager, mock_redis: Mock) -> None:
        """Test ping method when connection is successful"""
        mock_redis.ping.return_value = True

        result = redis_manager.ping()

        assert result is True
        mock_redis.ping.assert_called_once()

    def test_ping_failure(self, redis_manager: RedisManager, mock_redis: Mock) -> None:
        """Test ping method when connection fails"""
        import redis as redis_module

        mock_redis.ping.side_effect = redis_module.ConnectionError()

        result = redis_manager.ping()

        assert result is False

    def test_flushdb(self, redis_manager: RedisManager, mock_redis: Mock) -> None:
        """Test flushdb method"""
        mock_redis.flushdb.return_value = True

        result = redis_manager.flushdb()

        assert result is True
        mock_redis.flushdb.assert_called_once()

    def test_close(self, redis_manager: RedisManager, mock_redis: Mock) -> None:
        """Test close method"""
        redis_manager.close()

        mock_redis.close.assert_called_once()
