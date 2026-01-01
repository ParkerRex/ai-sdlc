from pathlib import Path

from ai_sdlc.commands import init


def test_run_init(temp_project_dir: Path, mocker):
    # Mock Path.cwd() to return our temp directory
    mocker.patch.object(Path, "cwd", return_value=temp_project_dir)

    # Mock any directory operations to prevent actual file system changes
    mocker.patch.object(Path, "mkdir")

    # Mock file writing operations
    mock_write_text = mocker.patch.object(Path, "write_text")

    init.run_init()

    # Verify directories would have been created (the actual code calls mkdir(exist_ok=True))
    Path.mkdir.assert_any_call(exist_ok=True)

    # Verify lock file would have been written (the actual code writes JSON directly)
    mock_write_text.assert_any_call("{}")  # Empty JSON object
