"""`aisdlc next` – generate the next lifecycle file via AI agent."""

from __future__ import annotations

import argparse

from ai_sdlc.constants import PREV_STEP_PLACEHOLDER
from ai_sdlc.exceptions import (
    MissingFileError,
    NoActiveWorkstreamError,
)
from ai_sdlc.utils import (
    get_root,
    load_config,
    read_lock,
    validate_step_file,
    write_lock,
)


def run_next(args: argparse.Namespace | None = None) -> None:
    """Generate the prompt for the next lifecycle step.

    Raises:
        NoActiveWorkstreamError: If no workstream is active.
        MissingFileError: If required files are missing.
        EmptyStepFileError: If step file exists but is empty.
    """
    conf = load_config()
    steps = conf["steps"]
    lock = read_lock()

    if not lock:
        raise NoActiveWorkstreamError()

    slug = lock["slug"]
    idx = steps.index(lock["current"])
    if idx + 1 >= len(steps):
        print("All steps complete. Run `aisdlc done` to archive.")
        return

    prev_step = steps[idx]
    next_step = steps[idx + 1]

    root = get_root()
    workdir = root / conf["active_dir"] / slug
    prev_file = workdir / f"{prev_step}-{slug}.md"
    prompt_file = root / conf["prompt_dir"] / f"{next_step}.instructions.md"
    next_file = workdir / f"{next_step}-{slug}.md"

    if not prev_file.exists():
        raise MissingFileError(
            str(prev_file),
            f"This file is required to generate the '{next_step}' step.\n"
            "Restore it from version control or recreate the previous step.",
        )
    if not prompt_file.exists():
        raise MissingFileError(
            str(prompt_file),
            f"This prompt template is essential for the '{next_step}' step.\n"
            f"Ensure it exists in '{conf['prompt_dir']}/' or run `aisdlc init`.",
        )

    print(f"Reading previous step from: {prev_file}")
    prev_step_content = prev_file.read_text()
    print(f"Reading prompt template from: {prompt_file}")
    prompt_template_content = prompt_file.read_text()

    merged_prompt = prompt_template_content.replace(
        PREV_STEP_PLACEHOLDER, prev_step_content
    )

    # Create a prompt file for the user to use with their preferred AI tool
    prompt_output_file = workdir / f"_prompt-{next_step}.md"
    prompt_output_file.write_text(merged_prompt)

    print(f"Generated AI prompt file: {prompt_output_file}")
    print(
        f"Use this prompt with your preferred AI tool to generate content for step '{next_step}'"
    )
    print(f"Then save the AI's response to: {next_file}")
    print()
    print("Options:")
    print(
        "  - Copy the prompt content and paste into any AI chat (Claude, ChatGPT, etc.)"
    )
    print("  - Use with Cursor: cursor agent --file " + str(prompt_output_file))
    print("  - Use with any other AI-powered editor or CLI tool")
    print()
    print(f"After saving the AI response, the next step file should be: {next_file}")
    print("Once ready, run 'aisdlc next' again to continue to the next step.")

    # Check if the user has already created the next step file
    if next_file.exists():
        # Validate file has content before advancing
        validate_step_file(next_file)

        print(f"Found existing file: {next_file}")
        print("Proceeding to update the workflow state...")

        # Update the lock to reflect the current step
        lock["current"] = next_step
        write_lock(lock)
        print(f"Advanced to step: {next_step}")

        # Clean up the prompt file since it's no longer needed
        if prompt_output_file.exists():
            prompt_output_file.unlink()
            print(f"Cleaned up prompt file: {prompt_output_file}")
    else:
        print(f"Waiting for you to create: {next_file}")
        print(
            "Use the generated prompt with your AI tool, then run 'aisdlc next' again."
        )
