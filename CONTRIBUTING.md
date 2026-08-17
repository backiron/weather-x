# Contributing

Contributions are welcome when they preserve the project's evidence-first boundary.

1. Open an issue describing the scientific or engineering problem.
2. Add tests for behavior changes.
3. Keep target truth, model inputs, and downstream application data separate.
4. Preserve observation time, receipt time, and label reveal time.
5. Do not add raw provider data or private station coordinates.
6. Run `pytest`, `ruff check .`, and `python scripts/verify_public_release.py`.

Claims of improved accuracy should include an out-of-time or spatially held-out comparison with
independent event-level sampling units.
