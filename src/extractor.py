import re
import unicodedata
from typing import Optional, Tuple
from src.models import RawPromotion, Promotion

# Mapeamento de bancos/programas de fidelidade de origem
BANK_PATTERNS = [
    (r"\bsicredi\b", "Sicredi"),
    (r"\blivelo\b", "Livelo"),
    (r"\besfera\b", "Esfera"),
    (r"\b(itau|itaú|iupp)\b", "Itaú"),
    (r"\bbradesco\b", "Bradesco"),
    (r"\bsantander\b", "Santander"),
    (r"\b(banco do brasil|\bbb\b)\b", "Banco do Brasil"),
    (r"\bcaixa\b", "Caixa"),
    (r"\b(c6|c6 bank|átomos|atomos)\b", "C6 Bank"),
    (r"\b(inter|loop inter|inter loop)\b", "Inter"),
    (r"\b(btg|btg pactual)\b", "BTG Pactual"),
    (r"\bnubank\b", "Nubank"),
    (r"\bsicoob\b", "Sicoob"),
    (r"\bbanrisul\b", "Banrisul"),
    (r"\bsafra\b", "Safra"),
    (r"\bporto seguro\b|\bporto bank\b", "Porto Bank"),
    (r"\bcredicard\b", "Credicard"),
    (r"\bpicpay\b", "PicPay"),
    (r"\b(todos os bancos|qualquer banco|demais bancos|bancos parceiros)\b", "Diversos Bancos"),
]

# Mapeamento de programas de milhas de destino
PROGRAM_PATTERNS = [
    (r"\bsmiles\b", "Smiles"),
    (r"\b(azul fidelidade|tudoazul|azul)\b", "Azul Fidelidade"),
    (r"\b(latam pass|latam)\b", "LATAM Pass"),
    (r"\b(tap|miles&go)\b", "TAP Miles&Go"),
    (r"\b(iberia|iberia plus)\b", "Iberia Plus"),
]

TRANSFER_KEYWORDS = [
    r"\btransfer[êe]ncia\b",
    r"\btransfira\b",
    r"\btransferir\b",
    r"\btransferindo\b",
    r"\btransferidos\b",
    r"\bconvers[ãa]o\b",
    r"\bbonificada\b",
]

EXCLUSION_PATTERNS = [
    r"\bvoe para\b",
    r"\bpassagens? a partir\b",
    r"\bpassagens? baratas?\b",
    r"\boferta de voos?\b",
]

BONUS_PATTERNS = [
    r"(?:at[eé]\s+)?(\d{1,3})%\s*(?:de\s+)?b[oô]nus",
    r"b[oô]nus\s+de\s+(?:at[eé]\s+)?(\d{1,3})%",
    r"(\d{1,3})%\s*extras?",
]


def _normalize(text: str) -> str:
    if not text:
        return ""
    return text.lower()


def extract_bank_and_program(text: str) -> Tuple[Optional[str], Optional[str]]:
    norm = _normalize(text)
    detected_bank = None
    detected_program = None

    for pattern, bank in BANK_PATTERNS:
        if re.search(pattern, norm, re.IGNORECASE):
            detected_bank = bank
            break

    for pattern, program in PROGRAM_PATTERNS:
        if re.search(pattern, norm, re.IGNORECASE):
            detected_program = program
            break

    return detected_bank, detected_program


def extract_bonus(text: str) -> Optional[int]:
    norm = _normalize(text)
    for pattern in BONUS_PATTERNS:
        match = re.search(pattern, norm, re.IGNORECASE)
        if match:
            try:
                pct = int(match.group(1))
                if 1 <= pct <= 500:
                    return pct
            except (ValueError, IndexError):
                pass
    return None


def is_transfer_promotion(text: str, bank: Optional[str], program: Optional[str]) -> bool:
    norm = _normalize(text)

    # Descarta ofertas de compra/resgate direto de passagens
    for exc in EXCLUSION_PATTERNS:
        if re.search(exc, norm, re.IGNORECASE):
            return False

    # Para ser promoção de transferência de pontos, DEVE conter palavra indicativa de transferência
    has_transfer_word = any(re.search(kw, norm, re.IGNORECASE) for kw in TRANSFER_KEYWORDS)
    if not has_transfer_word:
        return False

    # E deve ter pelo menos o programa de milhas ou o banco identificado
    return bool(bank or program)


def extract_promotion(raw: RawPromotion) -> Optional[Promotion]:
    full_text = f"{raw.title} {raw.summary}"
    bank, program = extract_bank_and_program(full_text)

    # Se não identificou nem programa aéreo nem banco, não é relevante
    if not bank and not program:
        return None

    # Se não é promoção de transferência de pontos, descartar
    if not is_transfer_promotion(full_text, bank, program):
        return None

    # Se não identificou o banco mas tem palavra de transferência para programa, assume "Diversos Bancos"
    if not bank and program:
        bank = "Diversos Bancos"

    # Se não identificou o programa, não é para milhas aéreas
    if not program:
        return None

    bonus = extract_bonus(full_text)

    return Promotion(
        id=raw.canonical_id,
        title=raw.title.strip(),
        link=raw.link.strip(),
        summary=raw.summary.strip(),
        source_bank=bank,
        target_program=program,
        bonus_percentage=bonus,
        published_at=raw.published_at,
        source=raw.source,
    )
