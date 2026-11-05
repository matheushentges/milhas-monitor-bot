import pytest
from unittest.mock import patch, MagicMock
from src.scrapers.rss_scraper import RssScraper
from src.scrapers.direct_smiles import DirectSmilesScraper
from src.scrapers.direct_azul import DirectAzulScraper

def test_rss_scraper_parses_feed():
    fake_entry = MagicMock()
    fake_entry.title = "Sicredi e Smiles com 70% de bônus"
    fake_entry.link = "https://melhoresdestinos.com.br/sicredi"
    fake_entry.summary = "Transfira pontos do Sicredi"
    fake_entry.published = "Thu, 05 Nov 2026 12:00:00 GMT"

    with patch("feedparser.parse") as mock_parse:
        mock_feed = MagicMock()
        mock_feed.bozo = 0
        mock_feed.entries = [fake_entry]
        mock_parse.return_value = mock_feed

        scraper = RssScraper(feeds=[{"name": "MD", "url": "https://test.com/rss"}])
        promos = scraper.fetch_promotions()

        assert len(promos) == 1
        assert promos[0].title == "Sicredi e Smiles com 70% de bônus"
        assert promos[0].link == "https://melhoresdestinos.com.br/sicredi"
        assert promos[0].source == "rss:MD"

def test_rss_scraper_handles_network_error():
    with patch("feedparser.parse", side_effect=Exception("Connection refused")):
        scraper = RssScraper(feeds=[{"name": "MD", "url": "https://test.com/rss"}])
        promos = scraper.fetch_promotions()
        assert promos == []

@patch("requests.get")
def test_direct_smiles_scraper_success(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = """
    <html>
      <div class="promo-card">
        <h3><a href="/promocoes/sicredi">Sicredi 70% de Bônus</a></h3>
        <p>Transfira seus pontos e ganhe bônus exclusivo</p>
      </div>
    </html>
    """
    mock_get.return_value = mock_resp

    scraper = DirectSmilesScraper()
    promos = scraper.fetch_promotions()

    assert len(promos) >= 1
    assert "Sicredi" in promos[0].title
    assert "smiles.com.br" in promos[0].link
    assert promos[0].source == "direct:smiles"

@patch("requests.get")
def test_direct_smiles_scraper_handles_403_gracefully(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 403
    mock_get.return_value = mock_resp

    scraper = DirectSmilesScraper()
    promos = scraper.fetch_promotions()
    assert promos == []

@patch("requests.get")
def test_direct_azul_scraper_handles_exception_gracefully(mock_get):
    mock_get.side_effect = Exception("Cloudflare blocked")

    scraper = DirectAzulScraper()
    promos = scraper.fetch_promotions()
    assert promos == []
