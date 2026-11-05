import pytest
from src.models import RawPromotion, Promotion
from src.extractor import extract_promotion

def test_extract_sicredi_smiles():
    raw = RawPromotion(
        title="Sicredi oferece até 70% de bônus na transferência de pontos para a Smiles",
        link="https://exemplo.com/sicredi-smiles",
        summary="Aproveite a promoção de transferência de pontos Sicredi para a Smiles com até 70% de bônus.",
        published_at="2026-11-05T10:00:00Z",
        source="rss:melhoresdestinos"
    )
    promo = extract_promotion(raw)
    assert promo is not None
    assert promo.source_bank == "Sicredi"
    assert promo.target_program == "Smiles"
    assert promo.bonus_percentage == 70
    assert promo.link == "https://exemplo.com/sicredi-smiles"

def test_extract_livelo_azul():
    raw = RawPromotion(
        title="Livelo e Azul: transfira seus pontos com até 100% de bônus",
        link="https://exemplo.com/livelo-azul",
        summary="Clientes Livelo ganham até 100% de bônus ao transferir pontos para o Azul Fidelidade.",
        source="rss:passageirodeprimeira"
    )
    promo = extract_promotion(raw)
    assert promo is not None
    assert promo.source_bank == "Livelo"
    assert promo.target_program == "Azul Fidelidade"
    assert promo.bonus_percentage == 100

def test_extract_itau_latam_pass():
    raw = RawPromotion(
        title="Itaú e LATAM Pass: ganhe 30% de bônus na transferência",
        link="https://exemplo.com/itau-latam",
        summary="Promoção exclusiva para clientes cartões Itaú transferindo para o LATAM Pass.",
        source="rss:pontospravoar"
    )
    promo = extract_promotion(raw)
    assert promo is not None
    assert promo.source_bank == "Itaú"
    assert promo.target_program == "LATAM Pass"
    assert promo.bonus_percentage == 30

def test_ignore_non_transfer_post():
    raw = RawPromotion(
        title="Smiles oferece passagens nacionais a partir de 3.000 milhas",
        link="https://exemplo.com/resgate-smiles",
        summary="Encontre passagens promocionais baratas para voar com a GOL.",
        source="rss:melhoresdestinos"
    )
    promo = extract_promotion(raw)
    assert promo is None

def test_extract_all_banks():
    raw = RawPromotion(
        title="Azul Fidelidade oferece até 80% de bônus na transferência de pontos de todos os bancos",
        link="https://exemplo.com/todos-os-bancos-azul",
        summary="Transfira pontos do seu cartão de crédito para a Azul e ganhe bônus.",
        source="rss:melhoresdestinos"
    )
    promo = extract_promotion(raw)
    assert promo is not None
    assert promo.source_bank == "Diversos Bancos"
    assert promo.target_program == "Azul Fidelidade"
    assert promo.bonus_percentage == 80
