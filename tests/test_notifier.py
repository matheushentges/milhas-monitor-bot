import pytest
from unittest.mock import patch, MagicMock
from src.models import Promotion
from src.notifier import TelegramNotifier

@pytest.fixture
def sample_promo():
    return Promotion(
        id="test1234",
        title="Sicredi oferece até 70% de bônus na transferência para a Smiles",
        link="https://exemplo.com/promo-sicredi",
        summary="Aproveite agora a nova promoção exclusiva para cooperados Sicredi.",
        source_bank="Sicredi",
        target_program="Smiles",
        bonus_percentage=70,
        published_at="2026-11-05T12:00:00Z"
    )

def test_format_message(sample_promo):
    notifier = TelegramNotifier(bot_token="fake-token", chat_id="12345")
    msg = notifier.format_message(sample_promo)

    assert "Sicredi" in msg
    assert "Smiles" in msg
    assert "70% de bônus" in msg
    assert "https://exemplo.com/promo-sicredi" in msg
    assert "<b>" in msg or "*" in msg

@patch("requests.post")
def test_send_notification_success(mock_post, sample_promo):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"ok": True}
    mock_post.return_value = mock_resp

    notifier = TelegramNotifier(bot_token="valid-token", chat_id="12345")
    success = notifier.send_notification(sample_promo)

    assert success is True
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert "valid-token" in args[0]
    assert kwargs["json"]["chat_id"] == "12345"
    assert kwargs["json"]["parse_mode"] == "HTML"

@patch("requests.post")
def test_send_notification_http_error(mock_post, sample_promo):
    mock_post.side_effect = Exception("Network timeout")

    notifier = TelegramNotifier(bot_token="valid-token", chat_id="12345")
    success = notifier.send_notification(sample_promo)

    assert success is False

def test_send_notification_missing_credentials(sample_promo):
    notifier = TelegramNotifier(bot_token=None, chat_id=None)
    success = notifier.send_notification(sample_promo)
    assert success is False
