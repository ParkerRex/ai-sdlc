"""Unit tests for `aisdlc done` command."""

import json
from pathlib import Path

import pytest

from ai_sdlc import utils
from ai_sdlc.commands.done import run_done
from ai_sdlc.exceptions import (
    FileWriteError,
    MissingStepFilesError,
    NoActiveWorkstreamError,
    WorkstreamNotFinishedError,
)


@pytest.fixture
def setup_project(temp_project_dir: Path):
    """Set up a project with config and directories."""
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

    utils.reset_root(temp_project_dir)
    yield temp_project_dir
    utils.reset_root(None)


def test_done_no_active_workstream(setup_project: Path):
    """Test done command with no active workstream."""
    (setup_project / ".aisdlc.lock").write_text("{}")

    with pytest.raises(NoActiveWorkstreamError) as exc_info:
        run_done()

    assert "No active workstream" in str(exc_info.value)


def test_done_workstream_not_finished(setup_project: Path):
    """Test done command when workstream is not on last step."""
    lock_data = {"slug": "test-idea", "current": "1.prd"}  # Not last step
    (setup_project / ".aisdlc.lock").write_text(json.dumps(lock_data))

    with pytest.raises(WorkstreamNotFinishedError) as exc_info:
        run_done()

    assert "not finished" in str(exc_info.value)


def test_done_missing_step_files(setup_project: Path):
    """Test done command when some step files are missing."""
    slug = "test-idea"
    workdir = setup_project / "doing" / slug
    workdir.mkdir(parents=True)

    # Create only first step file
    (workdir / "0.idea-test-idea.md").write_text("# Idea")
    # Missing: 1.prd-test-idea.md, 2.prd-plus-test-idea.md

    lock_data = {"slug": slug, "current": "2.prd-plus"}  # Last step
    (setup_project / ".aisdlc.lock").write_text(json.dumps(lock_data))

    with pytest.raises(MissingStepFilesError) as exc_info:
        run_done()

    assert "1.prd" in str(exc_info.value)
    assert "2.prd-plus" in str(exc_info.value)


def test_done_archives_successfully(setup_project: Path, capsys):
    """Test successful archive of completed workstream."""
    slug = "test-idea"
    workdir = setup_project / "doing" / slug
    workdir.mkdir(parents=True)

    # Create all step files
    (workdir / "0.idea-test-idea.md").write_text("# Idea")
    (workdir / "1.prd-test-idea.md").write_text("# PRD")
    (workdir / "2.prd-plus-test-idea.md").write_text("# PRD Plus")

    lock_data = {"slug": slug, "current": "2.prd-plus"}
    (setup_project / ".aisdlc.lock").write_text(json.dumps(lock_data))

    run_done()

    # Check workdir moved to done
    assert not workdir.exists()
    done_dir = setup_project / "done" / slug
    assert done_dir.exists()
    assert (done_dir / "0.idea-test-idea.md").exists()
    assert (done_dir / "1.prd-test-idea.md").exists()
    assert (done_dir / "2.prd-plus-test-idea.md").exists()

    # Check lock was cleared
    new_lock = utils.read_lock()
    assert new_lock == {}

    captured = capsys.readouterr()
    assert "Archived to" in captured.out


def test_done_with_extra_files(setup_project: Path, capsys):
    """Test that extra files in workdir are also archived."""
    slug = "test-idea"
    workdir = setup_project / "doing" / slug
    workdir.mkdir(parents=True)

    # Create all step files
    (workdir / "0.idea-test-idea.md").write_text("# Idea")
    (workdir / "1.prd-test-idea.md").write_text("# PRD")
    (workdir / "2.prd-plus-test-idea.md").write_text("# PRD Plus")

    # Create extra file
    (workdir / "notes.md").write_text("# Notes")

    lock_data = {"slug": slug, "current": "2.prd-plus"}
    (setup_project / ".aisdlc.lock").write_text(json.dumps(lock_data))

    run_done()

    # Check extra file was also moved
    done_dir = setup_project / "done" / slug
    assert (done_dir / "notes.md").exists()


def test_done_destination_conflict(setup_project: Path):
    """Test done command when destination has conflicting files."""
    slug = "test-idea"
    workdir = setup_project / "doing" / slug
    workdir.mkdir(parents=True)

    # Create all step files
    (workdir / "0.idea-test-idea.md").write_text("# Idea")
    (workdir / "1.prd-test-idea.md").write_text("# PRD")
    (workdir / "2.prd-plus-test-idea.md").write_text("# PRD Plus")

    # Create destination with conflicting nested structure
    dest = setup_project / "done" / slug / slug
    dest.mkdir(parents=True)

    lock_data = {"slug": slug, "current": "2.prd-plus"}
    (setup_project / ".aisdlc.lock").write_text(json.dumps(lock_data))

    with pytest.raises(FileWriteError):
        run_done()
