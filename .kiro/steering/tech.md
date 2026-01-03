# Technology Stack

## Core Framework

- **Python 3.10+** required
- **MCP (Model Context Protocol)**: FastMCP for stdio server implementation
- **Pydantic v2**: Schema validation and settings management
- **httpx**: Async HTTP client
- **structlog**: Structured logging

## Build System

- **setuptools**: Package management via `pyproject.toml`
- **pip**: Dependency management with `requirements.txt` and `requirements-dev.txt`

## Development Tools

- **pytest**: Testing framework with async support (`pytest-asyncio`)
- **ruff**: Linting and formatting
- **mypy**: Static type checking

## External APIs

- **OpenStreetMap Overpass**: Location and POI data
- **OpenWeather API**: Real-time weather conditions
- **NPS API**: National Park Service alerts (stub implementation)

## Common Commands

### Setup
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

### Run Server
```bash
python -m outdoor_mcp
# or
outdoor-intelligence-mcp
```

### Testing
```bash
pip install -r requirements-dev.txt
pytest -q
```

### Linting
```bash
ruff check src/ tests/
```

### Type Checking
```bash
mypy src/
```

## Configuration

- Environment variables via `.env` file (see `.env.example`)
- Settings managed through `pydantic-settings`
- Optional API keys with demo fallback mode
