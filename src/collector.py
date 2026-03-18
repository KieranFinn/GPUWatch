"""Data collection using the gpuhunt library."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from src.config import COLLECT_TIMEOUT, PROVIDERS
from src.models import GPUOffer

logger = logging.getLogger(__name__)


def collect_all(
    gpu_name: Optional[str] = None,
    providers: Optional[list[str]] = None,
    timeout: int = COLLECT_TIMEOUT,
) -> list[GPUOffer]:
    """Collect GPU offers from all (or selected) providers via gpuhunt.

    Args:
        gpu_name: Optional filter — only return offers matching this GPU name (case-insensitive substring).
        providers: Explicit provider list; falls back to config PROVIDERS (empty = all).
        timeout: Per-provider timeout in seconds.

    Returns:
        List of GPUOffer dataclasses.
    """
    try:
        from gpuhunt import QueryFilter, query
    except ImportError:
        logger.error(
            "gpuhunt is not installed. Run: pip install gpuhunt"
        )
        return []

    provider_list = providers or PROVIDERS or None  # None → gpuhunt uses all

    query_filter = QueryFilter()
    if gpu_name:
        query_filter.gpu_name = [gpu_name]

    try:
        logger.info("Collecting GPU prices (providers=%s, timeout=%ss) …", provider_list or "all", timeout)
        raw_offers = query(provider_list, query_filter=query_filter)
    except Exception:
        logger.exception("Failed to query gpuhunt")
        return []

    now = datetime.now(timezone.utc)
    offers: list[GPUOffer] = []
    for item in raw_offers:
        try:
            offers.append(
                GPUOffer(
                    provider=getattr(item, "provider", "unknown"),
                    gpu_name=getattr(item, "gpu_name", "unknown"),
                    gpu_memory=float(getattr(item, "gpu_memory", 0.0)),
                    price_per_hour=float(getattr(item, "price", 0.0)),
                    currency="USD",
                    spot=bool(getattr(item, "spot", False)),
                    region=getattr(item, "region", ""),
                    timestamp=now,
                )
            )
        except Exception:
            logger.warning("Skipping malformed offer: %s", item, exc_info=True)

    if gpu_name:
        needle = gpu_name.lower()
        offers = [o for o in offers if needle in o.gpu_name.lower()]

    logger.info("Collected %d offers", len(offers))
    return offers
