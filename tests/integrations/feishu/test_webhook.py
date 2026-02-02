"""Tests for Feishu webhook handler."""

import pytest
import hashlib
import json
from unittest.mock import Mock

from src.integrations.feishu.webhook import (
    FeishuWebhookHandler,
    FeishuEventType
)


class TestFeishuWebhookHandler:
    """Test cases for FeishuWebhookHandler."""

    def test_init(self):
        """Test initialization."""
        handler = FeishuWebhookHandler(
            verification_token="test_token",
            encrypt_key="test_key"
        )
        assert handler.verification_token == "test_token"
        assert handler.encrypt_key == "test_key"
        assert handler.event_handlers == {}

    def test_register_handler(self):
        """Test registering event handler."""
        handler = FeishuWebhookHandler()
        mock_handler = Mock()

        handler.register_handler("test_event", mock_handler)

        assert "test_event" in handler.event_handlers
        assert handler.event_handlers["test_event"] == mock_handler

    def test_verify_signature_success(self):
        """Test successful signature verification."""
        handler = FeishuWebhookHandler(encrypt_key="test_key")

        timestamp = "1234567890"
        nonce = "random_nonce"
        encrypt = '{"test":"data"}'

        # Calculate expected signature
        content = f"{timestamp}{nonce}test_key{encrypt}"
        expected_signature = hashlib.sha256(content.encode()).hexdigest()

        result = handler.verify_signature(
            timestamp=timestamp,
            nonce=nonce,
            encrypt=encrypt,
            signature=expected_signature
        )

        assert result is True

    def test_verify_signature_failure(self):
        """Test failed signature verification."""
        handler = FeishuWebhookHandler(encrypt_key="test_key")

        result = handler.verify_signature(
            timestamp="1234567890",
            nonce="random_nonce",
            encrypt='{"test":"data"}',
            signature="invalid_signature"
        )

        assert result is False

    def test_verify_signature_no_key(self):
        """Test signature verification skipped when no key configured."""
        handler = FeishuWebhookHandler()

        result = handler.verify_signature(
            timestamp="1234567890",
            nonce="random_nonce",
            encrypt='{"test":"data"}',
            signature="any_signature"
        )

        assert result is True

    def test_handle_url_verification_success(self):
        """Test URL verification challenge."""
        handler = FeishuWebhookHandler(verification_token="test_token")

        data = {
            "token": "test_token",
            "challenge": "test_challenge"
        }

        result = handler.handle_url_verification(data)

        assert result["challenge"] == "test_challenge"

    def test_handle_url_verification_invalid_token(self):
        """Test URL verification with invalid token."""
        handler = FeishuWebhookHandler(verification_token="test_token")

        data = {
            "token": "wrong_token",
            "challenge": "test_challenge"
        }

        with pytest.raises(ValueError, match="Invalid verification token"):
            handler.handle_url_verification(data)

    def test_handle_url_verification_no_token_check(self):
        """Test URL verification without token check."""
        handler = FeishuWebhookHandler()

        data = {
            "token": "any_token",
            "challenge": "test_challenge"
        }

        result = handler.handle_url_verification(data)

        assert result["challenge"] == "test_challenge"

    def test_handle_event_url_verification(self):
        """Test handling URL verification event."""
        handler = FeishuWebhookHandler(verification_token="test_token")

        event_data = {
            "type": FeishuEventType.URL_VERIFICATION,
            "token": "test_token",
            "challenge": "test_challenge"
        }

        result = handler.handle_event(event_data)

        assert result["challenge"] == "test_challenge"

    def test_handle_event_with_handler(self):
        """Test handling event with registered handler."""
        handler = FeishuWebhookHandler()
        mock_handler = Mock(return_value={"processed": True})

        handler.register_handler(FeishuEventType.MESSAGE_RECEIVE, mock_handler)

        event_data = {
            "header": {
                "event_type": FeishuEventType.MESSAGE_RECEIVE
            },
            "event": {
                "message": {"text": "Hello"}
            }
        }

        result = handler.handle_event(event_data)

        assert result["processed"] is True
        mock_handler.assert_called_once_with({"message": {"text": "Hello"}})

    def test_handle_event_no_handler(self):
        """Test handling event without registered handler."""
        handler = FeishuWebhookHandler()

        event_data = {
            "header": {
                "event_type": "unknown_event"
            },
            "event": {}
        }

        result = handler.handle_event(event_data)

        assert result is None

    def test_process_webhook_success(self):
        """Test processing webhook request."""
        handler = FeishuWebhookHandler()
        mock_handler = Mock(return_value={"result": "ok"})
        handler.register_handler(FeishuEventType.MESSAGE_RECEIVE, mock_handler)

        body = {
            "header": {
                "event_type": FeishuEventType.MESSAGE_RECEIVE
            },
            "event": {
                "message": {"text": "Hello"}
            }
        }

        result = handler.process_webhook(body)

        assert result["result"] == "ok"

    def test_process_webhook_with_signature_verification(self):
        """Test processing webhook with signature verification."""
        handler = FeishuWebhookHandler(encrypt_key="test_key")

        # Create body with all data first
        body = {
            "type": FeishuEventType.URL_VERIFICATION,
            "challenge": "test_challenge"
        }
        timestamp = "1234567890"
        nonce = "random_nonce"
        encrypt = json.dumps(body, separators=(",", ":"))

        # Calculate signature
        content = f"{timestamp}{nonce}test_key{encrypt}"
        signature = hashlib.sha256(content.encode()).hexdigest()

        headers = {
            "X-Lark-Request-Timestamp": timestamp,
            "X-Lark-Request-Nonce": nonce,
            "X-Lark-Signature": signature
        }

        result = handler.process_webhook(body, headers)

        assert result["challenge"] == "test_challenge"

    def test_process_webhook_invalid_signature(self):
        """Test processing webhook with invalid signature."""
        handler = FeishuWebhookHandler(encrypt_key="test_key")

        body = {"test": "data"}
        headers = {
            "X-Lark-Request-Timestamp": "1234567890",
            "X-Lark-Request-Nonce": "random_nonce",
            "X-Lark-Signature": "invalid_signature"
        }

        with pytest.raises(ValueError, match="Invalid signature"):
            handler.process_webhook(body, headers)

    def test_process_webhook_default_response(self):
        """Test processing webhook with default response."""
        handler = FeishuWebhookHandler()

        body = {
            "header": {
                "event_type": "unknown_event"
            },
            "event": {}
        }

        result = handler.process_webhook(body)

        assert result["code"] == 0
        assert result["msg"] == "success"

