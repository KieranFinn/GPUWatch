"""Data models for GPUWatch."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class GPUOffer:
    """A single GPU pricing offer from a cloud provider."""

    provider: str
    gpu_name: str
    gpu_memory: float  # GiB
    price_per_hour: float
    currency: str = "USD"
    spot: bool = False
    region: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def as_dict(self) -> dict:
        """Serialise to a plain dict (JSON-friendly)."""
        return {
            "provider": self.provider,
            "gpu_name": self.gpu_name,
            "gpu_memory": self.gpu_memory,
            "price_per_hour": self.price_per_hour,
            "currency": self.currency,
            "spot": self.spot,
            "region": self.region,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True)
class ArbitrageOpportunity:
    """An arbitrage opportunity across providers for the same GPU."""

    gpu_name: str
    min_price: float
    min_provider: str
    max_price: float
    max_provider: str
    spread_pct: float  # ((max - min) / min) * 100

    def as_dict(self) -> dict:
        return {
            "gpu_name": self.gpu_name,
            "min_price": self.min_price,
            "min_provider": self.min_provider,
            "max_price": self.max_price,
            "max_provider": self.max_provider,
            "spread_pct": round(self.spread_pct, 1),
        }
