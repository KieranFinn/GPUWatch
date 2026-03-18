#!/usr/bin/env python3
"""GPUWatch CLI — GPU cloud pricing tracker.

Usage:
    python gpu_price_tracker.py snapshot [--gpu NAME]
    python gpu_price_tracker.py stats    [--gpu NAME]
    python gpu_price_tracker.py arbitrage [--min-spread PCT]
    python gpu_price_tracker.py export   [--output FILE]
    python gpu_price_tracker.py serve    [--port PORT]
"""

from __future__ import annotations

import argparse
import logging
import sys


def _setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        level=level,
    )


# ── Subcommand handlers ─────────────────────────────────────────


def cmd_snapshot(args: argparse.Namespace) -> None:
    """Collect prices from providers and save to the database."""
    from src.collector import collect_all
    from src.storage import save_snapshot

    offers = collect_all(gpu_name=args.gpu)
    if not offers:
        print("No offers collected. Check your network or gpuhunt installation.")
        sys.exit(1)

    n = save_snapshot(offers)
    print(f"✅ Saved {n} offers to database.")


def cmd_stats(args: argparse.Namespace) -> None:
    """Show per-GPU statistics from the latest snapshot."""
    from src.analyzer import print_stats
    from src.storage import get_latest

    offers = get_latest(gpu_name=args.gpu)
    if not offers:
        print("No data. Run 'snapshot' first.")
        sys.exit(1)
    print_stats(offers)


def cmd_arbitrage(args: argparse.Namespace) -> None:
    """Find and display arbitrage opportunities."""
    from src.analyzer import find_arbitrage, print_arbitrage
    from src.storage import get_latest

    offers = get_latest()
    if not offers:
        print("No data. Run 'snapshot' first.")
        sys.exit(1)
    opps = find_arbitrage(offers, min_spread=args.min_spread)
    print_arbitrage(opps)

    if args.notify and opps:
        from src.notifier import notify_arbitrage

        notify_arbitrage(opps)


def cmd_export(args: argparse.Namespace) -> None:
    """Export all stored data to CSV."""
    from src.storage import export_csv

    csv_text = export_csv(output=args.output)
    if args.output:
        print(f"✅ Exported to {args.output}")
    else:
        print(csv_text)


def cmd_serve(args: argparse.Namespace) -> None:
    """Start the FastAPI server."""
    import uvicorn

    from src.config import API_HOST, API_PORT

    port = args.port or API_PORT
    host = API_HOST
    print(f"🚀 Starting GPUWatch API on {host}:{port}")
    uvicorn.run("src.api:app", host=host, port=port, reload=args.reload)


# ── CLI definition ───────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gpuwatch",
        description="GPUWatch — GPU cloud pricing tracker & analytics",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")
    sub = parser.add_subparsers(dest="command", required=True)

    # snapshot
    p_snap = sub.add_parser("snapshot", help="Collect current prices and save to DB")
    p_snap.add_argument("--gpu", type=str, default=None, help="Filter by GPU name")
    p_snap.set_defaults(func=cmd_snapshot)

    # stats
    p_stats = sub.add_parser("stats", help="Show price statistics")
    p_stats.add_argument("--gpu", type=str, default=None, help="Filter by GPU name")
    p_stats.set_defaults(func=cmd_stats)

    # arbitrage
    p_arb = sub.add_parser("arbitrage", help="Find arbitrage opportunities")
    p_arb.add_argument("--min-spread", type=float, default=100.0, help="Minimum spread %% (default: 100)")
    p_arb.add_argument("--notify", action="store_true", help="Send Telegram alert")
    p_arb.set_defaults(func=cmd_arbitrage)

    # export
    p_exp = sub.add_parser("export", help="Export data to CSV")
    p_exp.add_argument("--output", "-o", type=str, default=None, help="Output file path (stdout if omitted)")
    p_exp.set_defaults(func=cmd_export)

    # serve
    p_serve = sub.add_parser("serve", help="Start API server")
    p_serve.add_argument("--port", type=int, default=None, help="Port number")
    p_serve.add_argument("--reload", action="store_true", help="Enable auto-reload (dev mode)")
    p_serve.set_defaults(func=cmd_serve)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    _setup_logging(args.verbose)
    args.func(args)


if __name__ == "__main__":
    main()
