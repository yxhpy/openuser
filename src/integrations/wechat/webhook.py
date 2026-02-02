"""
WeChat Work Webhook Handler

Handles incoming webhook events from WeChat Work, including:
- Signature verification
- URL verification
- Event routing and processing
"""

import hashlib
import xml.etree.ElementTree as ET
from typing import Dict, Callable, Optional, Any
from Crypto.Cipher import AES
import base64
import struct
import socket


class WeChatWebhookHandler:
    """WeChat Work webhook event handler with signature verification."""

    def __init__(self, token: str, encoding_aes_key: str, corp_id: str):
        """
        Initialize webhook handler.

        Args:
            token: Webhook verification token
            encoding_aes_key: Message encryption key (43 characters)
            corp_id: WeChat Work corporation ID
        """
        self.token = token
        self.encoding_aes_key = encoding_aes_key
        self.corp_id = corp_id
        self._handlers: Dict[str, Callable] = {}

        # Decode AES key
        self.aes_key = base64.b64decode(encoding_aes_key + "=")

    def register_handler(self, event_type: str, handler: Callable) -> None:
        """
        Register event handler.

        Args:
            event_type: Event type (e.g., "text", "image", "event")
            handler: Handler function
        """
        self._handlers[event_type] = handler

    def verify_signature(
        self, msg_signature: str, timestamp: str, nonce: str, echostr: str
    ) -> bool:
        """
        Verify webhook signature for URL verification.

        Args:
            msg_signature: Message signature from WeChat
            timestamp: Timestamp from WeChat
            nonce: Random nonce from WeChat
            echostr: Echo string from WeChat

        Returns:
            True if signature is valid
        """
        # Sort parameters
        params = sorted([self.token, timestamp, nonce, echostr])
        # Calculate SHA1
        sha1 = hashlib.sha1()
        sha1.update("".join(params).encode("utf-8"))
        signature = sha1.hexdigest()

        return signature == msg_signature

    def decrypt_message(self, encrypt_msg: str) -> str:
        """
        Decrypt encrypted message from WeChat.

        Args:
            encrypt_msg: Base64 encoded encrypted message

        Returns:
            Decrypted message XML string

        Raises:
            Exception: If decryption fails
        """
        # Decode base64
        cipher_text = base64.b64decode(encrypt_msg)

        # Create AES cipher
        cipher = AES.new(self.aes_key, AES.MODE_CBC, self.aes_key[:16])

        # Decrypt
        plain_text = cipher.decrypt(cipher_text)

        # Remove padding
        pad = plain_text[-1]
        if isinstance(pad, str):
            pad = ord(pad)
        plain_text = plain_text[:-pad]

        # Extract message
        # Format: random(16) + msg_len(4) + msg + corp_id
        content = plain_text[16:]
        msg_len = struct.unpack("!I", content[:4])[0]
        msg_content = content[4 : 4 + msg_len].decode("utf-8")

        return msg_content

    def encrypt_message(self, msg: str, nonce: str, timestamp: str) -> Dict[str, str]:
        """
        Encrypt message for WeChat response.

        Args:
            msg: Message XML string
            nonce: Random nonce
            timestamp: Timestamp

        Returns:
            Dict with encrypted message and signature
        """
        # Add random bytes, message length, message, and corp_id
        msg_bytes = msg.encode("utf-8")
        msg_len = struct.pack("!I", len(msg_bytes))
        corp_id_bytes = self.corp_id.encode("utf-8")

        # Generate random bytes
        import os

        random_bytes = os.urandom(16)

        # Combine
        plain_text = random_bytes + msg_len + msg_bytes + corp_id_bytes

        # Add PKCS7 padding
        block_size = 32
        padding_len = block_size - (len(plain_text) % block_size)
        padding = bytes([padding_len] * padding_len)
        plain_text += padding

        # Encrypt
        cipher = AES.new(self.aes_key, AES.MODE_CBC, self.aes_key[:16])
        cipher_text = cipher.encrypt(plain_text)

        # Encode base64
        encrypt_msg = base64.b64encode(cipher_text).decode("utf-8")

        # Calculate signature
        params = sorted([self.token, timestamp, nonce, encrypt_msg])
        sha1 = hashlib.sha1()
        sha1.update("".join(params).encode("utf-8"))
        signature = sha1.hexdigest()

        return {
            "encrypt": encrypt_msg,
            "msg_signature": signature,
            "timestamp": timestamp,
            "nonce": nonce,
        }

    def parse_xml(self, xml_str: str) -> Dict[str, Any]:
        """
        Parse XML message to dict.

        Args:
            xml_str: XML string

        Returns:
            Parsed message dict
        """
        root = ET.fromstring(xml_str)
        result = {}

        for child in root:
            result[child.tag] = child.text

        return result

    def process_webhook(
        self,
        msg_signature: str,
        timestamp: str,
        nonce: str,
        body: str,
        echostr: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process incoming webhook request.

        Args:
            msg_signature: Message signature
            timestamp: Timestamp
            nonce: Random nonce
            body: Request body (XML or empty for URL verification)
            echostr: Echo string for URL verification

        Returns:
            Response dict

        Raises:
            Exception: If signature verification fails
        """
        # URL verification
        if echostr:
            if not self.verify_signature(msg_signature, timestamp, nonce, echostr):
                raise Exception("Invalid signature for URL verification")

            # Decrypt echostr
            decrypted = self.decrypt_message(echostr)
            return {"echostr": decrypted}

        # Parse encrypted message
        msg_dict = self.parse_xml(body)
        encrypt_msg = msg_dict.get("Encrypt", "")

        # Verify signature
        params = sorted([self.token, timestamp, nonce, encrypt_msg])
        sha1 = hashlib.sha1()
        sha1.update("".join(params).encode("utf-8"))
        signature = sha1.hexdigest()

        if signature != msg_signature:
            raise Exception("Invalid message signature")

        # Decrypt message
        decrypted_xml = self.decrypt_message(encrypt_msg)
        event_data = self.parse_xml(decrypted_xml)

        # Route to handler
        msg_type = event_data.get("MsgType", "")
        handler = self._handlers.get(msg_type)

        if handler:
            response = handler(event_data)
            if response:
                # Encrypt response
                response_xml = self._build_response_xml(event_data, response)
                return self.encrypt_message(response_xml, nonce, timestamp)

        return {"status": "ok"}

    def _build_response_xml(
        self, event_data: Dict[str, Any], response: Dict[str, Any]
    ) -> str:
        """
        Build response XML.

        Args:
            event_data: Original event data
            response: Response data

        Returns:
            XML string
        """
        root = ET.Element("xml")

        # Add ToUserName
        to_user = ET.SubElement(root, "ToUserName")
        to_user.text = f"<![CDATA[{event_data.get('FromUserName', '')}]]>"

        # Add FromUserName
        from_user = ET.SubElement(root, "FromUserName")
        from_user.text = f"<![CDATA[{event_data.get('ToUserName', '')}]]>"

        # Add CreateTime
        create_time = ET.SubElement(root, "CreateTime")
        import time

        create_time.text = str(int(time.time()))

        # Add MsgType
        msg_type = ET.SubElement(root, "MsgType")
        msg_type.text = f"<![CDATA[{response.get('msg_type', 'text')}]]>"

        # Add Content
        if response.get("content"):
            content = ET.SubElement(root, "Content")
            content.text = f"<![CDATA[{response['content']}]]>"

        return ET.tostring(root, encoding="unicode")
