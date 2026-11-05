import html
import logging
import requests
from typing import Optional
from src.models import Promotion

logger = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        self.bot_token = bot_token
        self.chat_id = chat_id

    @property
    def is_configured(self) -> bool:
        return bool(self.bot_token and self.chat_id)

    def format_message(self, promo: Promotion) -> str:
        safe_bank = html.escape(promo.source_bank)
        safe_program = html.escape(promo.target_program)
        safe_title = html.escape(promo.title)
        safe_link = html.escape(promo.link)

        bonus_text = f"Até {promo.bonus_percentage}% de bônus" if promo.bonus_percentage else "Bônus Promocional"

        return (
            "✈️ <b>NOVA PROMOÇÃO DE TRANSFERÊNCIA!</b>\n\n"
            f"🏦 <b>Origem:</b> {safe_bank}\n"
            f"🎯 <b>Destino:</b> {safe_program}\n"
            f"🎁 <b>Bônus:</b> {bonus_text}\n\n"
            f"📌 <i>{safe_title}</i>\n\n"
            f'🔗 <a href="{safe_link}">Clique aqui para ver a matéria completa</a>'
        )

    def send_notification(self, promo: Promotion, dry_run: bool = False) -> bool:
        message = self.format_message(promo)

        if dry_run:
            logger.info("[DRY RUN] Mensagem que seria enviada ao Telegram:\n%s", message)
            return True

        if not self.is_configured:
            logger.warning("TelegramNotifier não configurado (TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_ID ausentes).")
            return False

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
        }

        try:
            resp = requests.post(url, json=payload, timeout=15)
            if resp.status_code == 200:
                logger.info("Notificação enviada com sucesso para promoção: %s", promo.title)
                return True
            else:
                logger.error("Falha ao enviar mensagem no Telegram. Status: %s, Resposta: %s", resp.status_code, resp.text)
                return False
        except Exception as e:
            logger.error("Erro de conexão ao enviar para o Telegram: %s", e)
            return False
