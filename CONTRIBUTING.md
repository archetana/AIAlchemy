# Contributing to AIAlchemy

Thank you for your interest in contributing to AIAlchemy! This document provides guidelines for contributing to this AI-powered startup evaluation platform.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style Guidelines](#code-style-guidelines)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)
- [Documentation](#documentation)

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/AIAlchemy.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Follow the [Development Setup](#development-setup) section

## Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional)
- Google Cloud SDK (for cloud features)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Frontend Setup
```bash
cd frontend
npm install
```

### Pre-commit Hooks
```bash
pip install pre-commit
pre-commit install
```

## Code Style Guidelines

### Python (Backend)
- Follow PEP 8 style guide
- Use Black for code formatting: `black .`
- Use isort for import sorting: `isort .`
- Use type hints for all functions
- Write docstrings for all classes and methods
- Maximum line length: 88 characters

### JavaScript/React (Frontend)
- Use ESLint and Prettier
- Follow functional component patterns with hooks
- Use proper TypeScript typing
- Maximum line length: 80 characters

### Example Python Code
```python
from typing import List, Optional

async def evaluate_startup(
    startup_data: StartupData,
    options: Optional[EvaluationOptions] = None
) -> EvaluationResult:
    """
    Evaluate startup using multi-agent AI system.
    
    Args:
        startup_data: Company information and materials
        options: Optional evaluation parameters
        
    Returns:
        Complete evaluation with scoring and recommendations
    """
    # Implementation here
    pass
```

## Commit Guidelines

### Commit Message Format
```
type(scope): Brief description

Detailed explanation of changes (optional)

Closes #issue-number (if applicable)
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Build process or auxiliary tool changes

### Examples
```
feat(api): Add startup evaluation endpoint
fix(ui): Resolve dashboard loading issue
docs: Update API documentation
```

## Pull Request Process

1. **Update your branch**: Sync with the latest main branch
2. **Run tests**: Ensure all tests pass
3. **Check code style**: Run linting and formatting tools
4. **Write tests**: Add tests for new functionality
5. **Update documentation**: Update relevant docs
6. **Create PR**: Use the provided template
7. **Code review**: Address feedback from reviewers

### PR Checklist
- [ ] Code follows project style guidelines
- [ ] Tests pass and new tests added
- [ ] Documentation updated
- [ ] No breaking changes (or properly documented)
- [ ] Commit messages follow guidelines

## Testing

### Backend Testing
```bash
cd backend
pytest tests/ -v --cov=app
```

### Frontend Testing
```bash
cd frontend
npm test
npm test -- --coverage
```

### Integration Testing
```bash
# Run both backend and frontend
docker-compose up -d
# Run integration tests
pytest tests/integration/
```

## Documentation

### What to Document
- New features and APIs
- Configuration changes
- Deployment procedures
- Architecture decisions

### Documentation Structure
```
docs/
├── API-ENDPOINTS.md       # API documentation
├── DEPLOYMENT-STEPS.md    # Deployment guide
├── DEVELOPMENT-BACKLOG.md # Development tasks
├── DEVELOPMENT-ROADMAP.md # Future plans
├── GCP-DEPLOYMENT.md      # Google Cloud deployment
├── agents.md              # AI agent documentation
└── ...
```

### Writing Documentation
- Use clear, concise language
- Include code examples
- Add screenshots for UI changes
- Update README.md for major changes

## Issue Reporting

### Bug Reports
Use the bug report template and include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details
- Screenshots (if applicable)

### Feature Requests
Use the feature request template and include:
- Problem statement
- Proposed solution
- Alternative approaches
- Implementation considerations

## Code Review Guidelines

### As a Reviewer
- Be constructive and helpful
- Focus on code quality and maintainability
- Check for proper testing
- Ensure documentation is updated

### As an Author
- Respond promptly to feedback
- Ask questions if feedback is unclear
- Make requested changes or discuss alternatives
- Keep PR scope focused

## Getting Help

- Create an issue for bugs or feature requests
- Use GitHub Discussions for questions
- Check existing documentation
- Review similar issues/PRs

## License

By contributing, you agree that your contributions will be licensed under the MIT License.