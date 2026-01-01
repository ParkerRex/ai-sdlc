# ai_sdlc/commands/init.py
"""`aisdlc init` – scaffold baseline folders, config, prompts & lock."""

import importlib.resources as pkg_resources
import sys
from pathlib import Path

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

  📌 Current: your-feature-slug @ 0X-step-name
     ✅idea ▸ ✅prd ▸ ☐prd-plus ▸ ☐architecture ▸ ...

*   This shows your currently active feature, the current step you're on, and your overall progress.
*   '✅' indicates a completed step.
*   '☐' indicates a pending step.
*   The part after '@' (e.g., '0X-step-name') is the code for the current step.
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


def _discover_prompt_files(prompt_dir) -> list[str]:
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


def run_init(args: object = None) -> None:
    """Scaffold AI-SDLC project: .aisdlc, prompts/, doing/, done/, .aisdlc.lock and print instructions."""
    print("Initializing AI-SDLC project...")

    # Use current working directory for init (since .aisdlc doesn't exist yet)
    init_root = Path.cwd()

    try:
        scaffold_dir = pkg_resources.files("ai_sdlc").joinpath("scaffold_template")
        default_config_content = scaffold_dir.joinpath(".aisdlc").read_text()
        prompt_files_source_dir = scaffold_dir.joinpath("prompts")
        prompt_file_names = _discover_prompt_files(prompt_files_source_dir)
        if not prompt_file_names:
            print(
                "⚠️ Warning: No prompt templates found in the ai-sdlc package scaffold."
            )
    except Exception as e:
        print(
            f"❌ Critical Error: Could not load scaffold templates from the ai-sdlc package: {e}"
        )
        print("   This might indicate a broken installation.")
        print(
            "   Please try reinstalling ai-sdlc: `uv pip install --force-reinstall ai-sdlc`"
        )
        print(
            "   If the issue persists, please report it on the project's issue tracker."
        )
        sys.exit(1)

    # Create directories
    prompts_target_dir = init_root / "prompts"
    prompts_target_dir.mkdir(exist_ok=True)
    (init_root / "doing").mkdir(exist_ok=True)
    (init_root / "done").mkdir(exist_ok=True)
    print(
        f"📂 Created/ensured directories: {prompts_target_dir.relative_to(Path.cwd())}, doing/, done/"
    )

    # Write .aisdlc config file
    config_target_path = init_root / ".aisdlc"
    if not config_target_path.exists():
        try:
            config_target_path.write_text(default_config_content)
            print(
                f"📄 Created default config: {config_target_path.relative_to(Path.cwd())}"
            )
        except OSError as e:
            print(f"❌ Error writing config file {config_target_path}: {e}")
            sys.exit(1)
    else:
        print(
            f"📄 Config file {config_target_path.relative_to(Path.cwd())} already exists, skipping creation."
        )

    # Copy prompt templates
    print("✨ Setting up prompt templates...")
    all_prompts_exist = True
    for fname in prompt_file_names:
        target_file = prompts_target_dir / fname
        if not target_file.exists():
            try:
                content = prompt_files_source_dir.joinpath(fname).read_text()
                target_file.write_text(content)
                print(f"  - Created prompt: {target_file.relative_to(Path.cwd())}")
            except FileNotFoundError:
                print(
                    f"  ⚠️ Warning: Packaged prompt template for '{fname}' not found within ai-sdlc package. Please create it manually in '{prompts_target_dir}'."
                )
                all_prompts_exist = False
            except OSError as e:
                print(f"  ❌ Error creating prompt '{fname}': {e}")
                all_prompts_exist = False
        else:
            # To avoid too much noise, only print if it was skipped.
            # print(f"  - Prompt {target_file.relative_to(Path.cwd())} already exists, skipping.")
            pass
    if all_prompts_exist and all(
        (prompts_target_dir / fname).exists() for fname in prompt_file_names
    ):
        print(
            f"  👍 All prompt templates are set up in {prompts_target_dir.relative_to(Path.cwd())}."
        )
    else:
        print(
            f"  ℹ️ Some prompt templates might be missing or could not be created. Check {prompts_target_dir.relative_to(Path.cwd())}."
        )

    # Create lock file
    try:
        import json

        lock_file_path = init_root / ".aisdlc.lock"
        lock_file_path.write_text(json.dumps({}))
        print(f"🔒 Created empty lock file: {lock_file_path.relative_to(Path.cwd())}")
    except OSError as e:
        print(f"❌ Error writing lock file: {e}")
        sys.exit(1)

    # Print instructions
    print(ASCII_ART)
    print(WELCOME_MESSAGE)
    print(HOW_IT_WORKS)
    print(STATUS_BAR_EXPLANATION)
    print(GETTING_STARTED_GUIDE)

    print("\n✅  AI-SDLC initialized successfully! Your project is ready.")
    print(
        f"   Run `aisdlc new \"Your first feature idea\"` from '{Path.cwd()}' to get started."
    )
