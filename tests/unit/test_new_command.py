"""Unit tests for `aisdlc new` command."""

import argparse
import json
from pathlib import Path

import pytest

from ai_sdlc import utils
from ai_sdlc.commands.new import run_new
from ai_sdlc.exceptions import WorkstreamExistsError


@pytest.fixture
def setup_project(temp_project_dir: Path):
    """Set up a minimal project with .aisdlc config."""
    config_content = json.dumps({
        "version": "0.1.0",
        "steps": ["0.idea", "1.prd", "2.prd-plus"],
        "prompt_dir": "prompts",
        "active_dir": "doing",
        "done_dir": "done"
    })
    (temp_project_dir / ".aisdlc").write_text(config_content)
    (temp_project_dir / "doing").mkdir()
    (temp_project_dir / "done").mkdir()
    utils.reset_root(temp_project_dir)
    yield temp_project_dir
    utils.reset_root(None)


def make_args(title: list[str]) -> argparse.Namespace:
    """Create args namespace for run_new."""
    return argparse.Namespace(title=title)


def test_new_creates_workstream(setup_project: Path, capsys):
    """Test that new command creates workstream folder and files."""
    run_new(make_args(["My", "Test", "Idea"]))

    workdir = setup_project / "doing" / "my-test-idea"
    assert workdir.exists()

    idea_file = workdir / "0.idea-my-test-idea.md"
    assert idea_file.exists()
    content = idea_file.read_text()
    assert "# My Test Idea" in content
    assert "## Problem" in content
    assert "## Solution" in content

    # Check lock file was created
    lock_file = setup_project / ".aisdlc.lock"
    assert lock_file.exists()
    lock_data = utils.read_lock()
    assert lock_data["slug"] == "my-test-idea"
    assert lock_data["current"] == "0.idea"

    captured = capsys.readouterr()
    assert "Created" in captured.out


def test_new_workstream_already_exists(setup_project: Path):
    """Test error when workstream already exists."""
    # Create existing workstream
    (setup_project / "doing" / "existing-idea").mkdir(parents=True)

    with pytest.raises(WorkstreamExistsError) as exc_info:
        run_new(make_args(["Existing", "Idea"]))

    assert "already exists" in str(exc_info.value)


def test_new_slugifies_title(setup_project: Path):
    """Test that titles are properly slugified."""
    run_new(make_args(["Hello", "World!", "Test"]))

    workdir = setup_project / "doing" / "hello-world-test"
    assert workdir.exists()


def test_new_handles_special_characters(setup_project: Path):
    """Test that special characters in title are handled."""
    run_new(make_args(["Test@#$%Feature"]))

    workdir = setup_project / "doing" / "test-feature"
    assert workdir.exists()


def test_new_single_word_title(setup_project: Path):
    """Test new command with single word title."""
    run_new(make_args(["Feature"]))

    workdir = setup_project / "doing" / "feature"
    assert workdir.exists()
    assert (workdir / "0.idea-feature.md").exists()
