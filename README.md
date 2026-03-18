# ⚡️ GPUWatch

**Because GPU pricing shouldn't be a black box.**

Real-time GPU cloud pricing tracker, comparator, and analytics engine. Track prices across 12+ providers, spot arbitrage opportunities, and analyze market trends.

---

## 🎯 What is GPUWatch?

The GPU cloud market is fragmented and opaque. Prices for the same GPU can vary **10x** across providers, and there's no central place to compare them. GPUWatch fixes that.

- 📊 **Track** real-time pricing from 12+ GPU cloud providers
- 🔍 **Compare** the same GPU across platforms instantly
- 📈 **Analyze** historical price trends and market cycles
- 🚨 **Alert** on arbitrage opportunities and price drops
- 🌐 **API** for programmatic access to all data

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  gpuhunt     │────▶️│   SQLite DB   │────▶️│  Dashboard  │
│  (collector) │     │  (time-series)│     │  (FastAPI)  │
└─────────────┘     └──────────────┘     └─────────────┘
       │                    │                     │
   12+ providers      Historical data        REST API
                                             Telegram Bot
```

## 📡 Supported Providers

| Provider | Status | GPU Types |
|----------|--------|-----------|
| AWS | ✅ | A10G, A100, H100, P4 |
| GCP | ✅ | T4, A100, H100, L4 |
| Azure | ✅ | T4, A100, H100 |
| Lambda Cloud | ✅ | A100, H100, H200 |
| RunPod | ✅ | A100, H100, B200 |
| Vast.ai | ✅ | A100, 4090, H100 |
| Vultr | ✅ | A100, H100 |
| Cudo | ✅ | A100, RTX 4090 |
| Tensordock | ✅ | A100, RTX 4090 |
| OCI (Oracle) | ✅ | A10, A100 |
| DataCrunch | ✅ | A100, H100 |
| Verda (nebius) | ✅ | H100, H200 |
| Akash Network | 🔜 | On-chain data |

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pip or uv

### Installation

```bash
git clone https://github.com/YOUR_ORG/GPUWatch.git
cd GPUWatch
pip install -r requirements.txt
```

### Take Your First Snapshot

```bash
# Collect current prices from all providers
python gpu_price_tracker.py snapshot

# View statistics
python gpu_price_tracker.py stats

# Find arbitrage opportunities
python gpu_price_tracker.py arbitrage

# Export to CSV
python gpu_price_tracker.py export --output prices.csv

# Start API server
python gpu_price_tracker.py serve --port 8765
```

## 📊 Sample Output

```
=== GPU Price Statistics ===

GPU: H100 80GB
  Providers: 8
  Min: $0.80/hr (Verda)
  Max: $4.99/hr (RunPod)
  Avg: $2.86/hr
  Spread: 524%  🚨 Arbitrage opportunity!

GPU: A100 80GB
  Providers: 10
  Min: $0.12/hr (Vultr)
  Max: $1.59/hr (Cudo)
  Avg: $0.95/hr
  Spread: 1196%  🚨 Arbitrage opportunity!
```

## 🔌 API

```bash
# Get latest prices for a specific GPU
GET /api/v1/prices?gpu=H100

# Get historical prices
GET /api/v1/history?gpu=A100&days=30

# Get arbitrage opportunities
GET /api/v1/arbitrage?min_spread=100

# Get all supported GPUs
GET /api/v1/gpus
```

## 🗺️ Roadmap

- [x] Multi-provider price collection (12 providers)
- [x] SQLite time-series storage
- [x] Arbitrage detection
- [x] CSV export
- [x] Simple API server
- [ ] Web Dashboard (FastAPI + React)
- [ ] Telegram/Discord price alert bot
- [ ] Akash on-chain data integration
- [ ] Historical trend analysis & visualization
- [ ] Spot vs on-demand price comparison
- [ ] Price prediction model
- [ ] GPU availability tracking (not just price)

## 🧱 Tech Stack

- **Data Collection**: [gpuhunt](https://github.com/dstackai/gpuhunt) + custom scrapers
- **Storage**: SQLite (→ TimescaleDB for production)
- **API**: FastAPI
- **Frontend**: React + Recharts (planned)
- **Alerts**: Telegram Bot API

## 🤝 Contributing

PRs welcome! Especially for:
- New provider integrations
- Dashboard UI/UX
- Price analysis algorithms
- Documentation improvements

## 📄 License

MIT

---

<p align="center">
  <b>GPUWatch</b> — Track every GPU, on every cloud, at every price point. ⚡️
</p>
