import logging
import requests
from bs4 import BeautifulSoup
from typing import List
from urllib.parse import urljoin
from src.models import RawPromotion
from src.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}

AZUL_PROMOS_URL = "https://www.voeazul.com.br/br/pt/programa-de-fidelidade/promocoes"


class DirectAzulScraper(BaseScraper):
    def fetch_promotions(self) -> List[RawPromotion]:
        promotions: List[RawPromotion] = []

        try:
            logger.info("Consultando promoções diretamente em Azul: %s", AZUL_PROMOS_URL)
            resp = requests.get(AZUL_PROMOS_URL, headers=HEADERS, timeout=15)
            if resp.status_code != 200:
                logger.warning("Azul retornou status code %s. Pulando scraper direto.", resp.status_code)
                return []

            soup = BeautifulSoup(resp.text, "html.parser")
            cards = soup.find_all(["div", "article", "a"], class_=lambda c: c and any(w in str(c).lower() for w in ["promo", "card", "banner", "offer"]))

            for card in cards:
                title_elem = card.find(["h2", "h3", "h4", "p", "strong"])
                link_elem = card if card.name == "a" else card.find("a")

                if not title_elem or not link_elem:
                    continue

                title = title_elem.get_text(strip=True)
                href = link_elem.get("href", "")
                if not href or not title:
                    continue

                full_url = urljoin(AZUL_PROMOS_URL, href)
                summary_elem = card.find("p")
                summary = summary_elem.get_text(strip=True) if summary_elem else title

                promotions.append(
                    RawPromotion(
                        title=title,
                        link=full_url,
                        summary=summary,
                        source="direct:azul"
                    )
                )
        except Exception as e:
            logger.warning("Falha ao consultar site direto da Azul: %s", e)

        return promotions
