#!/usr/bin/env python
"""Entry-point for the `aisdlc` CLI."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from importlib import import_module

from .exceptions import AisdlcError, ConfigError
from .utils import load_config, read_lock, render_step_bar

#: Type alias for command handler functions
CommandHandler = Callable[[argparse.Namespace], None]


def _resolve(dotted: str) -> CommandHandler:
    """Import `"module:function"` and return the function object."""
    module_name, func_name = dotted.split(":")
    module = import_module(module_name)
    func: CommandHandler = getattr(module, func_name)
    return func


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
            bar = render_step_bar(steps, idx)
            print(f"\n---\nCurrent: {slug} @ {current_step_name}\n   {bar}\n---")
        else:
            print(
                f"\n---\nCurrent: {slug} @ {current_step_name} (Step not in config)\n---"
            )
    except ConfigError:
        # Config missing - silently skip status display
        return
    except Exception as exc:
        # Avoid masking unexpected errors while keeping CLI usable.
        print(f"Warning: unable to display status ({exc})", file=sys.stderr)
        return


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

    try:
        handler(args)
    except AisdlcError as e:
        print(f"Error: {e.message}", file=sys.stderr)
        sys.exit(e.exit_code)

    # Display status after most commands, unless it's status itself or init (before lock exists)
    if args.command not in ["status", "init"]:
        _display_compact_status()


if __name__ == "__main__":
    main()
