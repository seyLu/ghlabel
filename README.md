<div align="center">
    <img height=100 src="https://github.com/seyLu/python-template/blob/main/static/icons/python.png" alt="Python Template Icon">
    <h1>Python Template</h1>
    <p>Template Repository for quickly starting a Python project</p>
    <p>
        <a href="https://github.com/seyLu/python-template/issues/new">Report Bug</a>
        ·
        <a href="https://github.com/seyLu/python-template/issues/new">Request Feature</a>
        ·
        <a href="https://github.com/seyLu/python-template/discussions">Ask Question</a>
    </p>
</div>

<br>

### Supported Python version

```bash
python==3.11
```

<br>

### Built-in Python Tooling Features

- Lint Workflow
    * Ruff (superfast linter written in rust)
    * Isort (import sorter)
    * Black (opinionated formatter)
    * Mypy (type checking)
- Lint pre-commit ([see Setup: pre-commit](#setup-pre-commit))
    * Ruff
    * Isort
    * Black
- Config
    * Dependabot for pip
        - .github/dependabot.yaml
    * Tooling
        - pyproject.toml
    * Logging ([see Usage: logging with logging.ini](#usage-logging-ini))
        - logging.ini
    * Global Editor Rules
        - .editorconfig

<br>
<div id="#setup-pre-commit"></div>

### Setup: pre-commit

```bash
pip install pre-commit
pre-commit install
```

<br>
<div id="#usage-logging-ini"></div>

### Usage: logging with logging.ini

```python
from logging.config import fileConfig

fileConfig("logging.ini")

logging.info("Works as expected.")
```
