import os
import pytest
from src.config import load_config, AppConfig

def test_load_config_default(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("""
banks:
  - sicredi
  - livelo
min_bonus_percentage: 50
feeds:
  - name: "Feed Test"
    url: "https://example.com/feed"
direct_scrapers:
  smiles: true
  azul: false
""", encoding="utf-8")

    os.environ["TELEGRAM_BOT_TOKEN"] = "fake-token"
    os.environ["TELEGRAM_CHAT_ID"] = "12345678"

    cfg = load_config(str(config_file))
    assert isinstance(cfg, AppConfig)
    assert cfg.banks == ["sicredi", "livelo"]
    assert cfg.min_bonus_percentage == 50
    assert len(cfg.feeds) == 1
    assert cfg.feeds[0]["name"] == "Feed Test"
    assert cfg.direct_scrapers.get("smiles") is True
    assert cfg.direct_scrapers.get("azul") is False
    assert cfg.telegram_bot_token == "fake-token"
    assert cfg.telegram_chat_id == "12345678"

def test_load_config_default_banks_all(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("""
banks:
  - all
min_bonus_percentage: 0
feeds: []
""", encoding="utf-8")

    cfg = load_config(str(config_file))
    assert cfg.banks == ["all"]
    assert cfg.should_monitor_bank("sicredi") is True
    assert cfg.should_monitor_bank("itau") is True
