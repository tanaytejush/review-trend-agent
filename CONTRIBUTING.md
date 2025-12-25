# Contributing

Thank you for your interest in contributing to the Review Trend Analysis System!

## Development Setup

1. Fork the repository
2. Clone your fork:
```bash
git clone https://github.com/your-username/review-trend-agent.git
cd review-trend-agent
```

3. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Configure your environment:
```bash
cp .env.example .env
# Add your API keys to .env
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write descriptive docstrings
- Keep functions focused and modular

## Testing

Before submitting a pull request:

1. Test your changes:
```bash
python -m pytest tests/
```

2. Run linting:
```bash
flake8 .
black .
```

3. Ensure documentation is updated

## Pull Request Process

1. Create a feature branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes
3. Commit with clear messages
4. Push to your fork
5. Open a pull request

## Reporting Issues

When reporting issues, please include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Relevant logs or error messages

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help create a welcoming environment

Thank you for contributing!
