# Contributing

Thank you for improving `swatch-story`.

## Development Setup

```bash
python -m pip install -e ".[dev]"
```

## Quality Checks

Run these before opening a pull request:

```bash
ruff check .
ruff format --check .
pytest -q
python -m build
```

## Guidelines

- Keep the project local-first. Do not add remote image fetching to the MVP.
- Use English for code comments, commit messages, and issue templates.
- Keep `README.md`, `README-zh.md`, and `README-ja.md` synchronized in meaning.
- Add behavior-focused tests before changing behavior.
- Use Conventional Commit messages when possible.
