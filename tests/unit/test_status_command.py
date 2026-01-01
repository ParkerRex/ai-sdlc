"""Unit tests for `aisdlc status` command."""

import json
from pathlib import Path

import pytest

from ai_sdlc import utils
from ai_sdlc.commands.status import run_status


@pytest.fixture
def setup_project(temp_project_dir: Path):
    """Set up a project with config."""
    config_data = {
        "version": "0.1.0",
        "steps": ["0.idea", "1.prd", "2.prd-plus"],
        "prompt_dir": "prompts",
        "active_dir": "doing",
        "done_dir": "done",
    }
    (temp_project_dir / ".aisdlc").write_text(json.dumps(config_data))

    utils.reset_root(temp_project_dir)
    yield temp_project_dir
    utils.reset_root(None)


def test_status_no_active_workstream(setup_project: Path, capsys):
    """Test status command with no active workstream."""
    (setup_project / ".aisdlc.lock").write_text("{}")

    run_status()

    captured = capsys.readouterr()
    assert "Active workstreams" in captured.out
    assert "none" in captured.out
    assert "aisdlc new" in captured.out


def test_status_shows_current_step(setup_project: Path, capsys):
    """Test status command shows current workstream and step."""
    lock_data = {"slug": "my-feature", "current": "1.prd"}
    (setup_project / ".aisdlc.lock").write_text(json.dumps(lock_data))

    run_status()

    captured = capsys.readouterr()
    assert "Active workstreams" in captured.out
    assert "my-feature" in captured.out
    assert "1.prd" in captured.out


def test_status_shows_progress_bar(setup_project: Path, capsys):
    """Test status command shows progress bar with completed/pending steps."""
    lock_data = {"slug": "my-feature", "current": "1.prd"}
    (setup_project / ".aisdlc.lock").write_text(json.dumps(lock_data))

    run_status()

    captured = capsys.readouterr()
    # First two steps should be complete (index 0, 1)
    assert "[x]idea" in captured.out
    assert "[x]prd" in captured.out
    # Third step should be pending
    assert "[ ]prd-plus" in captured.out


def test_status_first_step(setup_project: Path, capsys):
    """Test status when on first step."""
    lock_data = {"slug": "new-idea", "current": "0.idea"}
    (setup_project / ".aisdlc.lock").write_text(json.dumps(lock_data))

    run_status()

    captured = capsys.readouterr()
    assert "[x]idea" in captured.out
    assert "[ ]prd" in captured.out
    assert "[ ]prd-plus" in captured.out


def test_status_last_step(setup_project: Path, capsys):
    """Test status when on last step."""
    lock_data = {"slug": "finished-feature", "current": "2.prd-plus"}
    (setup_project / ".aisdlc.lock").write_text(json.dumps(lock_data))

    run_status()

    captured = capsys.readouterr()
    # All steps should be complete
    assert "[x]idea" in captured.out
    assert "[x]prd" in captured.out
    assert "[x]prd-plus" in captured.out


def test_status_progress_bar_format(setup_project: Path, capsys):
    """Test that progress bar uses correct separator."""
    lock_data = {"slug": "test", "current": "0.idea"}
    (setup_project / ".aisdlc.lock").write_text(json.dumps(lock_data))

    run_status()

    captured = capsys.readouterr()
    # Check separator is used
    assert ">" in captured.out
