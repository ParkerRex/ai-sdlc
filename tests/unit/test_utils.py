import json
from pathlib import Path

import pytest

from ai_sdlc import utils
from ai_sdlc.exceptions import ConfigCorruptedError, ConfigNotFoundError


def test_slugify():
    assert utils.slugify("Hello World!") == "hello-world"
    assert utils.slugify("  Test Slug with Spaces  ") == "test-slug-with-spaces"
    assert utils.slugify("Special!@#Chars") == "special-chars"
    assert utils.slugify("") == "idea"  # As per current implementation


def test_load_config_success(temp_project_dir: Path):
    mock_aisdlc_content = json.dumps({
        "version": "0.1.0",
        "steps": ["0.idea", "1.prd"],
        "prompt_dir": "prompts",
        "active_dir": "doing",
        "done_dir": "done"
    })
    aisdlc_file = temp_project_dir / ".aisdlc"
    aisdlc_file.write_text(mock_aisdlc_content)

    utils.reset_root(temp_project_dir)
    try:
        config = utils.load_config()
        assert config["version"] == "0.1.0"
        assert config["steps"] == ["0.idea", "1.prd"]
    finally:
        utils.reset_root(None)


def test_load_config_missing(temp_project_dir: Path):
    utils.reset_root(temp_project_dir)
    try:
        with pytest.raises(ConfigNotFoundError):
            utils.load_config()
    finally:
        utils.reset_root(None)


def test_load_config_corrupted(temp_project_dir: Path):
    aisdlc_file = temp_project_dir / ".aisdlc"
    aisdlc_file.write_text("this is not valid json {")  # Corrupted JSON

    utils.reset_root(temp_project_dir)
    try:
        with pytest.raises(ConfigCorruptedError):
            utils.load_config()
    finally:
        utils.reset_root(None)


def test_read_write_lock(temp_project_dir: Path):
    utils.reset_root(temp_project_dir)
    try:
        lock_data = {"slug": "test-slug", "current": "0.idea"}

        # Test write_lock
        utils.write_lock(lock_data)
        lock_file = temp_project_dir / ".aisdlc.lock"
        assert lock_file.exists()
        assert json.loads(lock_file.read_text()) == lock_data

        # Test read_lock
        read_data = utils.read_lock()
        assert read_data == lock_data

        # Test read_lock when file doesn't exist
        lock_file.unlink()
        assert utils.read_lock() == {}

        # Test read_lock with corrupted JSON
        lock_file.write_text("not json {")
        assert utils.read_lock() == {}  # Should return empty dict on corruption
    finally:
        utils.reset_root(None)
