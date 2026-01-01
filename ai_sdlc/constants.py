"""Centralized constants for ai-sdlc CLI."""

# Configuration file names
CONFIG_FILE = ".aisdlc"
LOCK_FILE = ".aisdlc.lock"

# Default directory names (used during init and as fallbacks)
DEFAULT_ACTIVE_DIR = "doing"
DEFAULT_DONE_DIR = "done"
DEFAULT_PROMPT_DIR = "prompts"

# Prompt template placeholder for injecting previous step content
PREV_STEP_PLACEHOLDER = "<prev_step></prev_step>"
