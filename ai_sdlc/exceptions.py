"""Custom exceptions for ai-sdlc CLI."""

from __future__ import annotations

from ai_sdlc.constants import CONFIG_FILE


class AisdlcError(Exception):
    """Base exception for all ai-sdlc errors."""

    exit_code: int = 1

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class ConfigError(AisdlcError):
    """Configuration-related errors (config not found, corrupted, etc.)."""

    pass


class ConfigNotFoundError(ConfigError):
    """Raised when config file is not found."""

    def __init__(self) -> None:
        super().__init__(
            f"Config file {CONFIG_FILE} not found. "
            "Ensure you are in an ai-sdlc project directory.\n"
            "Run `aisdlc init` to initialize a new project."
        )


class ConfigCorruptedError(ConfigError):
    """Raised when config file is corrupted."""

    def __init__(self, details: str) -> None:
        super().__init__(
            f"Config file {CONFIG_FILE} is corrupted: {details}\n"
            "Please fix the file or run `aisdlc init` in a new directory."
        )


class ConfigInvalidError(ConfigError):
    """Raised when config is missing required keys or has invalid types."""

    def __init__(self, errors: list[str]) -> None:
        error_list = "\n  - ".join(errors)
        super().__init__(
            f"Config file {CONFIG_FILE} is invalid:\n  - {error_list}\n"
            "Please fix the file or run `aisdlc init` to create a valid config."
        )


class WorkstreamError(AisdlcError):
    """Workstream-related errors."""

    pass


class NoActiveWorkstreamError(WorkstreamError):
    """Raised when no active workstream exists."""

    def __init__(self) -> None:
        super().__init__("No active workstream. Run `aisdlc new` first.")


class WorkstreamExistsError(WorkstreamError):
    """Raised when trying to create a workstream that already exists."""

    def __init__(self, slug: str) -> None:
        super().__init__(f"Workstream '{slug}' already exists.")


class WorkstreamNotFinishedError(WorkstreamError):
    """Raised when trying to archive an unfinished workstream."""

    def __init__(self) -> None:
        super().__init__(
            "Workstream not finished yet. Complete all steps before archiving."
        )


class FileError(AisdlcError):
    """File-related errors."""

    pass


class MissingFileError(FileError):
    """Raised when a required file is missing."""

    def __init__(self, path: str, hint: str | None = None) -> None:
        message = f"Required file is missing: {path}"
        if hint:
            message += f"\n{hint}"
        super().__init__(message)


class MissingStepFilesError(FileError):
    """Raised when step files are missing for archiving."""

    def __init__(self, missing: list[str]) -> None:
        super().__init__(f"Missing step files: {', '.join(missing)}")


class EmptyStepFileError(FileError):
    """Raised when a step file exists but is empty."""

    def __init__(self, path: str) -> None:
        super().__init__(
            f"Step file is empty: {path}\n"
            "Please add content before advancing to the next step."
        )


class FileWriteError(FileError):
    """Raised when a file cannot be written."""

    def __init__(self, path: str, details: str) -> None:
        super().__init__(f"Cannot write file '{path}': {details}")


class ScaffoldError(AisdlcError):
    """Errors during project scaffolding (init command)."""

    def __init__(self, details: str) -> None:
        super().__init__(
            f"Failed to load scaffold templates: {details}\n"
            "This might indicate a broken installation.\n"
            "Try reinstalling: `uv pip install --force-reinstall ai-sdlc`"
        )
