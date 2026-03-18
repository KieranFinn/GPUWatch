"""Analytics: statistics and arbitrage detection."""

from __future__ import annotations

import statistics
from collections import defaultdict
from typing import Optional

from src.models import ArbitrageOpportunity, GPUOffer


def compute_stats(offers: list[GPUOffer]) -> dict[str, dict]:
    """Compute per-GPU statistics from a list of offers.

    Returns a dict keyed by gpu_name with keys:
        count, min, max, avg, spread_pct, min_provider, max_provider
    """
    grouped: dict[str, list[GPUOffer]] = defaultdict(list)
    for o in offers:
        grouped[o.gpu_name].append(o)

    stats: dict[str, dict] = {}
    for gpu, gpu_offers in sorted(grouped.items()):
        prices = [o.price_per_hour for o in gpu_offers]
        min_offer = min(gpu_offers, key=lambda o: o.price_per_hour)
        max_offer = max(gpu_offers, key=lambda o: o.price_per_hour)
        min_price = min_offer.price_per_hour
        max_price = max_offer.price_per_hour
        spread = ((max_price - min_price) / min_price * 100) if min_price > 0 else 0.0
        stats[gpu] = {
            "count": len(prices),
            "min": min_price,
            "max": max_price,
            "avg": round(statistics.mean(prices), 4),
            "spread_pct": round(spread, 1),
            "min_provider": min_offer.provider,
            "max_provider": max_offer.provider,
        }
    return stats


def find_arbitrage(
    offers: list[GPUOffer],
    min_spread: float = 100.0,
) -> list[ArbitrageOpportunity]:
    """Detect arbitrage opportunities where the spread exceeds *min_spread* %.

    Args:
        offers: Current GPU offers.
        min_spread: Minimum spread percentage to flag.

    Returns:
        Sorted list of ArbitrageOpportunity (highest spread first).
    """
    stats = compute_stats(offers)
    opportunities: list[ArbitrageOpportunity] = []
    for gpu, s in stats.items():
        if s["spread_pct"] >= min_spread:
            opportunities.append(
                ArbitrageOpportunity(
                    gpu_name=gpu,
                    min_price=s["min"],
                    min_provider=s["min_provider"],
                    max_price=s["max"],
                    max_provider=s["max_provider"],
                    spread_pct=s["spread_pct"],
                )
            )
    opportunities.sort(key=lambda a: a.spread_pct, reverse=True)
    return opportunities


# ── Pretty-printing ──────────────────────────────────────────────


def print_stats(offers: list[GPUOffer]) -> None:
    """Pretty-print per-GPU statistics to stdout."""
    stats = compute_stats(offers)
    if not stats:
        print("No data available.")
        return

    print("\n=== GPU Price Statistics ===\n")
    for gpu, s in stats.items():
        flag = "  🚨 Arbitrage opportunity!" if s["spread_pct"] >= 100 else ""
        print(f"GPU: {gpu}")
        print(f"  Providers: {s['count']}")
        print(f"  Min: ${s['min']:.2f}/hr ({s['min_provider']})")
        print(f"  Max: ${s['max']:.2f}/hr ({s['max_provider']})")
        print(f"  Avg: ${s['avg']:.2f}/hr")
        print(f"  Spread: {s['spread_pct']:.0f}%{flag}")
        print()


def print_arbitrage(opportunities: list[ArbitrageOpportunity]) -> None:
    """Pretty-print arbitrage opportunities to stdout."""
    if not opportunities:
        print("No arbitrage opportunities found at the given threshold.")
        return

    print("\n=== Arbitrage Opportunities ===\n")
    for arb in opportunities:
        print(f"🚨 {arb.gpu_name}")
        print(f"   Buy:  ${arb.min_price:.2f}/hr @ {arb.min_provider}")
        print(f"   Sell: ${arb.max_price:.2f}/hr @ {arb.max_provider}")
        print(f"   Spread: {arb.spread_pct:.0f}%")
        print()
