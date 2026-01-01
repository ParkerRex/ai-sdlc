# AI-SDLC

**Markdown-driven software development lifecycle powered by AI agents**

[![PyPI version](https://img.shields.io/pypi/v/ai-sdlc.svg)](https://pypi.org/project/ai-sdlc/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/ParkerRex/ai-sdlc/blob/main/LICENSE)
[![Python version](https://img.shields.io/badge/python-3.13+-blue.svg)](https://python.org)

```bash
uv pip install ai-sdlc
```

<p align="center">
  <img src="./.github/assets/github.png" alt="AI-SDLC GitHub" width="600">
</p>

## What is AI-SDLC?

AI-SDLC is a CLI tool that guides software development through an 8-step structured workflow. It generates markdown files and AI prompts that help you go from an initial idea to production-ready code with comprehensive tests.

The tool is **AI-agnostic**—it generates prompts you can use with any AI assistant (Claude, ChatGPT, Cursor, etc.). No API keys or specific AI tools required.

### The Problem

Developers often jump straight to coding, skipping important planning steps. This leads to:
- Unclear requirements discovered mid-implementation
- Architecture decisions made ad-hoc
- Missing test coverage
- Poor documentation of decisions

### The Solution

AI-SDLC enforces a structured workflow:
1. Document decisions and rationale in version-controlled markdown
2. Generate comprehensive implementation plans before coding
3. Create thorough test strategies
4. Maintain project history

## Quick Start

### 1. Install

```bash
# Install uv (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install AI-SDLC
uv pip install ai-sdlc
```

### 2. Initialize

```bash
mkdir my-project && cd my-project
aisdlc init
```

### 3. Start a Feature

```bash
aisdlc new "Add user authentication system"
aisdlc status
```

### 4. Work Through the Steps

1. Fill out the generated markdown in `doing/add-user-authentication-system/0.idea-*.md`
2. Run `aisdlc next` to generate a prompt for the next step
3. Use the prompt with your AI tool and save the response
4. Repeat until all 8 steps complete
5. Archive with `aisdlc done`

## The 8-Step Workflow

```
0.idea → 1.prd → 2.prd-plus → 3.system-template → 4.systems-patterns → 5.tasks → 6.tasks-plus → 7.tests
```

| Step | Name | Purpose |
|------|------|---------|
| 01 | idea | Initial problem statement and strategic pitch |
| 02 | prd | Product requirements document |
| 03 | prd-plus | Enhanced requirements with edge cases |
| 04 | architecture | System architecture design |
| 05 | system-patterns | Design patterns and implementation strategy |
| 06 | tasks | Task breakdown and implementation plan |
| 07 | tasks-plus | Task review and handoff preparation |
| 08 | tests | Test plan and test code generation |

### Workflow Modes

| Mode | Steps | Description |
|------|-------|-------------|
| Chat Mode | 1-5 | Iterate with AI chat to refine ideas, requirements, and architecture |
| Manual Mode | 6 | Fill out task list markdown directly |
| Agent Mode | 7-8 | Automated processing for task review and test generation |

## Commands

| Command | Description |
|---------|-------------|
| `aisdlc init` | Initialize AI-SDLC in current directory |
| `aisdlc new <idea>` | Start new feature with idea description |
| `aisdlc next` | Generate prompt for next step |
| `aisdlc status` | Show current project status |
| `aisdlc done` | Archive completed feature to done/ |
| `aisdlc --help` | Show help |

## How It Works

When you run `aisdlc next`:

1. Reads the previous step's markdown file
2. Merges content into the prompt template for the next step
3. Writes the merged prompt to `_prompt-<step>.md`
4. You copy the prompt to your AI tool, get a response, and save it

All state is tracked in files:
- `.aisdlc` - Project configuration (TOML)
- `.aisdlc.lock` - Current workflow state (JSON)
- `doing/<slug>/` - Active feature files
- `done/<slug>/` - Completed features

## Project Structure

```
.
├── ai_sdlc/                # Main Python package
│   ├── cli.py              # Entry point for aisdlc command
│   ├── commands/           # Command implementations (init, new, next, status, done)
│   ├── scaffold_template/  # Default templates for new projects
│   └── utils.py            # Shared helpers
├── prompts/                # LLM prompt templates for each step
├── tests/                  # Test suite
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── doing/                  # Active features (created by init)
├── done/                   # Completed features (created by init)
├── .aisdlc                 # Project configuration
└── .aisdlc.lock            # Current workflow state
```

## Installation

### Prerequisites

- Python 3.13+
- uv (recommended) or pip

### Install Options

```bash
# Using uv (recommended)
uv pip install ai-sdlc

# Using pip
pip install ai-sdlc

# Verify installation
aisdlc --help
```

## Development Setup

```bash
git clone https://github.com/ParkerRex/ai-sdlc.git
cd ai-sdlc
uv venv && source .venv/bin/activate
uv sync --all-features
```

### Running Tests

```bash
uv pip install -e .[dev]

# Lint and format
uv run ruff check ai_sdlc tests
uv run ruff format ai_sdlc tests

# Type check
uv run pyright

# Run tests
uv run pytest
uv run pytest tests/unit/        # Unit tests only
uv run pytest tests/integration/ # Integration tests only
```

## Technology Stack

| Component | Technology |
|-----------|------------|
| CLI | Python 3.13+, argparse (stdlib) |
| Package manager | uv |
| Dev tools | Ruff, Pyright, pytest |
| Build | setuptools, PEP 621 |

Runtime has zero external dependencies—uses only Python standard library.

## Troubleshooting

**"Permission denied" errors**
- Check file permissions in your project directory

**"Invalid .aisdlc configuration"**
- Verify `.aisdlc` has valid TOML syntax
- Run `aisdlc init` to regenerate defaults

**"Lock file corruption"**
- Delete `.aisdlc.lock` and run `aisdlc status`

## Contributing

1. Fork and clone the repository
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Make changes with tests
4. Run quality checks: `ruff check`, `pyright`, `pytest`
5. Open a PR

## Roadmap

- Pluggable AI providers (`--model` flag for GPT-4, Claude, Gemini)
- 09-release-plan step for CI/CD and deployment
- Context-window management for large projects
- Template customization per project
- Parallel workflows for multiple features

## License

MIT - See [LICENSE](LICENSE) for details.
