#!/usr/bin/env python
"""Entry-point for the `aisdlc` CLI."""

from __future__ import annotations

import argparse
import sys
from importlib import import_module
from typing import TYPE_CHECKING

from .utils import load_config, read_lock

if TYPE_CHECKING:
    from collections.abc import Callable


def _resolve(dotted: str) -> Callable[..., None]:
    """Import `"module:function"` and return the function object."""
    module_name, func_name = dotted.split(":")
    module = import_module(module_name)
    return getattr(module, func_name)  # type: ignore[no-any-return]


def _display_compact_status() -> None:
    """Displays a compact version of the current workstream status."""
    lock = read_lock()
    if not lock or "slug" not in lock:
        return  # No active workstream or invalid lock

    try:
        conf = load_config()
        steps = conf["steps"]
        slug = lock.get("slug", "N/A")
        current_step_name = lock.get("current", "N/A")

        if current_step_name in steps:
            idx = steps.index(current_step_name)
            # Steps are in format like "0.idea", take the part after the dot
            bar = " ▸ ".join(
                [
                    ("✅" if i <= idx else "☐") + s.split(".", 1)[1]
                    for i, s in enumerate(steps)
                ]
            )
            print(f"\n---\n📌 Current: {slug} @ {current_step_name}\n   {bar}\n---")
        else:
            print(
                f"\n---\n📌 Current: {slug} @ {current_step_name} (Step not in config)\n---"
            )
    except FileNotFoundError:  # .aisdlc missing
        print(
            "\n---\n📌 AI-SDLC config (.aisdlc) not found. Cannot display status.\n---"
        )
    except Exception:  # Catch other potential errors during status display
        print(
            "\n---\n📌 Could not display current status due to an unexpected issue.\n---"
        )


def _create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="aisdlc",
        description="AI-SDLC: A structured software development lifecycle tool with AI assistance.",
        epilog="Run 'aisdlc <command> --help' for more information on a specific command.",
    )

    subparsers = parser.add_subparsers(
        title="commands",
        dest="command",
        metavar="<command>",
    )

    # init command
    init_parser = subparsers.add_parser(
        "init",
        help="Initialize a new AI-SDLC project",
        description="Scaffold baseline folders, config, prompts & lock file for a new AI-SDLC project.",
    )
    init_parser.set_defaults(handler="ai_sdlc.commands.init:run_init")

    # new command
    new_parser = subparsers.add_parser(
        "new",
        help="Start a new workstream from an idea",
        description="Create a new workstream folder and first markdown file from an idea title.",
    )
    new_parser.add_argument(
        "title",
        nargs="+",
        help="The title of your idea (can be multiple words)",
    )
    new_parser.set_defaults(handler="ai_sdlc.commands.new:run_new")

    # next command
    next_parser = subparsers.add_parser(
        "next",
        help="Advance to the next lifecycle step",
        description="Generate the next lifecycle file via AI agent prompt.",
    )
    next_parser.set_defaults(handler="ai_sdlc.commands.next:run_next")

    # status command
    status_parser = subparsers.add_parser(
        "status",
        help="Show progress through lifecycle steps",
        description="Display the current workstream status and progress through all steps.",
    )
    status_parser.set_defaults(handler="ai_sdlc.commands.status:run_status")

    # done command
    done_parser = subparsers.add_parser(
        "done",
        help="Archive a completed workstream",
        description="Validate that all steps are complete and archive the workstream.",
    )
    done_parser.set_defaults(handler="ai_sdlc.commands.done:run_done")

    return parser


def main() -> None:  # noqa: D401
    """Run the requested sub-command."""
    parser = _create_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    handler = _resolve(args.handler)
    handler(args)

    # Display status after most commands, unless it's status itself or init (before lock exists)
    if args.command not in ["status", "init"]:
        _display_compact_status()


if __name__ == "__main__":
    main()
