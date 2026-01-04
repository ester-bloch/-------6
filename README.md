# Outdoor Intelligence MCP Server

A Python implementation of a **Model Context Protocol (MCP)** server that performs controlled external HTTP requests and exposes structured outdoor and environmental data to language models through typed tools.

The server executes network calls to authoritative data sources, aggregates external data, and returns schema-validated outputs suitable for deterministic reasoning and technical evaluation.

---

## Purpose

This MCP server provides a dedicated runtime for executing external HTTP calls, retrieving live outdoor and environmental data, and exposing that data through a bounded, predictable tool interface.

It centralizes network access, validation, and orchestration concerns that should not be handled directly by a language model.

---

## Available MCP Tools

- **search_locations**  
  Search for outdoor locations using geographic coordinates and distance constraints.

- **risk_and_safety_summary**  
  Return an interpreted safety-oriented summary derived from available data sources.

- **get_real_time_conditions**  
  Fetch live environmental and weather-related conditions.

- **get_location_profile**  
  Retrieve structured metadata for a specific location.

All tools return typed responses with explicit schemas.

---

## Data Sources

### [National Park Service API (USA)](https://www.nps.gov/subjects/developer/api-documentation.htm)

The official national data source of the United States National Park Service, providing authoritative information about U.S. national parks and protected areas.

Requires `NPS_API_KEY`.

### [OpenStreetMap / Overpass API](https://www.openstreetmap.org)

Global, community-maintained geographic data used for spatial and location-based queries.

### [OpenWeather API](https://openweathermap.org/api)

Live environmental and weather-related data relevant to outdoor activity.

Requires `OPENWEATHER_API_KEY`.

---

## Project Structure

```
src/
├── outdoor_mcp/
│   ├── __init__.py
│   ├── __main__.py          # Application entry point
│   ├── server.py            # FastMCP server setup
│   ├── config.py            # Configuration handling
│   ├── models/              # Typed schemas (Pydantic)
│   ├── tools/               # MCP-facing tool contracts
│   ├── services/            # Business logic orchestration
│   ├── providers/           # External API adapters
│   ├── core/                # HTTP, caching, rate limiting
│   └── utils/               # Shared utilities
tests/
├── unit/
├── integration/
├── property/
└── conftest.py
```

---

## Installation

### Prerequisites
- Python 3.10+
- pip or Poetry

### Using pip

```bash
git clone <repository-url>
cd outdoor-intelligence-mcp
python -m venv venv
source venv/bin/activate
pip install -e .
```

### Using Poetry

```bash
git clone <repository-url>
cd outdoor-intelligence-mcp
poetry install
poetry shell
```

---

## Configuration

### API Keys

1. Generate API keys from:
   - **[National Park Service](https://www.nps.gov/subjects/developer/get-started.htm)**
   - **[OpenWeather](https://home.openweathermap.org/api_keys)**

2. Copy the example environment file:

```bash
cp .env.example .env
```

3. Edit `.env` and add your API keys:

```env
NPS_API_KEY=your_nps_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
```

If API keys are not provided, the server runs in a fallback demo mode using internal logic while preserving tool availability and response structure.

---

## Development and Testing

### Running Tests

```bash
poetry run pytest
poetry run pytest --cov=src --cov-report=html
poetry run pytest tests/unit/
poetry run pytest tests/integration/
poetry run pytest tests/property/
```

### Code Quality

```bash
poetry run black src tests
poetry run isort src tests
poetry run flake8 src tests
poetry run mypy src
```

### Pre-commit Hooks

```bash
pre-commit run --all-files
pre-commit run black
pre-commit run mypy
```

---

## Engineering Quality

- Synchronous HTTP I/O using **HTTPX**
- TTL caching and in-flight request de-duplication
- Rate limiting and retry with exponential backoff
- Clean layered architecture  
  `Transport (MCP stdio) → Tools → Services → Providers → External APIs`
- Fully typed domain models (**Pydantic + mypy**)
- Unit and integration testing with **pytest**

---

## Technology Stack

- **FastMCP** – Official Python MCP SDK
- **Python 3.10+**
- **HTTPX**
- **Pydantic**
- **mypy**
- **pytest**
- **pre-commit**
- **Layered Architecture**

---

## Contributing and Extensibility

Contributions are welcome and are expected to follow the existing layered architecture and design principles of the project.

### Extending the Server

The server is designed to support incremental extension through additional providers and tools.

**Adding a new provider**
- Implement the provider under the `providers/` layer.
- Expose the provider via the service layer.
- Wire the provider into the server initialization flow.

**Adding a new tool**
- Define typed input and output schemas.
- Delegate business logic to the service layer.
- Register the tool at the server level.
- Return structured, schema-validated responses.

This design allows the system to evolve without impacting existing tools or providers.

### Contribution Workflow

- Fork the repository
- Create a feature branch
- Implement changes following the established architecture
- Run tests and ensure code quality
- Submit a pull request

---

## Acknowledgments

- Built with **[FastMCP](https://github.com/jlowin/fastmcp)**
- Data provided by the **[National Park Service API](https://www.nps.gov/subjects/developer/api-documentation.htm)**
- Geographic data from **[OpenStreetMap](https://www.openstreetmap.org)**
- Weather data from **[OpenWeather](https://openweathermap.org/api)**
