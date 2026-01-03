# Outdoor Intelligence MCP Server (stdio)

A production-grade **Model Context Protocol (MCP)** server that provides **decision-support** for outdoor activities: location discovery, deep profiles, real-time conditions, and a deterministic risk score with evidence.

This repository is designed for **human reviewers and AI evaluators**:
- Runs as a **real stdio MCP server** (Claude Desktop compatible).
- Clean layered architecture (**Tools → Services → Providers**).
- Async I/O, TTL caching, rate limiting, structured logs, and a stable JSON contract.
- No “README promises” that are not implemented.

---

## What you get

### Smart tools (LLM-native)
| Tool | Purpose | Notes |
|---|---|---|
| `search_locations` | Find POIs / trails / parks near coordinates | OSM via Overpass |
| `get_location_profile` | Nearby features and profile for a location | OSM feature scan |
| `get_real_time_conditions` | Weather + alerts | OpenWeather + extensible alerts provider |
| `risk_and_safety_summary` | **Risk score (0–100)** with breakdown, evidence, recommendations | Deterministic, explainable |

All tools return **structured JSON**: `ok`, `data`, `provenance`, `cache`, `warnings`.

---

## Architecture

```
src/outdoor_mcp/
  __main__.py              # python -m outdoor_mcp
  server.py                # FastMCP registration + orchestration (thin)
  tools/                   # Pydantic tool schemas (inputs)
  services/                # business logic (fusion, scoring)
  providers/               # external providers (Overpass/OpenWeather/NPS stub)
  models/                  # response schemas (Pydantic v2)
  core/                    # cache, http client, rate limiting, logging, settings
  utils/                   # id parsing and helpers
```

**Rule of engagement:** Tools never call HTTP. Providers never return “tool-shaped” responses.

---

## Quickstart

### 1) Install
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

### 2) Configure (optional but recommended)
Copy `.env.example` → `.env` and set:
- `OPENWEATHER_API_KEY` for real weather (otherwise demo fallback is used).

### 3) Run (stdio)
```bash
python -m outdoor_mcp
# or
outdoor-intelligence-mcp
```

**Logging:** goes to `stderr`. MCP protocol stays on `stdout`.

---

## Claude Desktop configuration

Create / edit your Claude Desktop config and add:

```json
{
  "mcpServers": {
    "outdoor-intelligence": {
      "command": "python",
      "args": ["-m", "outdoor_mcp"],
      "env": {
        "OPENWEATHER_API_KEY": "YOUR_KEY_OPTIONAL"
      }
    }
  }
}
```

---

## Example tool calls (conceptual)

### search_locations
Input:
```json
{"lat": 31.7767, "lon": 35.2345, "radius_km": 5, "query": "park", "limit": 5}
```

Output (shape):
```json
{
  "ok": true,
  "data": {"locations": [{"id":"osm:node:123:31.77:35.23","name":"...","kind":"park","center":{"lat":31.77,"lon":35.23}}]},
  "provenance": {"sources":["osm_overpass"], "fetched_at_iso":"..."},
  "cache": {"hit": false, "age_s": 0, "ttl_s": 600},
  "warnings": []
}
```

### risk_and_safety_summary
Output includes:
- `risk_score` (0–100)
- `breakdown` (weather/alerts/remoteness/daylight)
- `evidence` (raw conditions + feature_count + timestamps)
- `recommendations`
- `uncertainties` (explicit, reviewer-friendly)

---

## Testing

```bash
pip install -r requirements-dev.txt
pytest -q
```

Tests are **offline-friendly**:
- Risk scoring logic is unit-tested.
- Cache behavior is unit-tested.
- Integration import smoke test ensures packaging + server instantiation.

---

## Design tradeoffs (explicit)

- **NPS geo-alerts are not supported directly** by the public API, so the NPS provider is intentionally conservative (returns empty unless you extend it with parkCode-based lookups).
- Daylight risk is a deterministic heuristic (no sunrise provider integrated by default to keep the base system stable and easy to review).
- This server prioritizes **depth and correctness** over a large number of shallow tools.

---

## Extending the server

Add a new provider:
1. Create `providers/<name>.py`
2. Expose it via `services/`
3. Wire it into `server.py`

Add a new tool:
1. Define input schema in `tools/schemas.py`
2. Register tool in `server.py`
3. Return structured JSON (`ToolResponse`)

---

## License
MIT (or adapt as required for the hiring process)
