# Contributing to Candidate Evaluator

Thank you for your interest in contributing to Candidate Evaluator! This document provides guidelines and instructions for contributing.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Coding Standards](#coding-standards)
5. [Testing](#testing)
6. [Documentation](#documentation)
7. [Pull Request Process](#pull-request-process)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful and considerate in all interactions.

## Getting Started

### Development Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/yourusername/candidate-evaluation-model.git
   cd candidate-evaluation-model
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -e ".[dev]"
   ```

4. **Set up pre-commit hooks** (optional but recommended):
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Write code following our coding standards
   - Add tests for new functionality
   - Update documentation as needed

3. **Run tests**:
   ```bash
   pytest
   ```

4. **Run linting**:
   ```bash
   flake8 candidate_evaluator/
   black candidate_evaluator/
   ```

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add feature: description of your changes"
   ```

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**

## Coding Standards

### Python Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use [Black](https://black.readthedocs.io/) for code formatting
- Maximum line length: 100 characters
- Use type hints where appropriate

### Code Organization

```python
"""Module docstring describing purpose."""

import standard_library
import third_party_libraries

from local_package import local_module


class MyClass:
    """Class docstring."""

    def __init__(self):
        """Initialize the class."""
        pass

    def public_method(self, arg: str) -> str:
        """
        Public method docstring.

        Args:
            arg: Description of argument

        Returns:
            Description of return value
        """
        return self._private_method(arg)

    def _private_method(self, arg: str) -> str:
        """Private method docstring."""
        return arg.upper()
```

### Docstrings

Use Google-style docstrings:

```python
def function(arg1: str, arg2: int) -> bool:
    """
    Brief description of function.

    Longer description if needed, explaining what the function does,
    when to use it, and any important details.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of return value

    Raises:
        ValueError: Description of when this is raised
    """
    pass
```

## Testing

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Use descriptive test names: `test_function_name_expected_behavior`

Example:

```python
def test_evaluate_candidate_valid_input():
    """Test that evaluate_candidate works with valid input."""
    evaluator = CandidateEvaluator(config)
    result = evaluator.evaluate_candidate(
        candidate_id="TEST001",
        material_paths=["test_resume.txt"]
    )
    assert result.overall_score > 0
    assert len(result.scores) == 11
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_evaluator.py

# Run with coverage
pytest --cov=candidate_evaluator --cov-report=html

# Run with verbose output
pytest -v
```

### Test Coverage

Aim for at least 80% test coverage for new code. Check coverage with:

```bash
pytest --cov=candidate_evaluator --cov-report=term-missing
```

## Documentation

### Code Documentation

- Add docstrings to all public classes and functions
- Include type hints
- Explain complex logic with inline comments

### User Documentation

When adding new features, update:
- `README.md` - If it affects basic usage
- `docs/USAGE_GUIDE.md` - For detailed usage instructions
- Inline help text in CLI commands

## Pull Request Process

### Before Submitting

1. **Ensure tests pass**: Run `pytest` locally
2. **Update documentation**: Add/update relevant docs
3. **Follow commit conventions**: Use clear, descriptive commit messages
4. **Rebase if needed**: Keep your branch up to date with main

### PR Description

Include in your PR description:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe how you tested your changes

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code follows style guidelines
- [ ] All tests pass
```

### Review Process

1. A maintainer will review your PR
2. Address any feedback or requested changes
3. Once approved, your PR will be merged

## Areas for Contribution

### Good First Issues

Look for issues labeled `good-first-issue`:
- Documentation improvements
- Test coverage
- Bug fixes
- Minor feature additions

### Feature Ideas

- Additional export formats
- Integration with ATS systems
- Enhanced comparison analytics
- Performance optimizations
- Additional file format support

### Bug Reports

When reporting bugs, include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs

## Questions?

- Open an issue for general questions
- Use discussions for broader topics
- Contact maintainers directly for sensitive issues

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Thank You!

Your contributions help make Candidate Evaluator better for everyone. We appreciate your time and effort!
