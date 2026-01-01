"""`aisdlc done` – validate finished stream and archive it."""

import shutil

from ai_sdlc.exceptions import (
    FileWriteError,
    MissingStepFilesError,
    NoActiveWorkstreamError,
    WorkstreamNotFinishedError,
)
from ai_sdlc.utils import get_root, load_config, read_lock, write_lock


def run_done(args: object = None) -> None:
    """Validate and archive a completed workstream.

    Raises:
        NoActiveWorkstreamError: If no workstream is active.
        WorkstreamNotFinishedError: If workstream hasn't completed all steps.
        MissingStepFilesError: If required step files are missing.
        FileWriteError: If archiving fails.
    """
    conf = load_config()
    steps = conf["steps"]
    lock = read_lock()

    if not lock:
        raise NoActiveWorkstreamError()

    slug = lock["slug"]
    if lock["current"] != steps[-1]:
        raise WorkstreamNotFinishedError()

    root = get_root()
    workdir = root / conf["active_dir"] / slug
    missing = [s for s in steps if not (workdir / f"{s}-{slug}.md").exists()]
    if missing:
        raise MissingStepFilesError(missing)

    dest = root / conf["done_dir"] / slug
    if dest.exists():
        raise FileWriteError(
            str(dest), "Destination already exists. Remove or rename it first."
        )

    try:
        shutil.move(str(workdir), dest)
        write_lock({})
        print(f"Archived to {dest}")
    except OSError as e:
        raise FileWriteError(str(dest), str(e)) from e
