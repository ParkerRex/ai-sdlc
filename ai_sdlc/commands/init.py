# ai_sdlc/commands/init.py
"""`aisdlc init` – scaffold baseline folders, config, prompts & lock."""

from __future__ import annotations

import argparse
import importlib.resources as pkg_resources
import json
from pathlib import Path
from typing import TYPE_CHECKING

from ai_sdlc.constants import (
    CONFIG_FILE,
    DEFAULT_ACTIVE_DIR,
    DEFAULT_DONE_DIR,
    DEFAULT_PROMPT_DIR,
    LOCK_FILE,
)
from ai_sdlc.exceptions import FileWriteError, ScaffoldError

if TYPE_CHECKING:
    from importlib.abc import Traversable

ASCII_ART = """
   █████╗ ██╗███████╗██╗  ██╗ ██████╗██╗
  ██╔══██╗██║╚══███╔╝██║  ██║██╔════╝██║
  ███████║██║  ███╔╝ ███████║██║     ██║
  ██╔══██║██║ ███╔╝  ██╔══██║██║     ██║
  ██║  ██║██║███████╗██║  ██║╚██████╗███████╗
  ╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝╚══════╝
"""

WELCOME_MESSAGE = """
Welcome to AI-SDLC!
This tool helps you manage your software development lifecycle with AI assistance.
"""

HOW_IT_WORKS = """
How AI-SDLC Works:
------------------
*   AI-SDLC guides you through a structured 8-step feature development process.
*   Each step generates a Markdown file (e.g., for ideas, PRDs, architecture).
*   The `aisdlc next` command generates prompts for use with any AI tool (Claude, ChatGPT, Cursor, etc.).
*   This keeps your development process organized, documented, and version-controlled.
"""

STATUS_BAR_EXPLANATION = """
Understanding the Status Bar:
-----------------------------
After commands like `new` or `next`, you'll see a compact status update similar to this:

  Current: your-feature-slug @ 0X-step-name
  [done] idea > [done] prd > [ ] prd-plus > [ ] architecture > ...

*   This shows your currently active feature, the current step you're on, and your overall progress.
*   '[done]' indicates a completed step.
*   '[ ]' indicates a pending step.
"""

GETTING_STARTED_GUIDE = """
Getting Started:
----------------
1.  Initialize a new feature:
    `aisdlc new "Your Awesome Feature Title"`

2.  Open and fill in the first Markdown file created in the `doing/your-awesome-feature-title/` directory
    (e.g., `doing/your-awesome-feature-title/0.idea-your-awesome-feature-title.md`).

3.  Advance to the next step (AI-SDLC will generate a prompt for your AI tool):
    `aisdlc next`

4.  Use the generated prompt with your preferred AI tool (Claude, ChatGPT, Cursor, etc.) and save the response.

5.  Repeat steps 3 and 4 until all 8 steps are completed.

6.  Archive your feature:
    `aisdlc done`

7.  Check your progress anytime:
    `aisdlc status`
"""


def _discover_prompt_files(prompt_dir: Traversable) -> list[str]:
    """Discover all .instructions.md files from the scaffold template prompts directory."""
    prompt_files = []
    try:
        for item in prompt_dir.iterdir():
            name = item.name
            if name.endswith(".instructions.md"):
                prompt_files.append(name)
    except (TypeError, AttributeError):
        # Fallback for older Python or different resource types
        pass
    return sorted(prompt_files)


def run_init(args: argparse.Namespace | None = None) -> None:
    """Scaffold AI-SDLC project: .aisdlc, prompts/, doing/, done/, .aisdlc.lock.

    Raises:
        ScaffoldError: If scaffold templates cannot be loaded.
        FileWriteError: If files cannot be created.
    """
    print("Initializing AI-SDLC project...")

    # Use current working directory for init (since .aisdlc doesn't exist yet)
    init_root = Path.cwd()

    try:
        scaffold_dir = pkg_resources.files("ai_sdlc").joinpath("scaffold_template")
        default_config_content = scaffold_dir.joinpath(CONFIG_FILE).read_text()
        prompt_files_source_dir = scaffold_dir.joinpath("prompts")
        prompt_file_names = _discover_prompt_files(prompt_files_source_dir)
        if not prompt_file_names:
            print("Warning: No prompt templates found in the ai-sdlc package scaffold.")
    except Exception as e:
        raise ScaffoldError(str(e)) from e

    # Create directories
    prompts_target_dir = init_root / DEFAULT_PROMPT_DIR
    prompts_target_dir.mkdir(exist_ok=True)
    (init_root / DEFAULT_ACTIVE_DIR).mkdir(exist_ok=True)
    (init_root / DEFAULT_DONE_DIR).mkdir(exist_ok=True)
    print(
        f"Created directories: {prompts_target_dir.relative_to(Path.cwd())}, "
        f"{DEFAULT_ACTIVE_DIR}/, {DEFAULT_DONE_DIR}/"
    )

    # Write config file
    config_target_path = init_root / CONFIG_FILE
    if not config_target_path.exists():
        try:
            config_target_path.write_text(default_config_content)
            print(f"Created config: {config_target_path.relative_to(Path.cwd())}")
        except OSError as e:
            raise FileWriteError(str(config_target_path), str(e)) from e
    else:
        print(
            f"Config {config_target_path.relative_to(Path.cwd())} already exists, skipping."
        )

    # Copy prompt templates
    print("Setting up prompt templates...")
    all_prompts_exist = True
    for fname in prompt_file_names:
        target_file = prompts_target_dir / fname
        if not target_file.exists():
            try:
                content = prompt_files_source_dir.joinpath(fname).read_text()
                target_file.write_text(content)
                print(f"  Created: {target_file.relative_to(Path.cwd())}")
            except FileNotFoundError:
                print(f"  Warning: Template '{fname}' not found in package.")
                all_prompts_exist = False
            except OSError as e:
                print(f"  Warning: Could not create '{fname}': {e}")
                all_prompts_exist = False

    if all_prompts_exist and prompt_file_names:
        print(
            f"All prompt templates set up in {prompts_target_dir.relative_to(Path.cwd())}."
        )
    elif prompt_file_names:
        print(
            f"Some templates missing. Check {prompts_target_dir.relative_to(Path.cwd())}."
        )

    # Create lock file
    try:
        lock_file_path = init_root / LOCK_FILE
        lock_file_path.write_text(json.dumps({}))
        print(f"Created lock file: {lock_file_path.relative_to(Path.cwd())}")
    except OSError as e:
        raise FileWriteError(str(lock_file_path), str(e)) from e

    # Print instructions
    print(ASCII_ART)
    print(WELCOME_MESSAGE)
    print(HOW_IT_WORKS)
    print(STATUS_BAR_EXPLANATION)
    print(GETTING_STARTED_GUIDE)

    print("\nAI-SDLC initialized successfully! Your project is ready.")
    print(
        f"Run `aisdlc new \"Your first feature idea\"` from '{Path.cwd()}' to get started."
    )
