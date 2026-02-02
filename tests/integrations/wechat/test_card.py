"""
Tests for WeChat Work Card Builder
"""

import pytest
from src.integrations.wechat.card import WeChatCardBuilder, CardType


class TestWeChatCardBuilder:
    """Test WeChatCardBuilder class."""

    def test_init_default(self):
        """Test default initialization."""
        builder = WeChatCardBuilder()
        assert builder.card_type == CardType.TEXTCARD

    def test_init_custom_type(self):
        """Test initialization with custom type."""
        builder = WeChatCardBuilder(card_type=CardType.NEWS)
        assert builder.card_type == CardType.NEWS

    def test_set_title(self):
        """Test setting title."""
        builder = WeChatCardBuilder()
        result = builder.set_title("Test Title")

        assert result is builder  # Check chaining
        assert builder._title == "Test Title"

    def test_set_description(self):
        """Test setting description."""
        builder = WeChatCardBuilder()
        result = builder.set_description("Test Description")

        assert result is builder
        assert builder._description == "Test Description"

    def test_set_url(self):
        """Test setting URL."""
        builder = WeChatCardBuilder()
        result = builder.set_url("https://example.com")

        assert result is builder
        assert builder._url == "https://example.com"

    def test_set_button_text(self):
        """Test setting button text."""
        builder = WeChatCardBuilder()
        result = builder.set_button_text("Click Me")

        assert result is builder
        assert builder._btntxt == "Click Me"

    def test_add_article(self):
        """Test adding article."""
        builder = WeChatCardBuilder(card_type=CardType.NEWS)
        result = builder.add_article(
            title="Article Title",
            description="Article Description",
            url="https://example.com/article",
            picurl="https://example.com/pic.jpg",
        )

        assert result is builder
        assert len(builder._articles) == 1
        assert builder._articles[0]["title"] == "Article Title"
        assert builder._articles[0]["description"] == "Article Description"
        assert builder._articles[0]["url"] == "https://example.com/article"
        assert builder._articles[0]["picurl"] == "https://example.com/pic.jpg"

    def test_add_multiple_articles(self):
        """Test adding multiple articles."""
        builder = WeChatCardBuilder(card_type=CardType.NEWS)
        builder.add_article(title="Article 1")
        builder.add_article(title="Article 2")
        builder.add_article(title="Article 3")

        assert len(builder._articles) == 3

    def test_build_textcard_success(self):
        """Test building textcard successfully."""
        builder = WeChatCardBuilder()
        card = (
            builder.set_title("Card Title")
            .set_description("Card Description")
            .set_url("https://example.com")
            .set_button_text("View Details")
            .build()
        )

        assert card["title"] == "Card Title"
        assert card["description"] == "Card Description"
        assert card["url"] == "https://example.com"
        assert card["btntxt"] == "View Details"

    def test_build_textcard_without_button(self):
        """Test building textcard without button text."""
        builder = WeChatCardBuilder()
        card = (
            builder.set_title("Card Title")
            .set_description("Card Description")
            .set_url("https://example.com")
            .build()
        )

        assert "btntxt" not in card
        assert card["url"] == "https://example.com"

    def test_build_textcard_without_url(self):
        """Test building textcard without URL."""
        builder = WeChatCardBuilder()
        card = builder.set_title("Card Title").set_description("Card Description").build()

        assert card["url"] == ""

    def test_build_textcard_missing_title(self):
        """Test building textcard without title."""
        builder = WeChatCardBuilder()
        builder.set_description("Description only")

        with pytest.raises(ValueError) as exc_info:
            builder.build()

        assert "Title and description are required" in str(exc_info.value)

    def test_build_textcard_missing_description(self):
        """Test building textcard without description."""
        builder = WeChatCardBuilder()
        builder.set_title("Title only")

        with pytest.raises(ValueError) as exc_info:
            builder.build()

        assert "Title and description are required" in str(exc_info.value)

    def test_build_news_success(self):
        """Test building news card successfully."""
        builder = WeChatCardBuilder(card_type=CardType.NEWS)
        card = (
            builder.add_article(
                title="Article 1",
                description="Description 1",
                url="https://example.com/1",
                picurl="https://example.com/pic1.jpg",
            )
            .add_article(
                title="Article 2",
                description="Description 2",
                url="https://example.com/2",
            )
            .build()
        )

        assert "articles" in card
        assert len(card["articles"]) == 2
        assert card["articles"][0]["title"] == "Article 1"
        assert card["articles"][1]["title"] == "Article 2"

    def test_build_news_missing_articles(self):
        """Test building news card without articles."""
        builder = WeChatCardBuilder(card_type=CardType.NEWS)

        with pytest.raises(ValueError) as exc_info:
            builder.build()

        assert "At least one article is required" in str(exc_info.value)

    def test_build_message_textcard(self):
        """Test building complete textcard message."""
        builder = WeChatCardBuilder()
        message = (
            builder.set_title("Title")
            .set_description("Description")
            .build_message(touser="user1|user2", agent_id="1000001")
        )

        assert message["touser"] == "user1|user2"
        assert message["msgtype"] == "textcard"
        assert message["agentid"] == "1000001"
        assert "textcard" in message
        assert message["textcard"]["title"] == "Title"

    def test_build_message_news(self):
        """Test building complete news message."""
        builder = WeChatCardBuilder(card_type=CardType.NEWS)
        message = (
            builder.add_article(title="Article")
            .build_message(toparty="dept1|dept2", agent_id="1000001")
        )

        assert message["toparty"] == "dept1|dept2"
        assert message["msgtype"] == "news"
        assert message["agentid"] == "1000001"
        assert "news" in message

    def test_build_message_default_touser(self):
        """Test building message with default touser."""
        builder = WeChatCardBuilder()
        message = (
            builder.set_title("Title")
            .set_description("Description")
            .build_message(agent_id="1000001")
        )

        assert message["touser"] == "@all"

    def test_method_chaining(self):
        """Test method chaining."""
        builder = WeChatCardBuilder()
        result = (
            builder.set_title("Title")
            .set_description("Description")
            .set_url("https://example.com")
            .set_button_text("Click")
        )

        assert result is builder
        assert builder._title == "Title"
        assert builder._description == "Description"
        assert builder._url == "https://example.com"
        assert builder._btntxt == "Click"
