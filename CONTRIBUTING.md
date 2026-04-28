# Contributing to InvestorClaw

**Status**: Open for contributions  
**Last Updated**: April 16, 2026

---

## Welcome! 👋

Thank you for your interest in contributing to InvestorClaw. This document explains how to contribute code, report bugs, suggest features, and participate in the community.

---

## Quick Start

### For Bug Reports
1. Check [existing issues](https://gitlab.com/argonautsystems/InvestorClaw/-/issues)
2. Create a new issue with: title, description, steps to reproduce, expected vs actual behavior
3. Include: Python version, OpenClaw version, error logs

### For Feature Suggestions
1. Open an issue labeled `enhancement`
2. Describe the feature and use case
3. Explain how it fits the InvestorClaw vision

### For Code Contributions
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make changes following our code style
4. Write tests for new functionality
5. Create a pull request with description of changes

---

## Licensing & Legal

InvestorClaw uses a **dual license model**:

- **Free Tier**: Apache 2.0 + Commons Clause (non-commercial use)
- **Commercial Tier**: Proprietary (commercial use)

**All contributions are made under the Apache 2.0 license** for the free tier, with the understanding that:

1. Your contribution may be included in commercial products
2. InvestorClaw may be relicensed commercially
3. You grant InvestorClaw full rights to your contribution
4. You retain the right to use your contribution (non-exclusive)

---

## Contribution Scope

### ✅ Welcome Contributions

- Portfolio analysis improvements (holdings, performance, risk)
- Data provider integrations (Finnhub, Alpha Vantage, Polygon, etc.)
- Performance optimizations for large portfolios
- Unit tests and integration tests
- API documentation and user guides
- Bugfixes and security patches

### ❌ Not Open for Contribution

- Premium tier features (tax optimization, advisor mode, multi-portfolio)
- UI/frontend changes (OpenClaw integration)
- Commercial features (require commercial license)

Premium features should be proposed via: licensing@investorclaw.io

---

## Code Style

We follow **PEP 8** with:
- Type hints: Required for all functions
- Docstrings: Google style, required for public functions
- Line length: Max 100 characters
- Testing: 85%+ coverage for new code

### Format & Lint

```bash
black investorclaw/ --line-length=100
flake8 investorclaw/ --max-line-length=100
mypy investorclaw/ --strict
pytest tests/ -v --cov
```

---

## Pull Request Process

1. Fork and create feature branch
2. Make changes with tests
3. Run: `black`, `flake8`, `mypy`, `pytest`
4. Write PR description (use template below)
5. GitHub Actions will run automated tests
6. Team reviews and approves
7. Merged to main

### PR Template

```markdown
## Summary
[Brief description]

## Type
- [ ] Bug fix
- [ ] Feature
- [ ] Documentation
- [ ] Refactoring

## Related Issue
Closes #123

## Changes
- Change 1
- Change 2

## Testing
- [ ] Added unit tests
- [ ] All tests pass
- [ ] Tested with sample data

## Documentation
- [ ] Updated docs if needed
- [ ] Added docstrings
```

---

## Bug Reports & Features

**Bug Report**: Include steps to reproduce, environment info, error logs  
**Feature Request**: Problem statement, proposed solution, use cases

---

## Community Standards

We follow the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/).

Violations: conduct@investorclaw.io

---

## Getting Help

- **Questions**: [GitHub Discussions](https://gitlab.com/argonautsystems/InvestorClaw/discussions)
- **Bugs**: [GitHub Issues](https://gitlab.com/argonautsystems/InvestorClaw/-/issues)
- **Email**: support@investorclaw.io

---

## Recognition

Contributors are credited in:
- `CONTRIBUTORS.md`
- Release notes
- GitHub contributors page

---

## Contact

- **Maintainer**: Jason Perlow (@perlowja)
- **Issues**: [GitHub Issues](https://gitlab.com/argonautsystems/InvestorClaw/-/issues)
- **Discussions**: [GitHub Discussions](https://gitlab.com/argonautsystems/InvestorClaw/discussions)
- **Support**: support@investorclaw.io

---

Thank you for contributing! 🚀
