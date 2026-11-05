from dataclasses import dataclass
from typing import Optional
import hashlib

@dataclass
class RawPromotion:
    title: str
    link: str
    summary: str
    published_at: Optional[str] = None
    source: str = "rss"

    @property
    def canonical_id(self) -> str:
        # Generate stable ID based on link or title
        cleaned_link = self.link.strip().lower() if self.link else ""
        if cleaned_link:
            return hashlib.sha256(cleaned_link.encode("utf-8")).hexdigest()[:16]
        return hashlib.sha256(self.title.strip().lower().encode("utf-8")).hexdigest()[:16]


@dataclass
class Promotion:
    id: str
    title: str
    link: str
    summary: str
    source_bank: str
    target_program: str
    bonus_percentage: Optional[int] = None
    published_at: Optional[str] = None
    source: str = "rss"
