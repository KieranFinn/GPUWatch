"""FastAPI server exposing GPU pricing data."""

from __future__ import annotations

from typing import Optional

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

from src import __version__
from src.analyzer import compute_stats, find_arbitrage
from src.storage import get_history, get_latest

app = FastAPI(
    title="GPUWatch API",
    version=__version__,
    description="Real-time GPU cloud pricing tracker.",
)


@app.get("/")
def root() -> dict:
    return {"service": "GPUWatch", "version": __version__, "docs": "/docs"}


@app.get("/api/v1/prices")
def prices(gpu: Optional[str] = Query(None, description="Filter by GPU name (substring match)")) -> JSONResponse:
    """Return the latest price snapshot, optionally filtered by GPU."""
    offers = get_latest(gpu_name=gpu)
    return JSONResponse([o.as_dict() for o in offers])


@app.get("/api/v1/history")
def history(
    gpu: str = Query(..., description="GPU name to look up"),
    days: int = Query(30, ge=1, le=365, description="Number of days of history"),
) -> JSONResponse:
    """Return price history for a specific GPU."""
    offers = get_history(gpu_name=gpu, days=days)
    return JSONResponse([o.as_dict() for o in offers])


@app.get("/api/v1/arbitrage")
def arbitrage(
    min_spread: float = Query(100.0, ge=0, description="Minimum spread % to flag"),
) -> JSONResponse:
    """Find arbitrage opportunities in the latest snapshot."""
    offers = get_latest()
    opps = find_arbitrage(offers, min_spread=min_spread)
    return JSONResponse([a.as_dict() for a in opps])


@app.get("/api/v1/gpus")
def gpus() -> JSONResponse:
    """List all GPU names seen in the latest snapshot."""
    offers = get_latest()
    gpu_names = sorted({o.gpu_name for o in offers})
    return JSONResponse(gpu_names)


@app.get("/api/v1/stats")
def stats(gpu: Optional[str] = Query(None, description="Filter by GPU name")) -> JSONResponse:
    """Per-GPU statistics from the latest snapshot."""
    offers = get_latest(gpu_name=gpu)
    return JSONResponse(compute_stats(offers))
