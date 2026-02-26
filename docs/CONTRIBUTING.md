# Contributing to KaliVibe

Thank you for your interest in contributing to KaliVibe! This document provides guidelines and instructions for contributing.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)

---

## Code of Conduct

Be respectful, inclusive, and constructive. We're all here to build something useful for the security community.

---

## Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/KaliVibe.git
   cd KaliVibe
   ```
3. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

---

## Development Setup

```bash
# Install dependencies
uv sync

# Set up your environment
cp .env.example .env
# Edit .env with your OpenAI API key

# Run the agent to test
uv run python -m src.main
```

### Running Tests

```bash
# Lint check
uv run ruff check src/

# Format check
uv run ruff format --check src/

# Auto-format
uv run ruff format src/
```

---

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/AimanMadan/KaliVibe/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Your environment (Python version, OS, etc.)

### Suggesting Features

1. Open an issue with the `enhancement` label
2. Describe the feature and why it would be useful
3. Include examples if possible

### Submitting Code

1. Fork → Branch → Code → Test → Push → PR
2. Follow the coding standards below
3. Write clear commit messages
4. Update documentation if needed

---

## Coding Standards

We use **Ruff** for linting and formatting. Key rules:

### Python Style

- **Line length:** 88 characters (Black default)
- **Quotes:** Double quotes for strings, single for f-strings when needed
- **Imports:** Sorted with `isort` (handled by Ruff)
- **Type hints:** Encouraged for function signatures

### Code Organization

```python
# Good: Clear function with type hints and docstring
def resolve_path(filepath: str) -> str:
    """Resolve a filepath relative to the current bash directory.
    
    Args:
        filepath: Absolute or relative path to resolve.
        
    Returns:
        The absolute path.
    """
    ...
```

### Documentation

- Update `README.md` for user-facing changes
- Add docstrings to new functions/classes
- Update `docs/` for architectural changes

---

## Commit Guidelines

We follow conventional commits:

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Code style (formatting, etc.) |
| `refactor` | Code refactoring |
| `test` | Adding/updating tests |
| `chore` | Maintenance tasks |

**Examples:**
```
feat: add timeout configuration for commands
fix: handle EOF error in bash session
docs: update architecture diagram
```

---

## Pull Request Process

1. **Create a descriptive PR title** following commit conventions
2. **Link related issues** in the description
3. **Ensure all checks pass** (linting, formatting)
4. **Update documentation** if your changes affect users
5. **Request review** from maintainers

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How was this tested?

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Commit messages follow conventions
```

---

## Questions?

Open an issue or reach out to [@AimanMadan](https://github.com/AimanMadan).

Thank you for contributing! 🎉
