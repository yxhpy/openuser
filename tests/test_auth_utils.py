"""
Tests for authentication utilities (JWT and password hashing).
"""
import pytest
from datetime import timedelta

from src.api.auth_utils import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)


class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_get_password_hash(self):
        """Test password hashing."""
        password = "TestPassword123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$argon2")  # argon2 hash prefix

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "TestPassword123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "TestPassword123"
        wrong_password = "WrongPassword456"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False

    def test_different_hashes_for_same_password(self):
        """Test that same password produces different hashes (salt)."""
        password = "TestPassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTTokens:
    """Test JWT token creation and decoding."""

    def test_create_access_token(self):
        """Test access token creation."""
        data = {"sub": "testuser"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_custom_expiry(self):
        """Test access token creation with custom expiration."""
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=15)
        token = create_access_token(data, expires_delta)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self):
        """Test refresh token creation."""
        data = {"sub": "testuser"}
        token = create_refresh_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_token_valid(self):
        """Test decoding valid token."""
        data = {"sub": "testuser", "extra": "data"}
        token = create_access_token(data)
        decoded = decode_token(token)

        assert decoded is not None
        assert decoded["sub"] == "testuser"
        assert decoded["extra"] == "data"
        assert "exp" in decoded

    def test_decode_token_invalid(self):
        """Test decoding invalid token."""
        invalid_token = "invalid.token.here"
        decoded = decode_token(invalid_token)

        assert decoded is None

    def test_decode_token_malformed(self):
        """Test decoding malformed token."""
        malformed_token = "not-a-jwt-token"
        decoded = decode_token(malformed_token)

        assert decoded is None

    def test_token_contains_expiration(self):
        """Test that token contains expiration claim."""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        decoded = decode_token(token)

        assert decoded is not None
        assert "exp" in decoded
        assert isinstance(decoded["exp"], int)

    def test_different_tokens_for_same_data(self):
        """Test that same data produces different tokens (due to exp)."""
        import time
        data = {"sub": "testuser"}

        token1 = create_access_token(data)
        time.sleep(1)  # Wait to ensure different exp timestamp
        token2 = create_access_token(data)

        assert token1 != token2

        # Both should decode successfully
        decoded1 = decode_token(token1)
        decoded2 = decode_token(token2)

        assert decoded1 is not None
        assert decoded2 is not None
        assert decoded1["sub"] == decoded2["sub"]
