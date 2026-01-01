"""Unit tests for `aisdlc next` command."""

import json
from pathlib import Path

import pytest

from ai_sdlc import utils
from ai_sdlc.commands.next import PLACEHOLDER, run_next
from ai_sdlc.exceptions import MissingFileError, NoActiveWorkstreamError


@pytest.fixture
def setup_project(temp_project_dir: Path):
    """Set up a project with config, prompts, and active workstream."""
    config_content = """
version = "0.1.0"
steps = ["0.idea", "1.prd", "2.prd-plus"]
prompt_dir = "prompts"
active_dir = "doing"
done_dir = "done"
"""
    (temp_project_dir / ".aisdlc").write_text(config_content)
    (temp_project_dir / "doing").mkdir()
    (temp_project_dir / "done").mkdir()
    (temp_project_dir / "prompts").mkdir()

    # Create prompt templates
    (temp_project_dir / "prompts" / "1.prd.instructions.md").write_text(
        f"# PRD Template\n\n{PLACEHOLDER}\n\nGenerate a PRD."
    )
    (temp_project_dir / "prompts" / "2.prd-plus.instructions.md").write_text(
        f"# PRD Plus Template\n\n{PLACEHOLDER}\n\nExpand the PRD."
    )

    utils.reset_root(temp_project_dir)
    yield temp_project_dir
    utils.reset_root(None)


def test_next_no_active_workstream(setup_project: Path):
    """Test next command with no active workstream."""
    # Empty lock file
    (setup_project / ".aisdlc.lock").write_text("{}")

    with pytest.raises(NoActiveWorkstreamError) as exc_info:
        run_next()

    assert "No active workstream" in str(exc_info.value)


def test_next_all_steps_complete(setup_project: Path, capsys):
    """Test next command when all steps are already complete."""
    lock_data = {"slug": "test-idea", "current": "2.prd-plus"}  # Last step
    (setup_project / ".aisdlc.lock").write_text(json.dumps(lock_data))

    run_next()

    captured = capsys.readouterr()
    assert "All steps complete" in captured.out


def test_next_generates_prompt_file(setup_project: Path, capsys):
    """Test that next generates a prompt file with merged content."""
    # Set up workstream at step 0
    slug = "test-idea"
    workdir = setup_project / "doing" / slug
    workdir.mkdir(parents=True)

    # Create previous step file
    idea_content = "# Test Idea\n\nThis is my idea."
    (workdir / "0.idea-test-idea.md").write_text(idea_content)

    # Set lock to step 0
    lock_data = {"slug": slug, "current": "0.idea"}
    (setup_project / ".aisdlc.lock").write_text(json.dumps(lock_data))

    run_next()

    # Check prompt file was created
    prompt_file = workdir / "_prompt-1.prd.md"
    assert prompt_file.exists()

    # Check content was merged
    prompt_content = prompt_file.read_text()
    assert "# PRD Template" in prompt_content
    assert idea_content in prompt_content
    assert PLACEHOLDER not in prompt_content

    captured = capsys.readouterr()
    assert "Generated AI prompt file" in captured.out


def test_next_missing_previous_step_file(setup_project: Path):
    """Test next command when previous step file is missing."""
    slug = "test-idea"
    workdir = setup_project / "doing" / slug
    workdir.mkdir(parents=True)
    # Don't create the previous step file

    lock_data = {"slug": slug, "current": "0.idea"}
    (setup_project / ".aisdlc.lock").write_text(json.dumps(lock_data))

    with pytest.raises(MissingFileError) as exc_info:
        run_next()

    assert "missing" in str(exc_info.value).lower()


def test_next_missing_prompt_template(setup_project: Path):
    """Test next command when prompt template is missing."""
    slug = "test-idea"
    workdir = setup_project / "doing" / slug
    workdir.mkdir(parents=True)

    # Create previous step file
    (workdir / "0.idea-test-idea.md").write_text("# Test Idea")

    # Remove prompt template
    (setup_project / "prompts" / "1.prd.instructions.md").unlink()

    lock_data = {"slug": slug, "current": "0.idea"}
    (setup_project / ".aisdlc.lock").write_text(json.dumps(lock_data))

    with pytest.raises(MissingFileError) as exc_info:
        run_next()

    assert "missing" in str(exc_info.value).lower()


def test_next_advances_when_next_file_exists(setup_project: Path, capsys):
    """Test that next advances state when user has created next step file."""
    slug = "test-idea"
    workdir = setup_project / "doing" / slug
    workdir.mkdir(parents=True)

    # Create previous step file
    (workdir / "0.idea-test-idea.md").write_text("# Test Idea")

    # Create next step file (simulating user completing it)
    (workdir / "1.prd-test-idea.md").write_text("# PRD Content")

    lock_data = {"slug": slug, "current": "0.idea"}
    (setup_project / ".aisdlc.lock").write_text(json.dumps(lock_data))

    run_next()

    # Check lock was updated
    new_lock = utils.read_lock()
    assert new_lock["current"] == "1.prd"

    captured = capsys.readouterr()
    assert "Advanced to step" in captured.out


def test_next_cleans_up_prompt_file_after_advance(setup_project: Path):
    """Test that prompt file is deleted after advancing."""
    slug = "test-idea"
    workdir = setup_project / "doing" / slug
    workdir.mkdir(parents=True)

    # Create previous step file
    (workdir / "0.idea-test-idea.md").write_text("# Test Idea")

    # Create next step file
    (workdir / "1.prd-test-idea.md").write_text("# PRD Content")

    # Create prompt file (would exist from previous run)
    prompt_file = workdir / "_prompt-1.prd.md"
    prompt_file.write_text("prompt content")

    lock_data = {"slug": slug, "current": "0.idea"}
    (setup_project / ".aisdlc.lock").write_text(json.dumps(lock_data))

    run_next()

    # Prompt file should be cleaned up
    assert not prompt_file.exists()


def test_next_waits_when_next_file_missing(setup_project: Path, capsys):
    """Test that next waits for user when next step file doesn't exist."""
    slug = "test-idea"
    workdir = setup_project / "doing" / slug
    workdir.mkdir(parents=True)

    # Create previous step file only
    (workdir / "0.idea-test-idea.md").write_text("# Test Idea")

    lock_data = {"slug": slug, "current": "0.idea"}
    (setup_project / ".aisdlc.lock").write_text(json.dumps(lock_data))

    run_next()

    # Lock should NOT be updated
    new_lock = utils.read_lock()
    assert new_lock["current"] == "0.idea"

    captured = capsys.readouterr()
    assert "Waiting for you to create" in captured.out
