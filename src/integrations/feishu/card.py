"""Feishu interactive card builder.

This module provides:
- Card template builder
- Button actions
- Form elements
- Card update mechanism
"""

import json
from enum import Enum
from typing import Any, Dict, List, Optional


class CardElementType(str, Enum):
    """Card element types."""

    DIV = "div"
    HR = "hr"
    IMG = "img"
    ACTION = "action"
    NOTE = "note"
    MARKDOWN = "markdown"


class ButtonType(str, Enum):
    """Button types."""

    DEFAULT = "default"
    PRIMARY = "primary"
    DANGER = "danger"


class FeishuCardBuilder:
    """Builder for Feishu interactive cards.

    Provides fluent API for building rich interactive cards.
    """

    def __init__(self) -> None:
        """Initialize card builder."""
        self.config = {"wide_screen_mode": True}
        self.header: Optional[Dict[str, Any]] = None
        self.elements: List[Dict[str, Any]] = []

    def set_header(self, title: str, template: str = "blue") -> "FeishuCardBuilder":
        """Set card header.

        Args:
            title: Header title
            template: Color template (blue, wathet, turquoise, green, yellow,
                orange, red, carmine, violet, purple, indigo, grey)

        Returns:
            Self for chaining
        """
        self.header = {"title": {"tag": "plain_text", "content": title}, "template": template}
        return self

    def add_markdown(self, content: str) -> "FeishuCardBuilder":
        """Add markdown text element.

        Args:
            content: Markdown content

        Returns:
            Self for chaining
        """
        self.elements.append({"tag": "markdown", "content": content})
        return self

    def add_divider(self) -> "FeishuCardBuilder":
        """Add horizontal divider.

        Returns:
            Self for chaining
        """
        self.elements.append({"tag": "hr"})
        return self

    def add_image(
        self, img_key: str, alt: Optional[str] = None, title: Optional[str] = None
    ) -> "FeishuCardBuilder":
        """Add image element.

        Args:
            img_key: Image key from Feishu
            alt: Alt text
            title: Image title

        Returns:
            Self for chaining
        """
        element: Dict[str, Any] = {"tag": "img", "img_key": img_key}
        if alt:
            element["alt"] = {"tag": "plain_text", "content": alt}
        if title:
            element["title"] = {"tag": "plain_text", "content": title}

        self.elements.append(element)
        return self

    def add_button(
        self,
        text: str,
        value: Dict[str, Any],
        button_type: str = ButtonType.DEFAULT,
        url: Optional[str] = None,
    ) -> "FeishuCardBuilder":
        """Add button element.

        Args:
            text: Button text
            value: Button value (passed to callback)
            button_type: Button style (default, primary, danger)
            url: Optional URL to open

        Returns:
            Self for chaining
        """
        button = {
            "tag": "button",
            "text": {"tag": "plain_text", "content": text},
            "type": button_type,
            "value": value,
        }

        if url:
            button["url"] = url

        # Wrap in action element
        self.elements.append({"tag": "action", "actions": [button]})
        return self

    def add_buttons(self, buttons: List[Dict[str, Any]]) -> "FeishuCardBuilder":
        """Add multiple buttons in a row.

        Args:
            buttons: List of button configs with text, value, type, url

        Returns:
            Self for chaining
        """
        actions = []
        for btn in buttons:
            button = {
                "tag": "button",
                "text": {"tag": "plain_text", "content": btn["text"]},
                "type": btn.get("type", ButtonType.DEFAULT),
                "value": btn["value"],
            }
            if "url" in btn:
                button["url"] = btn["url"]
            actions.append(button)

        self.elements.append({"tag": "action", "actions": actions})
        return self

    def add_note(self, content: str) -> "FeishuCardBuilder":
        """Add note element (small gray text).

        Args:
            content: Note content

        Returns:
            Self for chaining
        """
        self.elements.append(
            {"tag": "note", "elements": [{"tag": "plain_text", "content": content}]}
        )
        return self

    def add_field(self, fields: List[Dict[str, str]], is_short: bool = True) -> "FeishuCardBuilder":
        """Add field element (key-value pairs).

        Args:
            fields: List of dicts with 'name' and 'value'
            is_short: Whether to display in two columns

        Returns:
            Self for chaining
        """
        field_elements = []
        for field in fields:
            field_elements.append(
                {
                    "is_short": is_short,
                    "text": {"tag": "lark_md", "content": f"**{field['name']}**\n{field['value']}"},
                }
            )

        self.elements.append({"tag": "div", "fields": field_elements})
        return self

    def build(self) -> str:
        """Build card JSON string.

        Returns:
            JSON string of card content
        """
        card = {"config": self.config, "elements": self.elements}

        if self.header:
            card["header"] = self.header

        return json.dumps(card, ensure_ascii=False)

    def to_message_content(self) -> str:
        """Build card as message content.

        Returns:
            JSON string suitable for send_message API
        """
        return self.build()
