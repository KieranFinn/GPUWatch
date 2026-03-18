"""Telegram notification support."""

from __future__ import annotations

import logging
from typing import Optional

import requests

from src.config import TG_BOT_TOKEN, TG_CHAT_ID
from src.models import ArbitrageOpportunity

logger = logging.getLogger(__name__)

_API_BASE = "https://api.telegram.org/bot{token}"


def send_message(
    text: str,
    token: Optional[str] = None,
    chat_id: Optional[str] = None,
    parse_mode: str = "HTML",
) -> bool:
    """Send a Telegram message. Returns True on success."""
    tok = token or TG_BOT_TOKEN
    cid = chat_id or TG_CHAT_ID
    if not tok or not cid:
        logger.warning("Telegram credentials not configured; skipping notification.")
        return False

    url = f"{_API_BASE.format(token=tok)}/sendMessage"
    payload = {"chat_id": cid, "text": text, "parse_mode": parse_mode}
    try:
        resp = requests.post(url, json=payload, timeout=15)
        resp.raise_for_status()
        logger.info("Telegram message sent to %s", cid)
        return True
    except requests.RequestException:
        logger.exception("Failed to send Telegram message")
        return False


def notify_arbitrage(opportunities: list[ArbitrageOpportunity]) -> bool:
    """Format and send arbitrage alerts via Telegram."""
    if not opportunities:
        return False

    lines = ["<b>🚨 GPU Arbitrage Alerts</b>\n"]
    for arb in opportunities[:10]:  # cap at 10
        lines.append(
            f"<b>{arb.gpu_name}</b>\n"
            f"  Buy: ${arb.min_price:.2f}/hr @ {arb.min_provider}\n"
            f"  Sell: ${arb.max_price:.2f}/hr @ {arb.max_provider}\n"
            f"  Spread: {arb.spread_pct:.0f}%\n"
        )
    return send_message("\n".join(lines))
