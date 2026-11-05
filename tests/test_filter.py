import os
import json
import pytest
from src.models import Promotion
from src.config import AppConfig
from src.storage import Storage
from src.filter import PromotionFilter

@pytest.fixture
def sample_promotions():
    return [
        Promotion(
            id="promo1",
            title="Sicredi e Smiles com 70% de bônus",
            link="https://exemplo.com/1",
            summary="Sicredi transfira",
            source_bank="Sicredi",
            target_program="Smiles",
            bonus_percentage=70
        ),
        Promotion(
            id="promo2",
            title="Livelo e LATAM Pass com 30% de bônus",
            link="https://exemplo.com/2",
            summary="Livelo transfira",
            source_bank="Livelo",
            target_program="LATAM Pass",
            bonus_percentage=30
        ),
        Promotion(
            id="promo3",
            title="Itaú e Azul com 40% de bônus",
            link="https://exemplo.com/3",
            summary="Itaú transfira",
            source_bank="Itaú",
            target_program="Azul Fidelidade",
            bonus_percentage=40
        ),
    ]

def test_storage_load_and_save(tmp_path):
    storage_file = tmp_path / "data" / "seen_posts.json"
    storage = Storage(file_path=str(storage_file))

    assert storage.load_seen_ids() == set()

    storage.save_seen_id("id1")
    storage.save_seen_ids(["id2", "id3"])

    loaded = storage.load_seen_ids()
    assert loaded == {"id1", "id2", "id3"}

def test_filter_all_banks(sample_promotions):
    config = AppConfig(banks=["all"], min_bonus_percentage=0)
    promo_filter = PromotionFilter()

    seen_ids = {"promo1"}
    filtered = promo_filter.filter_promotions(sample_promotions, config, seen_ids)

    # promo1 is already seen, so promo2 and promo3 should be returned
    assert len(filtered) == 2
    assert [p.id for p in filtered] == ["promo2", "promo3"]

def test_filter_specific_bank_and_bonus(sample_promotions):
    # Only Sicredi, minimum bonus 50%
    config = AppConfig(banks=["sicredi"], min_bonus_percentage=50)
    promo_filter = PromotionFilter()

    seen_ids = set()
    filtered = promo_filter.filter_promotions(sample_promotions, config, seen_ids)

    assert len(filtered) == 1
    assert filtered[0].id == "promo1"
    assert filtered[0].source_bank == "Sicredi"

def test_filter_min_bonus_cutoff(sample_promotions):
    # All banks, but minimum 45% bonus
    config = AppConfig(banks=["all"], min_bonus_percentage=45)
    promo_filter = PromotionFilter()

    seen_ids = set()
    filtered = promo_filter.filter_promotions(sample_promotions, config, seen_ids)

    # Only promo1 (70%) meets >= 45%
    assert len(filtered) == 1
    assert filtered[0].id == "promo1"
