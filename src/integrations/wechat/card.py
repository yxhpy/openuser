"""
WeChat Work Card Builder

Builds interactive cards (textcard and news messages) for WeChat Work.
"""

import json
from typing import List, Dict, Any, Optional
from enum import Enum


class CardType(Enum):
    """WeChat Work card types."""

    TEXTCARD = "textcard"
    NEWS = "news"


class WeChatCardBuilder:
    """Builder for WeChat Work interactive cards."""

    def __init__(self, card_type: CardType = CardType.TEXTCARD):
        """
        Initialize card builder.

        Args:
            card_type: Type of card to build
        """
        self.card_type = card_type
        self._title: Optional[str] = None
        self._description: Optional[str] = None
        self._url: Optional[str] = None
        self._btntxt: Optional[str] = None
        self._articles: List[Dict[str, str]] = []

    def set_title(self, title: str) -> "WeChatCardBuilder":
        """
        Set card title.

        Args:
            title: Card title

        Returns:
            Self for chaining
        """
        self._title = title
        return self

    def set_description(self, description: str) -> "WeChatCardBuilder":
        """
        Set card description.

        Args:
            description: Card description

        Returns:
            Self for chaining
        """
        self._description = description
        return self

    def set_url(self, url: str) -> "WeChatCardBuilder":
        """
        Set card URL.

        Args:
            url: Card URL

        Returns:
            Self for chaining
        """
        self._url = url
        return self

    def set_button_text(self, text: str) -> "WeChatCardBuilder":
        """
        Set button text (for textcard).

        Args:
            text: Button text

        Returns:
            Self for chaining
        """
        self._btntxt = text
        return self

    def add_article(
        self,
        title: str,
        description: str = "",
        url: str = "",
        picurl: str = "",
    ) -> "WeChatCardBuilder":
        """
        Add article to news card.

        Args:
            title: Article title
            description: Article description
            url: Article URL
            picurl: Article picture URL

        Returns:
            Self for chaining
        """
        article = {
            "title": title,
            "description": description,
            "url": url,
            "picurl": picurl,
        }
        self._articles.append(article)
        return self

    def build(self) -> Dict[str, Any]:
        """
        Build card content.

        Returns:
            Card content dict

        Raises:
            ValueError: If required fields are missing
        """
        if self.card_type == CardType.TEXTCARD:
            if not self._title or not self._description:
                raise ValueError("Title and description are required for textcard")

            card = {
                "title": self._title,
                "description": self._description,
                "url": self._url or "",
            }

            if self._btntxt:
                card["btntxt"] = self._btntxt

            return card

        elif self.card_type == CardType.NEWS:
            if not self._articles:
                raise ValueError("At least one article is required for news card")

            return {"articles": self._articles}

        raise ValueError(f"Unknown card type: {self.card_type}")

    def build_message(
        self,
        touser: Optional[str] = None,
        toparty: Optional[str] = None,
        totag: Optional[str] = None,
        agent_id: str = "",
    ) -> Dict[str, Any]:
        """
        Build complete message payload.

        Args:
            touser: User IDs separated by '|'
            toparty: Department IDs separated by '|'
            totag: Tag IDs separated by '|'
            agent_id: Application agent ID

        Returns:
            Complete message payload dict
        """
        content = self.build()

        message = {
            "touser": touser or "@all",
            "toparty": toparty or "",
            "totag": totag or "",
            "msgtype": self.card_type.value,
            "agentid": agent_id,
            self.card_type.value: content,
        }

        return message
