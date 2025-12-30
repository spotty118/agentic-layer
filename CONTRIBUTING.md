# Contributing to Agentic Layer

Thank you for your interest in contributing to Agentic Layer! This document provides guidelines for contributing to the project.

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/agentic-layer.git
cd agentic-layer
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e ".[dev]"
```

4. Set up your OpenAI API key:
```bash
export OPENAI_API_KEY='your-api-key'
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agentic_layer

# Run specific test file
pytest tests/test_config.py

# Run specific test
pytest tests/test_config.py::TestConfig::test_default_config
```

## Code Style

We follow PEP 8 style guidelines. Before submitting:

```bash
# Format code
black agentic_layer/ tests/

# Check style
flake8 agentic_layer/ tests/

# Type checking
mypy agentic_layer/
```

## Project Structure

```
agentic-layer/
├── agentic_layer/          # Main package
│   ├── __init__.py         # Package initialization
│   ├── cli.py              # CLI interface
│   ├── orchestrator.py     # Core orchestration logic
│   ├── config.py           # Configuration management
│   ├── validators.py       # Validation utilities
│   └── logger.py           # Logging and output
├── tests/                  # Test suite
│   ├── test_config.py
│   ├── test_validators.py
│   └── test_logger.py
├── setup.py                # Package setup
├── README.md               # Main documentation
├── EXAMPLES.md             # Usage examples
└── CONTRIBUTING.md         # This file
```

## Making Changes

1. **Create a branch** for your feature or bugfix:
```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes** following the code style guidelines

3. **Add tests** for new functionality

4. **Run tests** to ensure everything works:
```bash
pytest
```

5. **Commit your changes** with clear messages:
```bash
git commit -m "feat: Add support for custom AI providers"
```

We follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Adding or updating tests
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

6. **Push to your fork**:
```bash
git push origin feature/your-feature-name
```

7. **Create a Pull Request** on GitHub

## What to Contribute

### High Priority
- Support for other LLM providers (Anthropic Claude, local models)
- Enhanced codebase context gathering (AST parsing, semantic search)
- Automatic rollback functionality
- Web UI for visualization
- Better error recovery
- Plugin system for custom actions

### Medium Priority
- Integration with version control systems
- CI/CD examples and templates
- More validation rules
- Performance optimizations
- Better progress tracking

### Low Priority
- Additional output formats
- More configuration options
- Documentation improvements
- Example projects

## Reporting Bugs

Create an issue on GitHub with:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Python version, OS, etc.)
- Error messages and logs

## Suggesting Features

Create an issue with:
- Clear description of the feature
- Use cases and benefits
- Potential implementation approach
- Any relevant examples

## Code Review Process

All submissions require review. We'll:
- Check code quality and style
- Verify tests pass
- Review documentation
- Ensure backwards compatibility
- Provide feedback for improvements

## Testing Guidelines

- Write tests for all new features
- Maintain or improve code coverage
- Test edge cases and error conditions
- Use descriptive test names
- Keep tests isolated and independent

Example test structure:
```python
class TestNewFeature:
    """Tests for new feature"""

    def test_basic_functionality(self):
        """Test that basic feature works"""
        # Arrange
        # Act
        # Assert
        pass

    def test_edge_case(self):
        """Test edge case handling"""
        pass

    def test_error_handling(self):
        """Test error conditions"""
        pass
```

## Documentation

- Update README.md for user-facing changes
- Add docstrings for new functions/classes
- Update EXAMPLES.md with usage examples
- Comment complex logic

## Release Process

1. Update version in `setup.py` and `__init__.py`
2. Update CHANGELOG.md
3. Create release notes
4. Tag release: `git tag v0.2.0`
5. Push to PyPI

## Questions?

- Open an issue for questions
- Check existing issues and discussions
- Join our community chat (coming soon)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow the Golden Rule

Thank you for contributing to Agentic Layer!
