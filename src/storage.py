import os
import json
import logging
from typing import Set, Iterable

logger = logging.getLogger(__name__)


class Storage:
    def __init__(self, file_path: str = "data/seen_posts.json"):
        self.file_path = file_path

    def load_seen_ids(self) -> Set[str]:
        if not os.path.exists(self.file_path):
            return set()
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return set(data)
                elif isinstance(data, dict):
                    return set(data.keys())
        except Exception as e:
            logger.error("Erro ao carregar %s: %s", self.file_path, e)
        return set()

    def save_seen_id(self, promo_id: str) -> None:
        self.save_seen_ids([promo_id])

    def save_seen_ids(self, promo_ids: Iterable[str]) -> None:
        seen = self.load_seen_ids()
        seen.update(promo_ids)

        parent = os.path.dirname(self.file_path)
        if parent:
            os.makedirs(parent, exist_ok=True)

        try:
            # Salva ordenado para que os diffs no git fiquem limpos
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(sorted(list(seen)), f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error("Erro ao salvar %s: %s", self.file_path, e)
