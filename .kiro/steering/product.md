# Product Overview

**Outdoor Intelligence MCP Server** is a production-grade Model Context Protocol (MCP) server providing decision-support for outdoor activities.

## Core Capabilities

- **Location Discovery**: Search POIs, trails, and parks using OpenStreetMap Overpass
- **Location Profiles**: Deep profiles with nearby features and characteristics
- **Real-Time Conditions**: Weather data and alerts via OpenWeather API
- **Risk Assessment**: Deterministic risk scoring (0-100) with evidence, breakdown, and recommendations

## Key Design Principles

- **Structured JSON Contract**: All tools return consistent `{ok, data, provenance, cache, warnings}` format
- **Explainable & Deterministic**: Risk scores are reproducible with clear evidence trails
- **Offline-Friendly Testing**: Demo fallback mode when API keys unavailable
- **Reviewer-Friendly**: Explicit uncertainties, provenance tracking, and conservative defaults
- **Production-Ready**: Async I/O, TTL caching, rate limiting, structured logging

## Target Users

- LLM applications (Claude Desktop compatible)
- Human reviewers and AI evaluators
- Outdoor activity planning systems
