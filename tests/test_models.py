"""Tests for GPUWatch data models."""

from __future__ import annotations

import unittest
from datetime import datetime, timezone

from src.models import ArbitrageOpportunity, GPUOffer


class TestGPUOffer(unittest.TestCase):
    def test_creation_with_defaults(self) -> None:
        offer = GPUOffer(
            provider="aws",
            gpu_name="H100",
            gpu_memory=80.0,
            price_per_hour=3.50,
        )
        self.assertEqual(offer.provider, "aws")
        self.assertEqual(offer.gpu_name, "H100")
        self.assertEqual(offer.gpu_memory, 80.0)
        self.assertEqual(offer.price_per_hour, 3.50)
        self.assertEqual(offer.currency, "USD")
        self.assertFalse(offer.spot)
        self.assertEqual(offer.region, "")
        self.assertIsInstance(offer.timestamp, datetime)

    def test_creation_with_all_fields(self) -> None:
        ts = datetime(2026, 1, 1, tzinfo=timezone.utc)
        offer = GPUOffer(
            provider="lambda",
            gpu_name="A100",
            gpu_memory=40.0,
            price_per_hour=1.10,
            currency="EUR",
            spot=True,
            region="us-east-1",
            timestamp=ts,
        )
        self.assertTrue(offer.spot)
        self.assertEqual(offer.region, "us-east-1")
        self.assertEqual(offer.timestamp, ts)

    def test_as_dict(self) -> None:
        ts = datetime(2026, 3, 15, 12, 0, 0, tzinfo=timezone.utc)
        offer = GPUOffer(
            provider="runpod",
            gpu_name="H100",
            gpu_memory=80.0,
            price_per_hour=4.99,
            timestamp=ts,
        )
        d = offer.as_dict()
        self.assertEqual(d["provider"], "runpod")
        self.assertEqual(d["price_per_hour"], 4.99)
        self.assertIn("2026-03-15", d["timestamp"])

    def test_frozen(self) -> None:
        offer = GPUOffer(provider="a", gpu_name="b", gpu_memory=1, price_per_hour=1)
        with self.assertRaises(AttributeError):
            offer.provider = "x"  # type: ignore[misc]


class TestArbitrageOpportunity(unittest.TestCase):
    def test_creation(self) -> None:
        arb = ArbitrageOpportunity(
            gpu_name="H100",
            min_price=0.80,
            min_provider="verda",
            max_price=4.99,
            max_provider="runpod",
            spread_pct=523.75,
        )
        self.assertEqual(arb.gpu_name, "H100")
        self.assertAlmostEqual(arb.spread_pct, 523.75)

    def test_as_dict_rounds_spread(self) -> None:
        arb = ArbitrageOpportunity(
            gpu_name="A100",
            min_price=0.12,
            min_provider="vultr",
            max_price=1.59,
            max_provider="cudo",
            spread_pct=1225.0,
        )
        d = arb.as_dict()
        self.assertEqual(d["spread_pct"], 1225.0)
        self.assertEqual(d["min_provider"], "vultr")


if __name__ == "__main__":
    unittest.main()
