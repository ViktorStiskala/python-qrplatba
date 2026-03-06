# Contributing

## Prerequisites

- Python 3.9+
- [uv](https://docs.astral.sh/uv/)

## Setup

Clone the repository and install dependencies:

```bash
git clone https://github.com/ViktorStiskala/python-qrplatba.git
cd python-qrplatba
uv sync
```

### Pre-commit hooks

Pre-commit hooks run linting and formatting checks before each commit. Install them with:

```bash
uv tool install pre-commit
pre-commit install
```

## Running tests

```bash
uv run pytest
```

## Linting

Linting and formatting are enforced via [ruff](https://docs.astral.sh/ruff/). To run manually:

```bash
uv run ruff check .
uv run ruff format --check .
```

Or run all checks at once through pre-commit:

```bash
uvx pre-commit run --all-files
```
