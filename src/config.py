import os
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

try:
    import yaml
except ImportError:
    try:
        from ruamel.yaml import YAML
        _ruamel = YAML(typ='safe')
        class yaml:  # type: ignore
            @staticmethod
            def safe_load(stream):
                return _ruamel.load(stream)
    except ImportError:
        yaml = None  # type: ignore


@dataclass
class AppConfig:
    banks: List[str] = field(default_factory=lambda: ["all"])
    min_bonus_percentage: int = 0
    feeds: List[Dict[str, Any]] = field(default_factory=list)
    direct_scrapers: Dict[str, bool] = field(default_factory=dict)
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None

    def should_monitor_bank(self, bank_name: str) -> bool:
        if not bank_name:
            return False
        banks_lower = [b.strip().lower() for b in self.banks]
        if "all" in banks_lower or "*" in banks_lower:
            return True
        return bank_name.strip().lower() in banks_lower


def load_config(config_path: str = "config.yaml") -> AppConfig:
    data: Dict[str, Any] = {}
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            if yaml is not None:
                loaded = yaml.safe_load(f)
                if isinstance(loaded, dict):
                    data = loaded

    banks = data.get("banks", ["all"])
    min_bonus = int(data.get("min_bonus_percentage", 0))
    feeds = data.get("feeds", [])
    direct_scrapers = data.get("direct_scrapers", {})

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    return AppConfig(
        banks=banks,
        min_bonus_percentage=min_bonus,
        feeds=feeds,
        direct_scrapers=direct_scrapers,
        telegram_bot_token=token,
        telegram_chat_id=chat_id,
    )
