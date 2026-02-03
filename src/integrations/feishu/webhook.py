"""Feishu webhook handler for receiving and processing events.

This module handles:
- Webhook event reception
- Event signature verification
- Challenge verification for webhook setup
- Event type routing
- Error handling
"""

import hashlib
import hmac
import json
from enum import Enum
from typing import Any, Callable, Dict, Optional


class FeishuEventType(str, Enum):
    """Feishu event types."""

    URL_VERIFICATION = "url_verification"
    MESSAGE_RECEIVE = "im.message.receive_v1"
    MESSAGE_READ = "im.message.message_read_v1"
    APP_OPEN = "app_open"
    APP_STATUS_CHANGE = "app_status_change"
    CARD_ACTION = "card.action.trigger"


class FeishuWebhookHandler:
    """Handler for Feishu webhook events.

    Handles event verification, routing, and processing.

    Attributes:
        verification_token: Token for challenge verification
        encrypt_key: Key for event signature verification
        event_handlers: Dict mapping event types to handler functions
    """

    def __init__(self, verification_token: Optional[str] = None, encrypt_key: Optional[str] = None):
        """Initialize webhook handler.

        Args:
            verification_token: Token for URL verification challenge
            encrypt_key: Key for verifying event signatures
        """
        self.verification_token = verification_token
        self.encrypt_key = encrypt_key
        self.event_handlers: Dict[str, Callable] = {}

    def register_handler(self, event_type: str, handler: Callable[[Dict[str, Any]], Any]) -> None:
        """Register event handler for specific event type.

        Args:
            event_type: Event type to handle
            handler: Callable that processes the event
        """
        self.event_handlers[event_type] = handler

    def verify_signature(self, timestamp: str, nonce: str, encrypt: str, signature: str) -> bool:
        """Verify event signature.

        Args:
            timestamp: Request timestamp
            nonce: Random nonce
            encrypt: Encrypted event body
            signature: Signature to verify

        Returns:
            True if signature is valid
        """
        if not self.encrypt_key:
            return True  # Skip verification if no key configured

        # Concatenate timestamp + nonce + encrypt_key + encrypt
        content = f"{timestamp}{nonce}{self.encrypt_key}{encrypt}"
        computed_signature = hashlib.sha256(content.encode()).hexdigest()

        return hmac.compare_digest(computed_signature, signature)

    def handle_url_verification(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle URL verification challenge.

        Args:
            data: Challenge data with token and challenge

        Returns:
            Challenge response

        Raises:
            ValueError: If verification token doesn't match
        """
        token = data.get("token")
        challenge = data.get("challenge")

        if self.verification_token and token != self.verification_token:
            raise ValueError("Invalid verification token")

        return {"challenge": challenge}

    def handle_event(self, event_data: Dict[str, Any]) -> Optional[Any]:
        """Route and handle event.

        Args:
            event_data: Event data from webhook

        Returns:
            Handler result or None
        """
        event_type = event_data.get("type")

        # Handle URL verification
        if event_type == FeishuEventType.URL_VERIFICATION:
            return self.handle_url_verification(event_data)

        # Get event header and body
        header = event_data.get("header", {})
        event_type = header.get("event_type")

        # Find and call handler
        handler = self.event_handlers.get(event_type)
        if handler:
            event = event_data.get("event", {})
            return handler(event)

        return None

    def process_webhook(
        self, body: Dict[str, Any], headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Process incoming webhook request.

        Args:
            body: Request body (JSON)
            headers: Request headers (optional, for signature verification)

        Returns:
            Response data

        Raises:
            ValueError: If signature verification fails
        """
        # Verify signature if headers provided
        if headers and self.encrypt_key:
            timestamp = headers.get("X-Lark-Request-Timestamp", "")
            nonce = headers.get("X-Lark-Request-Nonce", "")
            signature = headers.get("X-Lark-Signature", "")
            encrypt = json.dumps(body, separators=(",", ":"))

            if not self.verify_signature(timestamp, nonce, encrypt, signature):
                raise ValueError("Invalid signature")

        # Handle event
        result = self.handle_event(body)

        # Return result or empty success response
        if result:
            return dict(result) if result else {"code": 0, "msg": "success"}
        return {"code": 0, "msg": "success"}
