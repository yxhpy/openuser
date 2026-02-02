"""Tests for Feishu interactive card builder."""

import pytest
import json

from src.integrations.feishu.card import (
    FeishuCardBuilder,
    CardElementType,
    ButtonType
)


class TestFeishuCardBuilder:
    """Test cases for FeishuCardBuilder."""

    def test_init(self):
        """Test initialization."""
        builder = FeishuCardBuilder()

        assert builder.config == {"wide_screen_mode": True}
        assert builder.header is None
        assert builder.elements == []

    def test_set_header(self):
        """Test setting card header."""
        builder = FeishuCardBuilder()
        builder.set_header("Test Title", "blue")

        assert builder.header is not None
        assert builder.header["title"]["content"] == "Test Title"
        assert builder.header["template"] == "blue"

    def test_set_header_chaining(self):
        """Test header setting returns self for chaining."""
        builder = FeishuCardBuilder()
        result = builder.set_header("Test")

        assert result is builder

    def test_add_markdown(self):
        """Test adding markdown element."""
        builder = FeishuCardBuilder()
        builder.add_markdown("**Bold** text")

        assert len(builder.elements) == 1
        assert builder.elements[0]["tag"] == "markdown"
        assert builder.elements[0]["content"] == "**Bold** text"

    def test_add_divider(self):
        """Test adding divider element."""
        builder = FeishuCardBuilder()
        builder.add_divider()

        assert len(builder.elements) == 1
        assert builder.elements[0]["tag"] == "hr"

    def test_add_image(self):
        """Test adding image element."""
        builder = FeishuCardBuilder()
        builder.add_image("img_123", alt="Alt text", title="Image Title")

        assert len(builder.elements) == 1
        element = builder.elements[0]
        assert element["tag"] == "img"
        assert element["img_key"] == "img_123"
        assert element["alt"]["content"] == "Alt text"
        assert element["title"]["content"] == "Image Title"

    def test_add_image_minimal(self):
        """Test adding image with minimal parameters."""
        builder = FeishuCardBuilder()
        builder.add_image("img_123")

        element = builder.elements[0]
        assert element["img_key"] == "img_123"
        assert "alt" not in element
        assert "title" not in element

    def test_add_button(self):
        """Test adding single button."""
        builder = FeishuCardBuilder()
        builder.add_button(
            text="Click Me",
            value={"action": "test"},
            button_type=ButtonType.PRIMARY
        )

        assert len(builder.elements) == 1
        action = builder.elements[0]
        assert action["tag"] == "action"
        assert len(action["actions"]) == 1

        button = action["actions"][0]
        assert button["text"]["content"] == "Click Me"
        assert button["value"] == {"action": "test"}
        assert button["type"] == ButtonType.PRIMARY

    def test_add_button_with_url(self):
        """Test adding button with URL."""
        builder = FeishuCardBuilder()
        builder.add_button(
            text="Open Link",
            value={},
            url="https://example.com"
        )

        button = builder.elements[0]["actions"][0]
        assert button["url"] == "https://example.com"

    def test_add_buttons(self):
        """Test adding multiple buttons."""
        builder = FeishuCardBuilder()
        buttons = [
            {"text": "Button 1", "value": {"id": 1}, "type": ButtonType.PRIMARY},
            {"text": "Button 2", "value": {"id": 2}, "type": ButtonType.DANGER}
        ]
        builder.add_buttons(buttons)

        assert len(builder.elements) == 1
        actions = builder.elements[0]["actions"]
        assert len(actions) == 2
        assert actions[0]["text"]["content"] == "Button 1"
        assert actions[1]["text"]["content"] == "Button 2"

    def test_add_buttons_with_url(self):
        """Test adding buttons with URLs."""
        builder = FeishuCardBuilder()
        buttons = [
            {"text": "Link 1", "value": {}, "url": "https://example1.com"},
            {"text": "Link 2", "value": {}, "url": "https://example2.com"}
        ]
        builder.add_buttons(buttons)

        actions = builder.elements[0]["actions"]
        assert actions[0]["url"] == "https://example1.com"
        assert actions[1]["url"] == "https://example2.com"

    def test_add_note(self):
        """Test adding note element."""
        builder = FeishuCardBuilder()
        builder.add_note("This is a note")

        assert len(builder.elements) == 1
        note = builder.elements[0]
        assert note["tag"] == "note"
        assert note["elements"][0]["content"] == "This is a note"

    def test_add_field(self):
        """Test adding field element."""
        builder = FeishuCardBuilder()
        fields = [
            {"name": "Field 1", "value": "Value 1"},
            {"name": "Field 2", "value": "Value 2"}
        ]
        builder.add_field(fields, is_short=True)

        assert len(builder.elements) == 1
        div = builder.elements[0]
        assert div["tag"] == "div"
        assert len(div["fields"]) == 2
        assert div["fields"][0]["is_short"] is True

    def test_build(self):
        """Test building card JSON."""
        builder = FeishuCardBuilder()
        builder.set_header("Test Card", "blue")
        builder.add_markdown("Content")
        builder.add_divider()

        card_json = builder.build()
        card = json.loads(card_json)

        assert "config" in card
        assert "header" in card
        assert "elements" in card
        assert len(card["elements"]) == 2

    def test_build_without_header(self):
        """Test building card without header."""
        builder = FeishuCardBuilder()
        builder.add_markdown("Content")

        card_json = builder.build()
        card = json.loads(card_json)

        assert "header" not in card
        assert len(card["elements"]) == 1

    def test_to_message_content(self):
        """Test converting to message content."""
        builder = FeishuCardBuilder()
        builder.add_markdown("Test")

        content = builder.to_message_content()

        # Should be same as build()
        assert content == builder.build()

    def test_chaining(self):
        """Test method chaining."""
        builder = FeishuCardBuilder()
        result = (builder
                  .set_header("Title")
                  .add_markdown("Content")
                  .add_divider()
                  .add_button("Click", {"action": "test"}))

        assert result is builder
        assert len(builder.elements) == 3

    def test_complex_card(self):
        """Test building complex card with multiple elements."""
        builder = FeishuCardBuilder()
        (builder
         .set_header("Complex Card", "green")
         .add_markdown("**Introduction**")
         .add_divider()
         .add_image("img_123", alt="Image")
         .add_field([
             {"name": "Status", "value": "Active"},
             {"name": "Count", "value": "42"}
         ])
         .add_buttons([
             {"text": "Approve", "value": {"action": "approve"}, "type": ButtonType.PRIMARY},
             {"text": "Reject", "value": {"action": "reject"}, "type": ButtonType.DANGER}
         ])
         .add_note("Last updated: 2024-01-01"))

        card_json = builder.build()
        card = json.loads(card_json)

        assert card["header"]["title"]["content"] == "Complex Card"
        assert len(card["elements"]) == 6

