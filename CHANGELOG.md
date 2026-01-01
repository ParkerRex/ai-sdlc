# Changelog

All notable changes to the `ai-sdlc` project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### 🔧 Technical Improvements

- **Proper CLI argument parsing**: Replaced manual `sys.argv` parsing with `argparse` using subparsers
  - Each command now has its own `--help` with detailed descriptions
  - `aisdlc --help` shows all available commands
  - `aisdlc <command> --help` shows command-specific help
  - Foundation for adding future flags like `--verbose`, `--force`, or `--template`
- **Dynamic prompt file discovery**: Removed hardcoded `PROMPT_FILE_NAMES` list
  - Prompt files are now automatically discovered from `scaffold_template/prompts/`
  - Adding new prompt files no longer requires updating code
  - Eliminates sync issues between code and scaffold template
- **Unified step naming convention**: Config steps now use dot format (`0.idea`, `1.prd`) matching prompt filenames, eliminating fragile string parsing scattered across multiple files and making the mapping between config and files explicit and consistent.
- **Improved project root detection**: Refactored `ROOT` constant to `get_root()` function
  - Lazy evaluation with caching for better performance
  - `reset_root()` API for testing without monkey-patching

## [0.6.3] - 2025-01-20

### 🔄 File Naming Convention Update

**Breaking Changes:**

- **Updated file naming**: Prompt files now use `.instructions.md` extension with new naming pattern
  - Changed from `{number}-{name}.prompt.yml` to `{number}.{name}.instructions.md`
  - All 8 prompt files renamed: `0.idea.instructions.md`, `1.prd.instructions.md`, `2.prd-plus.instructions.md`, etc.
  - Maintains tool-agnostic approach while using consistent markdown-style naming convention

### 🔧 Technical Improvements

- **Updated all references**: Comprehensive update of all file references throughout the codebase
  - Updated `ai_sdlc/commands/init.py` and `ai_sdlc/commands/next.py`
  - Updated integration tests to expect new file names
  - Updated CI/CD workflows to test new file names
- **Cross-reference fixes**: Updated internal prompt file references
  - Fixed references in `4.systems-patterns.instructions.md` to `3.system-template.instructions.md`
  - Fixed references in `7.tests.instructions.md` to `5.tasks.instructions.md`
- **Configuration updates**: Updated step names in scaffold template configuration
  - Updated `.aisdlc` configuration to use new step naming pattern
  - Updated Mermaid diagrams to reflect new naming convention

### 📚 Documentation Updates

- **Updated README**: File structure documentation now shows `.instructions.md` extensions
- **Updated CHANGELOG**: Migration guide references updated to new naming convention
- **Updated CI/CD documentation**: GitHub Actions workflows updated for new file names

### 📦 Migration Guide

Existing projects will continue to work, but to use the new naming convention:

1. **Rename prompt files**: Change `.prompt.yml` to `.instructions.md` for all prompt files
2. **Update file naming pattern**: Change from `{number}-{name}` to `{number}.{name}` format
3. **Update any custom references**: If you have custom scripts referencing these files, update the extensions and naming pattern

### 🎯 Benefits

- **Consistent naming**: Unified `{number}.{name}.instructions.md` pattern throughout the system
- **Tool compatibility**: Maintains compatibility with all AI tools and development environments
- **Future-ready**: Scalable naming convention for additional prompt files
- **Better organization**: Clearer file structure with consistent dot notation

## [0.6.2] - 2025-01-20

### 🔧 Test Fixes

- **Fixed failing tests**: Corrected test assertions to match actual implementation behavior
  - Fixed `test_run_init` to expect `mkdir(exist_ok=True)` instead of `mkdir(parents=True, exist_ok=True)`
  - Fixed `test_load_config_missing` to expect `SystemExit` instead of `FileNotFoundError`
  - Fixed `test_run_init` to mock `write_text` instead of non-existent `write_lock` function
- **Release workflow**: All tests now pass, enabling successful PyPI publishing

## [0.6.1] - 2025-01-20

### 🔧 CI/CD Fixes

- **Fixed GitHub environment requirement**: Commented out environment requirement in release workflow to avoid validation errors
- **Updated PyPI setup documentation**: Added notes about optional environment configuration
- **Workflow improvements**: Release workflow can now run without pre-existing GitHub environment

### 📚 Documentation Updates

- **Enhanced PyPI setup guide**: Clarified optional nature of GitHub environments
- **Workflow troubleshooting**: Added guidance for environment setup

## [0.6.0] - 2025-01-20

### 🔄 File Naming Convention Update

**Breaking Changes:**

- **Updated file naming**: Prompt files now use `.instructions.md` extension instead of `.prompt.yml`
  - All 8 prompt files renamed: `0.idea.instructions.md`, `1.prd.instructions.md`, etc.
  - Maintains tool-agnostic approach while using markdown-style naming convention

### 🔧 Technical Improvements

- **Updated all references**: Comprehensive update of all file references throughout the codebase
  - Updated `ai_sdlc/commands/init.py` and `ai_sdlc/commands/next.py`
  - Updated package data patterns in `pyproject.toml`
  - Updated integration tests to expect new file names
- **Cross-reference fixes**: Updated internal prompt file references
  - Fixed references in `4.systems-patterns.instructions.md` to `3.system-template.instructions.md`
  - Fixed references in `7.tests.instructions.md` to `5.tasks.instructions.md`

### 📚 Documentation Updates

- **Updated README**: File structure documentation now shows `.instructions.md` extensions
- **Updated CHANGELOG**: Migration guide references updated to new naming convention

### 📦 Migration Guide

Existing projects will continue to work, but to use the new naming convention:

1. **Rename prompt files**: Change `.prompt.yml` to `.instructions.md` for all prompt files
2. **Update any custom references**: If you have custom scripts referencing these files, update the extensions

### 🎯 Benefits

- **Consistent naming**: Aligns with YAML-style naming conventions while maintaining Markdown content
- **Tool compatibility**: Maintains compatibility with all AI tools and development environments
- **Future-ready**: Prepares for potential YAML frontmatter enhancements

## [0.5.0] - 2025-06-02

### 🎯 Major: Tool-Agnostic AI Integration

**Breaking Changes:**

- **Removed Cursor dependency**: AI-SDLC no longer requires Cursor or any specific AI tool
- **New prompt-based workflow**: `aisdlc next` now generates prompt files instead of calling AI agents directly
- **Updated file naming**: Prompt files now use `.instructions.md` extension (e.g., `0.idea.instructions.md`)
- **Simplified step names**: Steps now use single digits with dot separators (e.g., `0.idea`, `1.prd`) instead of zero-padded numbers

### ✨ New Features

- **Universal AI compatibility**: Works with any AI tool (Claude, ChatGPT, Cursor, Copilot, etc.)
- **Flexible workflow**: Users can choose between CLI automation or manual prompt usage
- **Improved user experience**: Clear instructions for using generated prompts with any AI assistant
- **Better error handling**: More informative messages when files are missing or corrupted

### 🔧 Technical Improvements

- **Broader Python support**: Now supports Python 3.11+ (previously required 3.13+)
- **Cleaner codebase**: Removed all tool-specific dependencies and references
- **Updated documentation**: Comprehensive guide for using AI-SDLC with any AI tool
- **Enhanced testing**: Updated test suite to work with the new tool-agnostic approach

### 📚 Documentation Updates

- **Tool-agnostic README**: Updated all documentation to remove Cursor-specific instructions
- **Flexible usage guide**: Added examples for using AI-SDLC with different AI tools
- **Simplified troubleshooting**: Removed tool-specific troubleshooting steps

### 🗑️ Removed

- **Cursor-specific files**: Removed `.cursor/` directory and Cursor configuration files
- **Repomix integration**: Removed Repomix-related files and references
- **Hardcoded AI agent calls**: Replaced with flexible prompt generation system

### 📦 Migration Guide

Existing projects will continue to work, but to take advantage of the new features:

1. **Update prompt files**: Rename your prompt files to use the new `.instructions.md` convention
2. **Update step references**: Change step names from `01-idea` to `0.idea` format in any custom scripts
3. **Choose your AI tool**: Use the generated prompts with your preferred AI assistant

### 🎉 Benefits

- **No vendor lock-in**: Use any AI tool you prefer
- **Easier setup**: No need to install or configure specific AI tools
- **Better compatibility**: Works across different development environments
- **Future-proof**: Adaptable to new AI tools and services as they emerge

## [0.4.0] - 2025-01-03

### 🚀 Major Features

- **8-step workflow**: Added new `07-tasks-plus` step for comprehensive task list review and handoff preparation
  - Inserted between existing `06-tasks` and `07-tests` (now `08-tests`)
  - Ensures implementation-ready documentation with complete context
  - Includes verification criteria for self-contained documentation
- **Tool-agnostic architecture**: Removed all Cursor-specific references and made AI-SDLC work with any AI tool
  - Updated all documentation, code, and configuration files
  - Supports any AI chat interface (Cursor, Claude, ChatGPT, VS Code with AI extensions, etc.)
  - Flexible usage: full CLI workflow OR prompts-only approach

### 📖 Documentation & UX Improvements

- **Enhanced README**: Complete restructure with professional appearance
  - Added badges for PyPI, license, Python version, and AI-powered status
  - Removed GIF placeholder and improved visual hierarchy
  - Added comprehensive table of contents with emoji icons and logical grouping
  - Enhanced "What is AI-SDLC?" section with key features and benefits
  - Improved Quick Start with numbered steps and clear instructions
  - Added workflow modes table and flexible usage options
- **Updated Mermaid diagrams**: Show iteration loops and agent modes
  - Steps 1-5: Connected to "💬 Iterate with AI Chat" node
  - Steps 7-8: Connected to "🤖 Use AI Agent Mode" node
  - Visual representation of different interaction patterns

### 🛠️ Developer Experience

- **Flexible usage options**:
  - **Option 1**: Full CLI workflow with `aisdlc` commands
  - **Option 2**: Prompts-only approach using templates directly with any AI chat
  - Clear instructions for both approaches
- **Simplified contributing**: Removed CLA requirement from contributing guidelines
- **Enhanced error messages**: Made all error messages tool-agnostic
- **Updated configuration**: All `.aisdlc` files include new workflow diagrams

### 🔧 Technical Changes

- Updated all prompt file references to include new `07-tasks-plus-prompt.md`
- Renamed `07-tests.md` to `08-tests-prompt.md` throughout codebase
- Updated step count references from 7 to 8 steps
- Modified `ai_sdlc/commands/init.py` to include new prompt file
- Updated integration tests to handle 8-step workflow
- Changed timeout variable names and messages to be tool-agnostic

### 📦 Backward Compatibility

- **Fully backward compatible**: Existing projects continue to work
- **Automatic migration**: System dynamically reads step configuration
- **No breaking changes**: All existing commands and workflows preserved

### Upgrading

To upgrade to version 0.4.0, use:

```bash
uv pip install --upgrade ai-sdlc
```

No configuration changes are needed - all improvements are backward compatible with existing AI-SDLC projects.

## [0.3.0] - 2025-01-15

### Overview

Version 0.3.0 brings significant improvements to error handling, security, and overall robustness of the tool. This release also introduces a comprehensive testing framework to ensure stability as the project evolves.

### Added

- **Comprehensive testing framework with pytest**
  - Basic test structure with fixtures and helpers
  - Unit tests for utility functions and commands
  - Integration tests for the CLI workflow
- **Enhanced error handling and robustness**
  - Detailed error messages for AI agent failures including stdout/stderr
  - Timeout handling for AI agent calls (45 second default)
  - Comprehensive file I/O error handling in all commands
  - Lock file corruption handling (gracefully handles invalid JSON)
  - Config file corruption handling (shows helpful error for invalid TOML)
- **Enhanced `aisdlc init` command**
  - Now scaffolds a default `.aisdlc` configuration file into the new project
  - Automatically creates a `prompts/` directory populated with default prompt templates for all SDLC steps
  - Displays a comprehensive and styled welcome message upon initialization, including:
    - An ASCII art logo for "AI-SDLC"
    - A brief explanation of how AI-SDLC works
    - A guide on understanding the compact status bar shown after commands
    - Quick "Getting Started" instructions for the main workflow (`new`, `next`, `done`)
- **Packaged default configuration and templates**
  - Default `.aisdlc` configuration and all prompt templates within the `ai-sdlc` distribution
  - Ensures `init` can robustly scaffold new projects

### Changed

- **Improved temporary file handling in `next` command**
  - Replaced hardcoded `/tmp/aisdlc_prompt.md` with secure `tempfile.NamedTemporaryFile`
  - Added proper cleanup in `finally` block to prevent leaks
- **Enhanced `next` command with verbose output**
  - Added informative messages about reading files, creating temporary files
  - Shows progress indicators at each step
- **Improved project root detection**
  - New `find_project_root()` function that searches upward for `.aisdlc` file
  - Allows running commands from subdirectories of the project

### Security

- **Secure temporary file management**
  - Implemented secure temporary file handling with proper permissions
  - Automatic file cleanup to prevent leaking sensitive prompt data

### Developer Improvements

- Added pytest, pytest-mock, ruff, and pyright to dev dependencies
- Improved documentation for development setup and testing

### Upgrading

To upgrade to version 0.3.0, use:

```bash
uv pip install --upgrade ai-sdlc
```

No configuration changes are needed - all improvements are backward compatible with existing AI-SDLC projects.

### Known Issues

- AI-SDLC continues to require Python 3.11 or newer

## [0.2.0] - 2025-05-17

- Python 3.13 support
- UV-first installation
- Streamlined lifecycle (removed release planning/retro steps)

## [0.1.0] - Initial Release

- Initial version with basic SDLC workflow
- Support for the initial lifecycle
- Integration with AI agents
