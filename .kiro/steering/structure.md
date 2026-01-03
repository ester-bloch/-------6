# Project Structure

## Architecture Pattern

**Layered Architecture**: Tools → Services → Providers

```
src/outdoor_mcp/
  __main__.py              # Entry point: python -m outdoor_mcp
  server.py                # FastMCP registration + orchestration (thin layer)
  tools/                   # Pydantic tool input schemas
  services/                # Business logic (fusion, scoring, orchestration)
  providers/               # External API integrations
  models/                  # Response schemas (Pydantic v2)
  core/                    # Infrastructure (cache, HTTP, rate limiting, logging, settings)
  utils/                   # Helpers (ID parsing, etc.)
```

## Key Directories

### `/tools`
- Tool input schemas using Pydantic
- Defines the contract for MCP tool invocations

### `/services`
- `location_service.py`: Location search and profiling
- `conditions_service.py`: Weather and alerts aggregation
- `risk_service.py`: Risk scoring logic

### `/providers`
- `base.py`: Provider protocol and context
- `overpass.py`: OpenStreetMap Overpass integration
- `openweather.py`: OpenWeather API client
- `nps.py`: National Park Service alerts (conservative stub)

### `/models`
- `common.py`: Shared models (ToolResponse, Provenance, Coordinates)
- `location.py`: Location and profile schemas
- `conditions.py`: Weather and alert schemas
- `risk.py`: Risk assessment schemas

### `/core`
- `cache.py`: TTL-based caching
- `http.py`: Async HTTP client wrapper
- `rate_limiter.py`: Rate limiting
- `logging.py`: Structured logging setup
- `settings.py`: Configuration management
- `exceptions.py`: Custom exception hierarchy

### `/utils`
- Helper functions (e.g., coordinate parsing from location IDs)

## Separation of Concerns

**Critical Rule**: Tools never call HTTP directly. Providers never return "tool-shaped" responses.

- **Tools**: Define inputs, delegate to services
- **Services**: Orchestrate providers, apply business logic
- **Providers**: Handle external API calls, return domain objects

## Testing Structure

```
tests/
  unit/                    # Unit tests (cache, risk scoring)
  integration/             # Integration tests (import, server instantiation)
```

Tests are offline-friendly with demo fallback mode.
