import logging
from typing import List, Dict, Any
import feedparser
from src.models import RawPromotion
from src.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"


class RssScraper(BaseScraper):
    def __init__(self, feeds: List[Dict[str, Any]]):
        self.feeds = feeds

    def fetch_promotions(self) -> List[RawPromotion]:
        promotions: List[RawPromotion] = []

        for feed_info in self.feeds:
            name = feed_info.get("name", "Desconhecido")
            url = feed_info.get("url")
            if not url:
                continue

            try:
                logger.info("Consultando feed RSS: %s (%s)", name, url)
                parsed = feedparser.parse(url, agent=USER_AGENT)

                if getattr(parsed, "bozo", 0) == 1 and not parsed.entries:
                    logger.warning("Possível erro ao interpretar feed %s: %s", name, getattr(parsed, "bozo_exception", "Desconhecido"))
                    continue

                for entry in parsed.entries:
                    title = getattr(entry, "title", "").strip()
                    link = getattr(entry, "link", "").strip()
                    summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
                    published = getattr(entry, "published", None) or getattr(entry, "updated", None)

                    if title and link:
                        promotions.append(
                            RawPromotion(
                                title=title,
                                link=link,
                                summary=summary.strip(),
                                published_at=published,
                                source=f"rss:{name}"
                            )
                        )
            except Exception as e:
                logger.error("Erro ao obter feed %s (%s): %s", name, url, e)

        return promotions
