import pytest
from unittest.mock import patch, MagicMock
from src.main import run_pipeline

def test_run_pipeline_dry_run(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("""
banks:
  - all
min_bonus_percentage: 0
feeds:
  - name: "test"
    url: "https://test.com/rss"
direct_scrapers:
  smiles: false
  azul: false
""", encoding="utf-8")

    storage_file = tmp_path / "seen_posts.json"

    with patch("src.main.RssScraper") as mock_rss:
        mock_instance = MagicMock()
        mock_raw = MagicMock()
        mock_raw.title = "Sicredi e Smiles com 70% de bônus na transferência"
        mock_raw.link = "https://test.com/sicredi"
        mock_raw.summary = "Transfira pontos"
        mock_raw.published_at = "2026-11-05"
        mock_raw.source = "test"
        mock_raw.canonical_id = "test-id-123"

        mock_instance.fetch_promotions.return_value = [mock_raw]
        mock_rss.return_value = mock_instance

        sent_count = run_pipeline(
            config_path=str(config_file),
            storage_path=str(storage_file),
            dry_run=True
        )

        assert sent_count == 1
        # In dry run, it shouldn't modify storage file
        assert not storage_file.exists()
