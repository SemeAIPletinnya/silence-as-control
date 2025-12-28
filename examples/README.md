## Testing Philosophy

This repository does not use traditional unit tests.

Tests are defined as **control specifications**, written in Markdown.
Each test describes:
- input conditions
- observed metrics
- decision rules
- expected system behavior

These tests are **evaluated conceptually**, not executed mechanically.

Silence-as-Control is validated by *decision correctness*, not code coverage.
