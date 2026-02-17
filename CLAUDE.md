# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python CLI tool for managing Qualtrics mailing lists via REST API. Supports scheduling and sending surveys via SMS or email, with timezone-aware scheduling and time slot ranges.

**Python version:** 3.11

## Common Commands

```bash
# Install dependencies
make install-deps

# Run all tests
make test                    # or: python -m pytest tests/ -v

# Run a single test file
python -m pytest tests/test_utils/test_datetime_utils.py -v

# Build executable (PyInstaller)
make build

# Clean build artifacts
make clean

# Install as editable package
make install
```

## Architecture

The codebase has a **dual implementation**:

1. **Monolithic** (`qualtrics_util.py`) — Single 75KB file used by PyInstaller builds via `standalone_main.py`
2. **Modular** (`src/qualtrics_util/`) — Refactored version with proper separation of concerns, still under development

Current PyInstaller builds use the monolithic version. The modular version does not yet implement all commands (send, delete, update are incomplete).

### Modular Structure (`src/qualtrics_util/`)

- **`cli.py`** — CLI argument parsing, command dispatch (`check`, `list`, `slist`, `send`, `delete`, `export`, `update`)
- **`config.py`** — `ConfigLoader` class: YAML config loading, `.env` parsing, dot-notation key access, IANA timezone validation with file line number error reporting
- **`api/base.py`** — `BaseQualtricsClient`: auth via `x-api-token` header, request handling, automatic pagination via `get_paginated()`
- **`api/contacts.py`** — `ContactsAPI`: get/update contacts, lookup IDs
- **`api/distributions.py`** — `DistributionsAPI`: create/delete SMS and email distributions
- **`api/messages.py`** — `MessagesAPI`: message template access
- **`api/surveys.py`** — `SurveysAPI`: survey data export
- **`models/embedded_data.py`** — Flat/nested dict conversion, field access helpers, send eligibility checks
- **`utils/datetime_utils.py`** — Time slot parsing (single: `800`, ranges: `[800,900]`), timezone conversion, ISO formatting
- **`services/scheduler.py`** — Time slot scheduling with timezone conversion
- **`services/exporter.py`** — Survey data export

### API Client Inheritance

All API classes (`ContactsAPI`, `DistributionsAPI`, `MessagesAPI`, `SurveysAPI`) inherit from `BaseQualtricsClient` which provides auth, pagination, and error handling via `QualtricsAPIError`.

## Configuration

The tool requires two input files:

1. **`.env`** — Contains `QUALTRICS_APITOKEN=<token>`
2. **`config_qualtrics.yaml`** — YAML config specifying survey, mailing list, message IDs, timezone, and embedded data defaults. Alternative config files via `--config` flag.

Key config sections: `account` (data center, directory, library), `project` (survey/message/mailing list IDs, timezone), `embedded_data` (default contact fields including TimeSlots and ContactMethod).

## Conventions

- Commit messages use conventional format: `type(scope): description`
- Tests follow AAA pattern (Arrange, Act, Assert) with pytest
- TDD approach preferred
