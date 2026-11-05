import logging
from typing import List, Set
from src.models import Promotion
from src.config import AppConfig

logger = logging.getLogger(__name__)


class PromotionFilter:
    def filter_promotions(
        self,
        promotions: List[Promotion],
        config: AppConfig,
        seen_ids: Set[str]
    ) -> List[Promotion]:
        eligible: List[Promotion] = []

        for promo in promotions:
            # 1. Ignorar se já foi visto
            if promo.id in seen_ids:
                logger.debug("Promoção já notificada: %s", promo.id)
                continue

            # 2. Filtrar por banco configurado
            # Se for 'Diversos Bancos', aceita sempre que o usuário tiver qualquer interesse
            is_generic = promo.source_bank.lower() in ["diversos bancos", "todos os bancos"]
            if not is_generic and not config.should_monitor_bank(promo.source_bank):
                logger.debug("Banco não monitorado: %s", promo.source_bank)
                continue

            # 3. Filtrar por percentual mínimo de bônus
            if promo.bonus_percentage is not None:
                if promo.bonus_percentage < config.min_bonus_percentage:
                    logger.debug("Bônus (%s%%) abaixo do mínimo (%s%%)", promo.bonus_percentage, config.min_bonus_percentage)
                    continue

            eligible.append(promo)

        return eligible
