"""`aisdlc new` – start a work-stream from an idea title."""

from __future__ import annotations

import argparse
import datetime

from ai_sdlc.exceptions import FileWriteError, WorkstreamExistsError
from ai_sdlc.utils import get_root, load_config, slugify, write_lock


def run_new(args: argparse.Namespace) -> None:
    """Create the work-stream folder and first markdown file.

    Raises:
        WorkstreamExistsError: If a workstream with this slug already exists.
        FileWriteError: If files cannot be created.
    """
    config = load_config()
    first_step = config["steps"][0]

    idea_text = " ".join(args.title)
    slug = slugify(idea_text)

    workdir = get_root() / config["active_dir"] / slug
    if workdir.exists():
        raise WorkstreamExistsError(slug)

    try:
        workdir.mkdir(parents=True)
        idea_file = workdir / f"{first_step}-{slug}.md"
        idea_file.write_text(
            f"# {idea_text}\n\n## Problem\n\n## Solution\n\n## Rabbit Holes\n",
        )

        write_lock(
            {
                "slug": slug,
                "current": first_step,
                "created": datetime.datetime.now(datetime.UTC).isoformat(),
            },
        )
        print(f"Created {idea_file}. Fill it out, then run `aisdlc next`.")
    except OSError as e:
        raise FileWriteError(str(workdir), str(e)) from e
