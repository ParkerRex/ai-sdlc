"""Shared helpers."""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

from .exceptions import ConfigCorruptedError, ConfigNotFoundError

_root_cache: Path | None = None


def get_root() -> Path:
    """Get project root lazily, caching result after first call."""
    global _root_cache
    if _root_cache is None:
        _root_cache = _find_project_root()
    return _root_cache


def _find_project_root() -> Path:
    """Find project root by searching for .aisdlc file in current and parent directories."""
    current_dir = Path.cwd()
    for parent in [current_dir] + list(current_dir.parents):
        if (parent / ".aisdlc").exists():
            return parent
    return current_dir


def reset_root(path: Path | None = None) -> None:
    """Reset root cache. For testing or when changing directories."""
    global _root_cache
    _root_cache = path


# --- TOML loader (Python >=3.11 stdlib) --------------------------------------
try:
    import tomllib as _toml  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover - fallback for < 3.11
    import tomli as _toml  # type: ignore[import-not-found,no-redef]


def load_config() -> dict[str, Any]:
    """Load and parse the .aisdlc configuration file.

    Raises:
        ConfigNotFoundError: If .aisdlc file doesn't exist.
        ConfigCorruptedError: If .aisdlc file contains invalid TOML.
    """
    cfg_path = get_root() / ".aisdlc"
    if not cfg_path.exists():
        raise ConfigNotFoundError()
    try:
        return _toml.loads(cfg_path.read_text())
    except _toml.TOMLDecodeError as e:
        raise ConfigCorruptedError(str(e)) from e


def slugify(text: str) -> str:
    """Convert text to kebab-case ASCII slug."""
    slug = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", slug).strip("-").lower()
    return slug or "idea"


def read_lock() -> dict[str, Any]:
    """Read the .aisdlc.lock file.

    Returns an empty dict if the file doesn't exist or is corrupted.
    Corrupted lock files log a warning but don't raise exceptions.
    """
    path = get_root() / ".aisdlc.lock"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())  # type: ignore[no-any-return]
    except json.JSONDecodeError:
        # Lock file corruption is recoverable - just treat as empty
        print(
            "Warning: .aisdlc.lock is corrupted. Treating as empty.",
            file=sys.stderr,
        )
        return {}


def write_lock(data: dict[str, Any]) -> None:
    """Write data to the .aisdlc.lock file."""
    (get_root() / ".aisdlc.lock").write_text(json.dumps(data, indent=2))


def render_step_bar(steps: list[str], current_index: int) -> str:
    """Render a step progress bar showing completed and pending steps.

    Args:
        steps: List of step names (e.g., ["0.idea", "1.design", "2.build"])
        current_index: Index of the current step (steps up to and including this are marked done)

    Returns:
        A formatted string like "done idea > done design > pending build"
    """
    return " ▸ ".join(
        ("✅" if i <= current_index else "☐") + s.split(".", 1)[1]
        for i, s in enumerate(steps)
    )
