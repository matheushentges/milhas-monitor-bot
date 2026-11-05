import argparse
import logging
import sys
from typing import List, Set
from src.config import load_config
from src.models import RawPromotion, Promotion
from src.extractor import extract_promotion
from src.filter import PromotionFilter
from src.storage import Storage
from src.notifier import TelegramNotifier
from src.scrapers.rss_scraper import RssScraper
from src.scrapers.direct_smiles import DirectSmilesScraper
from src.scrapers.direct_azul import DirectAzulScraper

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("milhas_bot")


def run_pipeline(
    config_path: str = "config.yaml",
    storage_path: str = "data/seen_posts.json",
    dry_run: bool = False
) -> int:
    config = load_config(config_path)
    storage = Storage(file_path=storage_path)
    seen_ids = storage.load_seen_ids()
    promo_filter = PromotionFilter()
    notifier = TelegramNotifier(
        bot_token=config.telegram_bot_token,
        chat_id=config.telegram_chat_id
    )

    logger.info("Iniciando varredura de promoções...")
    logger.info("Bancos monitorados: %s (Bônus mínimo: %s%%)", config.banks, config.min_bonus_percentage)
    logger.info("Posts já vistos no histórico: %d", len(seen_ids))

    # 1. Coleta Híbrida
    raw_promotions: List[RawPromotion] = []

    # Feeds RSS
    if config.feeds:
        rss = RssScraper(config.feeds)
        raw_promotions.extend(rss.fetch_promotions())

    # Scrapers Diretos
    if config.direct_scrapers.get("smiles", True):
        smiles = DirectSmilesScraper()
        raw_promotions.extend(smiles.fetch_promotions())

    if config.direct_scrapers.get("azul", True):
        azul = DirectAzulScraper()
        raw_promotions.extend(azul.fetch_promotions())

    logger.info("Total de itens brutos coletados: %d", len(raw_promotions))

    # 2. Extração Semântica
    extracted_promotions: List[Promotion] = []
    seen_in_batch: Set[str] = set()

    for raw in raw_promotions:
        promo = extract_promotion(raw)
        if promo:
            # Evita duplicatas dentro do próprio lote (ex: mesma promo na Smiles e no RSS)
            batch_key = f"{promo.source_bank.lower()}:{promo.target_program.lower()}:{promo.bonus_percentage}"
            if batch_key in seen_in_batch:
                continue
            seen_in_batch.add(batch_key)
            extracted_promotions.append(promo)

    logger.info("Promoções válidas de transferência identificadas: %d", len(extracted_promotions))

    # 3. Filtragem e Deduplicação
    eligible = promo_filter.filter_promotions(extracted_promotions, config, seen_ids)
    logger.info("Promoções novas e elegíveis para notificação: %d", len(eligible))

    # 4. Notificação e Atualização de Estado
    newly_sent_ids: List[str] = []

    for promo in eligible:
        success = notifier.send_notification(promo, dry_run=dry_run)
        if success:
            newly_sent_ids.append(promo.id)

    if not dry_run and newly_sent_ids:
        storage.save_seen_ids(newly_sent_ids)
        logger.info("Estado atualizado com %d novos registros em %s", len(newly_sent_ids), storage_path)

    logger.info("Execução finalizada com sucesso. Notificações disparadas: %d", len(newly_sent_ids))
    return len(newly_sent_ids)


def main():
    parser = argparse.ArgumentParser(description="Bot de Monitoramento de Promoções de Milhas")
    parser.add_argument("--config", default="config.yaml", help="Caminho do arquivo config.yaml")
    parser.add_argument("--storage", default="data/seen_posts.json", help="Caminho do seen_posts.json")
    parser.add_argument("--dry-run", action="store_true", help="Executa sem enviar mensagens ao Telegram e sem salvar no storage")
    parser.add_argument("--verbose", action="store_true", help="Ativa logs detalhados (DEBUG)")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    run_pipeline(
        config_path=args.config,
        storage_path=args.storage,
        dry_run=args.dry_run
    )


if __name__ == "__main__":
    main()
