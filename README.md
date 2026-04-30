# DistroSim

**A supply chain distribution cost simulator for China → Europe routes.**

DistroSim takes a product's physical and commercial details, queries live public APIs, and returns a full per-unit cost breakdown across every viable distribution route — ocean FCL, ocean LCL, and air freight — ranked by cost, speed, and reliability.

---

## Context

DistroSim was built as a practical tool for small and medium-sized importers, sourcing managers, and logistics students who need to understand the real cost of importing physical goods from China into European markets — without paying for expensive freight quoting platforms or doing the research manually.

The tool models the complete distribution chain from ex-works factory gate to final delivery, broken into up to 12 cost steps per route. Every estimate shows its source, confidence level, and a 90% prediction interval so the user always knows how reliable the number is.

---

## Who Is This For

| User | Use case |
|------|----------|
| **Importers & product buyers** | Get a full landed cost picture before committing to a supplier or shipment |
| **Sourcing & logistics teams** | Compare FCL vs LCL vs air across 8 European destinations in one run |
| **Supply chain students** | Learn how distribution costs are built up step by step, with real data |
| **Founders & e-commerce operators** | Estimate margins and duty exposure before launch |
| **Consultants & analysts** | Quick benchmark comparisons across destinations and freight modes |

No account, no API key, and no subscription is required to run a simulation.

---

## What It Does

### Input
The user provides:
- Product name, HS code, production cost, declared value
- Weight (kg) and dimensions (cm × cm × cm)
- Annual volume
- Destination (8 European cities)
- Freight mode preference (all / ocean only / air only)
- Last-mile preference (B2B pallet / B2C parcel / both)
- Trade scenario (standard MFN tariff, or a custom tariff surcharge %)
- Ranking weights (cost / speed / reliability)

### What the backend does
1. Fetches **World Bank LPI scores** (Logistics Performance Index) for China and the destination country — live, no key required
2. Fetches **WTO MFN duty rates** for the HS code — live, with benchmark fallback
3. Fetches **ECB exchange rates** — live, hourly cache
4. Fetches **port risk news** from RSS feeds relevant to the selected destination region
5. Builds all valid route permutations (up to 8 routes per simulation)
6. Calculates each of up to 12 cost steps per route using benchmark data, with 90% confidence intervals
7. Applies **XGBoost ML multipliers** (trained at startup on 600 synthetic samples using MAPIE conformal prediction) to adjust raw benchmark estimates for LPI, product weight, volume, and HS chapter
8. Calculates **CO2 emissions per unit** per route using GLEC Framework v3 / ISO 14083 emission factors
9. Tags each route with **live risk signals** extracted from the news feed (e.g. port congestion, strikes, Suez disruptions)
10. Ranks all routes by the user's weighted cost/time/reliability preference

### The 12 cost steps modelled per ocean route

| # | Step | What it covers |
|---|------|----------------|
| 1 | Ex-Works | Factory gate production cost |
| 2 | Origin Inland Transport | Factory → Shanghai port/airport |
| 3 | Export Customs & Docs | Chinese customs broker fee |
| 4 | Origin Port Handling (THC) | Terminal handling at Shanghai |
| 5 | International Freight | Ocean FCL / LCL / Air freight |
| 6 | Freight Insurance | Marine cargo insurance (% of CIF) |
| 7 | Destination Port Handling | THC at destination hub port |
| 8 | Import Customs & Duties | MFN duty + VAT + import broker fee |
| 9 | Destination Inland Transport | Port/airport → destination warehouse |
| 10 | Warehousing | Storage + handling at destination |
| 11 | Last-Mile Delivery | Road pallet (B2B) or parcel (B2C) |

Air routes skip THC steps and go directly PVG → destination airport.

### Destinations supported (v1)

| ID | City | Country | Hub Port |
|----|------|---------|----------|
| `dk_aarhus` | Aarhus | Denmark | Rotterdam → Aarhus |
| `de_hamburg` | Hamburg | Germany | Hamburg |
| `nl_rotterdam` | Rotterdam | Netherlands | Rotterdam |
| `se_gothenburg` | Gothenburg | Sweden | Rotterdam → Gothenburg |
| `gb_felixstowe` | Felixstowe | United Kingdom | Felixstowe |
| `tr_istanbul` | Istanbul | Turkey | Ambarli/Istanbul |
| `pl_gdansk` | Gdańsk | Poland | Gdańsk |
| `be_antwerp` | Antwerp | Belgium | Antwerp |

### Data sources

| Source | What it provides | Confidence |
|--------|-----------------|------------|
| World Bank LPI API | Logistics Performance Index scores | Live |
| WTO Tariff API | MFN import duty rates by HS code | Live / Benchmark fallback |
| ECB FX API | EUR/USD and other exchange rates | Live (1h cache) |
| RSS feeds (Reuters, Lloyd's, TradeWinds, etc.) | Port and freight disruption news | Live (1h cache) |
| CBRE / JLL / Prologis industrial reports | Warehouse costs by country | Benchmark (2023–2024) |
| Freightos / Xeneta benchmarks | Ocean and air freight rates | Benchmark (2023–2024) |
| GLEC Framework v3 / ISO 14083 | CO2 emission factors | Standard |

All benchmark values carry a min/max range. The ML conformal prediction layer widens the interval if the specific scenario (weight, LPI, volume) warrants it.

---

## Architecture

```
distrosim/
├── backend/                  # FastAPI application
│   ├── main.py               # Routes: /simulate, /destinations, /news, /route-map
│   ├── config.py             # API keys (optional), cache TTLs, ML settings
│   ├── api/
│   │   ├── benchmark.py      # Reads data/*.json, returns DataPoint objects
│   │   ├── world_bank.py     # LPI scores
│   │   ├── wto.py            # MFN duty rates
│   │   ├── currency.py       # ECB exchange rates
│   │   ├── co2.py            # GLEC emission calculator
│   │   ├── news.py           # RSS aggregator, multi-region
│   │   └── news_intelligence.py  # Keyword → route risk signal mapper
│   ├── services/
│   │   ├── simulation.py     # Main orchestrator
│   │   ├── step_calculator.py # Per-step cost/time calculations
│   │   └── route_builder.py  # Route permutation engine
│   ├── models/
│   │   ├── cost_predictor.py      # XGBoost cost multiplier
│   │   ├── lead_time_predictor.py # XGBoost lead-time multiplier
│   │   ├── error_margin.py        # MAPIE conformal prediction intervals
│   │   └── route_optimizer.py    # Weighted route ranking
│   └── db/
│       └── cache.py          # SQLite async cache (aiosqlite)
├── frontend/                 # Nuxt 3 SPA
│   ├── pages/
│   │   ├── index.vue         # Landing page
│   │   ├── simulator.vue     # Input form
│   │   ├── results.vue       # Results dashboard
│   │   └── news.vue          # Port news & risk signals
│   ├── components/
│   │   ├── RouteMap.vue      # Interactive Leaflet.js route map
│   │   ├── WaterfallChart.vue # Cost waterfall by step
│   │   ├── RouteTree.vue     # Route comparison tree
│   │   └── ...
│   ├── composables/
│   │   └── useI18n.ts        # EN/TR translation composable
│   └── stores/
│       └── simulation.ts     # Pinia store
└── data/                     # Benchmark JSON files
    ├── benchmark_rates.json  # Freight, THC, customs, last-mile rates
    ├── warehouse_costs.json  # Warehouse costs by country
    ├── destinations.json     # 8 destination configs with coordinates
    ├── country_list.json     # ISO codes, LPI fallback scores
    └── hs_codes.json         # Common HS code lookup
```

### Tech stack

**Backend:** Python 3.11+, FastAPI, uvicorn, httpx, aiosqlite, XGBoost, scikit-learn, MAPIE, feedparser

**Frontend:** Nuxt 3, Vue 3, TypeScript, Pinia, Tailwind CSS, Leaflet.js, Chart.js

**Infrastructure:** Docker + docker-compose (single command startup)

---

## Running Locally

### With Docker (recommended)

```bash
git clone https://github.com/ardaturker/Distrosim.git
cd Distrosim
cp .env.example .env   # all API keys are optional
docker-compose up
```

Frontend: http://localhost:3000  
Backend API: http://localhost:8000  
API docs: http://localhost:8000/docs

### Without Docker

**Backend:**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
NUXT_PUBLIC_API_BASE=http://localhost:8000 npm run dev
```

### Environment variables

All are optional. The system degrades gracefully to benchmark data when any API is unavailable.

```env
# Optional — higher rate limits on WTO API
WTO_API_KEY=

# Optional — live freight rates (paid APIs)
FREIGHTOS_API_KEY=
EASYSHIP_API_KEY=
DUTIFY_API_KEY=
DESCARTES_API_KEY=
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/simulate` | Run a full simulation. Returns ranked routes with cost breakdown. |
| `GET` | `/destinations` | List all supported destination cities. |
| `GET` | `/hs-codes` | List common HS codes with descriptions. |
| `GET` | `/news?region=rotterdam` | Aggregated port news for a region. |
| `GET` | `/news/risks?region=istanbul` | Risk signals extracted from live news. |
| `GET` | `/news/regions` | List all available news regions. |
| `GET` | `/route-map?destination_id=de_hamburg` | Route geometry for interactive map. |
| `GET` | `/cache/stats` | Cache hit/miss stats and entry count. |
| `DELETE` | `/cache/news` | Force-clear news cache for fresh fetch. |

Full interactive docs at `/docs` (Swagger UI) when the backend is running.

---

## Languages

The frontend supports **English** and **Turkish** via a toggle in the navigation bar. All landing page sections, simulation labels, and route step names are translated.

---

## What Has Been Done (v1)

- Multi-destination simulation engine — 8 European cities, all with destination-specific benchmark lanes, LPI scores, warehouse costs, THC, customs, and last-mile data
- 12-step cost model per route, fully parameterized by product weight, volume, value, and HS code
- Three freight modes: Ocean FCL (40ft), Ocean LCL (CBM-based), Air freight (chargeable weight)
- Two last-mile variants per freight mode: B2B road pallet, B2C parcel delivery
- XGBoost cost and lead-time multipliers with MAPIE conformal 90% prediction intervals
- Live API integrations: World Bank LPI, WTO MFN tariffs, ECB exchange rates
- Benchmark fallback with graceful degradation — no hard dependency on any external API
- CO2 emissions per unit per route (GLEC Framework v3 / ISO 14083)
- News × Route Intelligence — live RSS news tagged to affected freight routes as risk signals
- Multi-region port news aggregation (Rotterdam, Hamburg, Antwerp, Istanbul, Felixstowe, global)
- Tariff scenario toggle — model the cost impact of any % tariff surcharge on top of MFN
- Weighted route ranking by cost, speed, and reliability
- Interactive Leaflet.js route map — dynamic per destination
- Waterfall cost chart and route comparison table
- EN/TR i18n on all landing page and simulation UI text
- Docker + docker-compose single-command deployment
- SQLite async cache with configurable TTLs per data type

---

## What Is Planned (Future Versions)

### Short-term
- **More origin countries** — extend beyond China to Vietnam, Bangladesh, India, and Turkey as manufacturing origins
- **More destination regions** — North America (US East Coast, US West Coast), Southeast Asia, Middle East
- **Live freight rate APIs** — plug in Freightos or Xeneta when API keys are available, with automatic fallback to benchmarks
- **Shareable simulation URLs** — encode simulation parameters in a URL so results can be shared or bookmarked
- **Export to PDF / CSV** — download a full cost breakdown report

### Medium-term
- **Saved simulations** — compare multiple runs side by side across different products or destinations
- **Supplier lead-time integration** — add production lead time from the supplier as an input, giving a full factory-to-customer timeline
- **Break-even calculator** — at what volume does FCL become cheaper than LCL? At what product value does air become justifiable?
- **Multi-leg routing** — model transshipment routes (e.g. via Singapore or Colombo) and rail alternatives (China–Europe block trains)
- **User accounts and history** — save and revisit past simulations

### Long-term
- **Carrier-specific pricing** — integrate with specific carrier or freight forwarder APIs for live quotes
- **Carbon offset cost modeling** — add the cost of purchasing carbon offsets per route as an optional line item
- **API-first mode** — expose DistroSim as a standalone API so it can be embedded in ERP, sourcing, or procurement tools
- **Real-time disruption alerts** — push notifications when a saved route's risk level changes due to live news events

---

## License

MIT — free to use, modify, and deploy.

---

## Author

Built by [Arda Türker](https://github.com/ardaturker) as a personal project exploring supply chain cost modeling, ML-assisted estimation, and full-stack web development.
