# Contributing to Lich Framework

Thank you for your interest in contributing to Lich Framework! 🧙

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/DoTech-fi/lich.git
cd lich

# Install CLI in development mode
cd cli
pip install -e ".[dev]"

# Run tests
pytest
```

## 📋 Development Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use type hints where possible
- Write docstrings for public functions
- Keep functions small and focused

### Commit Messages

Use conventional commits:

```
feat: add new command
fix: resolve issue with migration
docs: update README
test: add tests for middleware
```

### Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit your changes
6. Push to your fork
7. Open a Pull Request

## 🧪 Running Tests

```bash
cd cli
pytest                    # Run all tests
pytest -v                 # Verbose output
pytest --cov=lich         # With coverage
pytest tests/test_make.py # Specific test file
```

## 📁 Project Structure

```
lich/
├── cli/                  # CLI package
│   ├── src/lich/
│   │   ├── commands/    # CLI commands
│   │   └── cli.py       # Main entry point
│   └── tests/           # CLI tests
├── template/             # Cookiecutter template
│   └── {{cookiecutter.project_slug}}/
├── docs/                 # Documentation
│   └── wiki/            # Wiki guides
└── README.md
```

## 🎯 Areas for Contribution

- **New Commands**: Add new `lich make` generators
- **Documentation**: Improve guides and examples
- **Tests**: Increase test coverage
- **Bug Fixes**: Fix reported issues
- **Templates**: Improve generated project templates

## 📝 Code of Conduct

Be respectful and inclusive. We welcome contributors from all backgrounds.

## ❓ Questions?

Open an issue or start a discussion on GitHub.

---

**Thank you for contributing!** 🙏
