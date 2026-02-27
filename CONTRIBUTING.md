# Contributing to TealFlowMCP

Thank you for your interest in contributing to TealFlowMCP! This document provides guidelines for contributing to the project.

## Branching Strategy

We use a simple two-branch workflow:

- **`main`**: Stable releases only. Protected branch requiring PR approval.
- **`develop`**: Active development branch. All feature work is merged here.

```
feature/xyz → develop → main
```

## Development Workflow

### 1. Create a Feature Branch

Always create your feature branch from `develop`:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
```

Branch naming conventions:
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `chore/description` - Maintenance tasks

### 2. Make Your Changes

- Write clear, concise code following the project's style
- Add tests for new functionality
- Update documentation as needed
- Keep commits focused and atomic

### 3. Commit Your Changes

Use clear, descriptive commit messages. We encourage (but don't enforce) [Conventional Commits](https://www.conventionalcommits.org/) format:

```
feat(tools): Add new dataset discovery options
fix(server): Resolve startup timeout issue
docs(readme): Update installation instructions
test(discovery): Add tests for edge cases
chore(deps): Update pytest to 8.0.0
```

Common prefixes:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `test:` - Test additions or modifications
- `chore:` - Maintenance tasks
- `refactor:` - Code refactoring
- `perf:` - Performance improvements

### 4. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a PR targeting the `develop` branch on GitHub.

#### PR Guidelines:
- Provide a clear title and description
- Reference any related issues
- Ensure all CI checks pass
- Request review from maintainers

### 5. After Merge

Once your PR is merged to `develop`, you can delete your feature branch:

```bash
git checkout develop
git pull origin develop
git branch -d feature/your-feature-name
```

## Release Process

Releases are managed by maintainers:

1. When ready for a release, create a PR from `develop` to `main`
2. Update version numbers (see Version Management below)
3. Update CHANGELOG.md with release notes
4. After merge to `main`, create and push a git tag

### Version Management

**Manual version updates are required in two files:**

1. **`tealflow_mcp/__init__.py`**:
   ```python
   __version__ = "X.Y.Z"
   ```

2. **`pyproject.toml`**:
   ```toml
   [project]
   version = "X.Y.Z"
   ```

**Version Format** (following [Semantic Versioning](https://semver.org/)):

- **On `develop` branch**: Use development versions
  - Format: `X.Y.Z.devN` (e.g., `0.2.0.dev1`, `0.2.0.dev2`)
  - Increment the dev number with each significant change on develop

- **On `main` branch**: Use release versions
  - Format: `X.Y.Z` (e.g., `0.2.0`, `1.0.0`)
  - Major.Minor.Patch versioning

- **Hotfixes on `main`**: Use post-release versions
  - Format: `X.Y.Z.postN` (e.g., `0.2.0.post1`)

**When to bump versions:**

- **Patch** (0.0.X): Bug fixes and minor changes
- **Minor** (0.X.0): New features, backwards-compatible
- **Major** (X.0.0): Breaking changes

**Important**: Always keep both files in sync! When bumping version, update both files in the same commit.

### CHANGELOG.md

Update the changelog following [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format:

```markdown
## [Unreleased]

### Added
- New features

### Changed
- Changes to existing functionality

### Fixed
- Bug fixes

### Removed
- Removed features
```

Before release, move unreleased changes under the new version heading.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- R (for running Shiny apps)
- UV package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/Appsilon/TealFlowMCP.git
cd TealFlowMCP

# Switch to develop branch
git checkout develop

# Install dependencies
uv sync
```

### Running Tests

```bash
# Run all tests
uv run python -m pytest tests/ -v

# Run with coverage
uv run python -m pytest tests/ --cov=tealflow_mcp --cov-report=term-missing -v

# Run specific test file
uv run python -m pytest tests/test_discovery.py -v
```

### Code Quality Checks

```bash
# Linting
uv run ruff check tealflow_mcp/ tests/

# Auto-fix linting issues
uv run ruff check tealflow_mcp/ tests/ --fix

# Format code
uv run ruff format tealflow_mcp/ tests/

# Type checking
uv run mypy tealflow_mcp/

# Run all checks (same as CI)
uv run ruff check tealflow_mcp/ tests/ && \
uv run ruff format tealflow_mcp/ tests/ --check && \
uv run mypy tealflow_mcp/ && \
uv run python -m pytest tests/ -v
```

## Code Style

- Follow PEP 8 guidelines (enforced by Ruff)
- Maximum line length: 100 characters
- Use type hints where practical
- Write descriptive docstrings for public functions and classes
- Keep functions focused and modular

## Testing Guidelines

- Write tests for all new functionality
- Maintain or improve code coverage
- Use descriptive test names that explain what is being tested
- Follow the Arrange-Act-Assert pattern
- Mock external dependencies appropriately

## Documentation

- Update README.md for user-facing changes
- Update CLAUDE.md for development workflow changes
- Add docstrings to new functions and classes
- Update CHANGELOG.md with your changes

## Questions or Issues?

- Open an issue on GitHub for bug reports or feature requests
- Join discussions in existing issues
- Reach out to maintainers for guidance

## License

By contributing to TealFlowMCP, you agree that your contributions will be licensed under the AGPL-3.0 license.

---

Thank you for contributing to TealFlowMCP! 🚀
