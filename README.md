# DevPulse Aggregator

An asynchronous Python data pipeline and CLI tool that concurrently fetches trending Python repositories from **GitHub** and articles from **Dev.to**, normalizes engagement metrics across sources, persists deduplicated records to **SQLite**, and generates a formatted Markdown morning briefing (`digest.md`).

## Key Engineering Highlights

- **Concurrent API Ingestion (`asyncio` & `aiohttp`):** Fetches data from multiple REST APIs in parallel with non-blocking I/O.
- **Resilient Network Layer:** Implements a custom `@retry` decorator with configurable backoff and custom exception hierarchies (`APIFetchError`) to handle rate limits (HTTP 403/429) gracefully without crashing the pipeline.
- **Cross-Source Score Normalization:** Solves scale bias between GitHub stars (hundreds of thousands) and Dev.to reactions (dozens) by computing a per-source relative score on a `0–100` scale before ranking.
- **Transactional Persistence & Auto-Migration:** Uses a custom context manager (`DatabaseConnection`) for atomic SQLite transactions (`COMMIT`/`ROLLBACK`) and `ON CONFLICT(url) DO UPDATE` to prevent duplicate entries while keeping scores fresh.
- **Memory-Efficient Streaming:** Reads stored records back from SQLite using a Python generator (`yield`) to maintain a flat memory footprint regardless of database size.
- **Isolated Unit Test Suite (`pytest`):** Covers API parsing via `unittest.mock.AsyncMock`, SQLite deduplication using `:memory:` fixtures, and cross-source ranking math.

---

## Project Structure

```text
devpulse-aggregator/
├── src/
│   ├── __init__.py
│   ├── config.py        # Dynamic path resolution (pathlib) and pipeline constants
│   ├── models.py        # Article data model and ArticleCollection ranking logic
│   ├── fetchers.py      # Abstract BaseFetcher, GitHub/Dev.to implementations, @retry decorator
│   ├── database.py      # SQLite context manager and row-streaming generator
│   ├── exporter.py      # Markdown briefing generator (digest.md)
│   └── main.py          # CLI entry point (argparse) and pipeline orchestrator
├── tests/
│   ├── test_fetchers.py # Mocked async HTTP tests
│   ├── test_database.py # In-memory SQLite deduplication tests
│   └── test_models.py   # Normalization and --top N sorting tests
├── run_digest.bat       # Batch wrapper for automated Windows Task Scheduler runs
├── requirements.txt
└── .gitignore
```

---

## Quick Start

### 1. Clone & Set Up Environment

```bash
git clone [https://github.com/YOUR_USERNAME/devpulse-aggregator.git](https://github.com/luvzaed/devpulse-aggregator.git)
cd devpulse-aggregator
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the Aggregator

Generate a briefing with all stored items, or pass `--top N` to limit the output to the highest-ranking items across sources:

```bash
python src/main.py --top 10
```

This creates `digest.md` in the project root with clickable links, normalized scores, and summaries.

### 3. Run the Test Suite

```bash
pytest
```

---

## Automated Local Scheduling (Windows)

To run the aggregator automatically every morning at 8:00 AM via Windows Task Scheduler:

```powershell
schtasks /create /tn "DevPulseMorningDigest" /tr "C:\path\to\devpulse-aggregator\run_digest.bat" /sc daily /st 08:00 /f
```
