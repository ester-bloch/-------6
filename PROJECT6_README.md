# Outdoor Intelligence MCP Server

An MCP (Model Context Protocol) server implemented in Python that provides structured access to outdoor, environmental, and location-based intelligence through a unified interface.

The server exposes MCP tools that aggregate and normalize data from multiple external providers, enabling MCP-compatible clients to retrieve environmental conditions, contextual risk signals, and location metadata in a consistent and validated format.

---

## Overview

This project implements an MCP server using the Python MCP SDK with a stdio transport.
It is designed to serve as a data-access layer between language models and external environmental data sources.

The server focuses on:
- Environmental and outdoor intelligence
- Provider abstraction and normalization
- Typed MCP tool interfaces
- Explicit error handling and validation

---

## Architecture

The project follows a modular structure that separates concerns between protocol handling, tool logic, provider access, and shared utilities.

```
src/
  server.py              MCP server initialization and tool registration
  tools/                 MCP tool implementations
  providers/             External data provider clients
  models/                Pydantic request and response models
  utils/                 Logging, retries, and error handling

tests/
  unit/
  integration/
```

All external calls are executed asynchronously.
Input and output schemas are validated using Pydantic models.
Provider-specific errors are translated into consistent MCP responses.

---

## MCP Tools

The server exposes the following tools:

### search_locations
Search for outdoor locations based on geographic coordinates and radius.

### get_location_profile
Retrieve detailed metadata for a specific location.

### get_real_time_conditions
Retrieve current environmental conditions for a location.

### risk_and_safety_summary
Return a synthesized summary of potential environmental risks and safety considerations.

---

## Requirements

- Python 3.10 or later
- Poetry (recommended) or pip

---

## Installation

### Using Poetry

```bash
poetry install
poetry run outdoor-intelligence-mcp
```

### Using pip

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt
python -m src.server
```

---

## Configuration

The server is configured using environment variables.

A reference configuration is provided in `.env.example`.

Common configuration variables include:
- Provider API keys
- Logging level and format
- Feature toggles for specific tools

Example:

```env
LOG_LEVEL=INFO
LOG_JSON=false
```

---

## Development

Development dependencies are listed in `requirements-dev.txt`.

Pre-commit hooks are configured via:

```bash
pre-commit install
```

---

## Testing

The project includes unit and integration tests.

Run all tests:

```bash
pytest
```

---

## MCP Client Integration

The server uses stdio transport and is compatible with MCP clients such as Claude Desktop and MCP Inspector.

Configuration examples can be adapted from the project structure and environment variables.

---

## License

See the license file included in the repository.
