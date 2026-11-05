from abc import ABC, abstractmethod
from typing import List
from src.models import RawPromotion

class BaseScraper(ABC):
    @abstractmethod
    def fetch_promotions(self) -> List[RawPromotion]:
        """Busca promoções brutas da fonte de dados."""
        pass
