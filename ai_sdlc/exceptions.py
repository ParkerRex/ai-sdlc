"""Custom exceptions for ai-sdlc CLI."""

from __future__ import annotations


class AisdlcError(Exception):
    """Base exception for all ai-sdlc errors."""

    exit_code: int = 1

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class ConfigError(AisdlcError):
    """Configuration-related errors (.aisdlc not found, corrupted, etc.)."""

    pass


class ConfigNotFoundError(ConfigError):
    """Raised when .aisdlc config file is not found."""

    def __init__(self) -> None:
        super().__init__(
            "Config file .aisdlc not found. "
            "Ensure you are in an ai-sdlc project directory.\n"
            "Run `aisdlc init` to initialize a new project."
        )


class ConfigCorruptedError(ConfigError):
    """Raised when .aisdlc config file is corrupted."""

    def __init__(self, details: str) -> None:
        super().__init__(
            f"Config file .aisdlc is corrupted: {details}\n"
            "Please fix the file or run `aisdlc init` in a new directory."
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
