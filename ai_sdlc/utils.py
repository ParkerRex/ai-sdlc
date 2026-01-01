"""Shared helpers."""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

from .constants import CONFIG_FILE, LOCK_FILE
from .exceptions import (
    ConfigCorruptedError,
    ConfigInvalidError,
    ConfigNotFoundError,
    EmptyStepFileError,
)

_root_cache: Path | None = None


def get_root() -> Path:
    """Get project root lazily, caching result after first call."""
    global _root_cache
    if _root_cache is None:
        _root_cache = _find_project_root()
    return _root_cache


def _find_project_root() -> Path:
    """Find project root by searching for config file in current and parent directories."""
    current_dir = Path.cwd()
    for parent in [current_dir] + list(current_dir.parents):
        if (parent / CONFIG_FILE).exists():
            return parent
    return current_dir


def reset_root(path: Path | None = None) -> None:
    """Reset root cache. For testing or when changing directories."""
    global _root_cache
    _root_cache = path


# Required config keys and their expected types
_REQUIRED_CONFIG = {
    "steps": list,
    "active_dir": str,
    "prompt_dir": str,
    "done_dir": str,
}


def _validate_config(config: dict[str, Any]) -> None:
    """Validate that config has all required keys with correct types.

    Raises:
        ConfigInvalidError: If required keys are missing or have wrong types.
    """
    errors: list[str] = []

    for key, expected_type in _REQUIRED_CONFIG.items():
        if key not in config:
            errors.append(f"Missing required key '{key}'")
        elif not isinstance(config[key], expected_type):
            actual_type = type(config[key]).__name__
            errors.append(
                f"Key '{key}' must be {expected_type.__name__}, got {actual_type}"
            )

    # Additional validation for steps
    if "steps" in config and isinstance(config["steps"], list):
        if len(config["steps"]) == 0:
            errors.append("'steps' must contain at least one step")
        elif not all(isinstance(s, str) for s in config["steps"]):
            errors.append("'steps' must be a list of strings")

    if errors:
        raise ConfigInvalidError(errors)


def load_config() -> dict[str, Any]:
    """Load and parse the .aisdlc configuration file.

    Raises:
        ConfigNotFoundError: If .aisdlc file doesn't exist.
        ConfigCorruptedError: If .aisdlc file contains invalid JSON.
        ConfigInvalidError: If required keys are missing or have wrong types.
    """
    cfg_path = get_root() / CONFIG_FILE
    if not cfg_path.exists():
        raise ConfigNotFoundError()
    try:
        config = json.loads(cfg_path.read_text())
    except json.JSONDecodeError as e:
        raise ConfigCorruptedError(str(e)) from e

    _validate_config(config)
    return config


def slugify(text: str) -> str:
    """Convert text to kebab-case ASCII slug."""
    slug = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", slug).strip("-").lower()
    return slug or "idea"


def read_lock() -> dict[str, Any]:
    """Read the lock file.

    Returns an empty dict if the file doesn't exist or is corrupted.
    Corrupted lock files log a warning but don't raise exceptions.
    """
    path = get_root() / LOCK_FILE
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())  # type: ignore[no-any-return]
    except json.JSONDecodeError:
        # Lock file corruption is recoverable - just treat as empty
        print(
            f"Warning: {LOCK_FILE} is corrupted. Treating as empty.",
            file=sys.stderr,
        )
        return {}


def write_lock(data: dict[str, Any]) -> None:
    """Write data to the lock file."""
    (get_root() / LOCK_FILE).write_text(json.dumps(data, indent=2))


def render_step_bar(steps: list[str], current_index: int) -> str:
    """Render a step progress bar showing completed and pending steps.

    Args:
        steps: List of step names (e.g., ["0.idea", "1.design", "2.build"])
        current_index: Index of the current step (steps up to and including this are marked done)

    Returns:
        A formatted string like "done idea > done design > pending build"
    """
    return " > ".join(
        ("[x]" if i <= current_index else "[ ]") + s.split(".", 1)[1]
        for i, s in enumerate(steps)
    )


def validate_step_file(path: Path) -> None:
    """Validate that a step file has content.

    Raises:
        EmptyStepFileError: If the file is empty or whitespace-only.
    """
    content = path.read_text()
    if not content.strip():
        raise EmptyStepFileError(str(path))
