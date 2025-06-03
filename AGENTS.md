# AGENT Guidelines

This repository contains unit and UI tests that require PyQt6.

## Running Tests
- Use the `run_tests.py` script from the repository root.
  - Unit tests: `python run_tests.py --unit -q`
  - UI tests: `python run_tests.py --ui -q`
  - All tests: `python run_tests.py -q`
- Before running UI tests on a fresh environment:
  1. Install Python dependencies:
     `pip install -r requirements.txt -r requirements-test.txt`
  2. Install system Qt libraries:
     `apt-get update && apt-get install -y libegl1`
- The environment variable `QT_QPA_PLATFORM=offscreen` is configured in
  `tests/ui/conftest.py` to allow headless execution.

## Workflow
- Always run unit tests before committing changes.
- If UI code is modified, run the affected UI tests as well.
- Keep commit messages concise and descriptive.
