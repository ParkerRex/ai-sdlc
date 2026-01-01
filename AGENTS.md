# Agents

## Project Overview
- ai-sdlc is a Python CLI package built with Hatchling and managed via uv.
- Primary entry point: `aisdlc` in `ai_sdlc/cli.py`.

## Local Workflow
- Install deps: `uv sync --all-extras --dev`
- Tests: `uv run pytest tests/ -v`
- Integration tests: `uv run pytest tests/integration/ -v`
- Lint: `uv run ruff check .`
- Format check: `uv run ruff format --check .`
- Type check: `uv run mypy ai_sdlc`

## Release Workflow
- Version lives in `pyproject.toml` and `CHANGELOG.md`.
- Tag-based releases: push a tag like `v0.7.0` to trigger `.github/workflows/release.yml`.
- Build artifacts are uploaded from `dist/` and published to PyPI via trusted publishing.

## CI Notes
- CI is in `.github/workflows/ci.yml`.
- Security checks include Bandit and Safety. Avoid silent `except Exception: pass` blocks.
