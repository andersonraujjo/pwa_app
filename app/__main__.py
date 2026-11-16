"""Permite `python -m app.cli` via `python -m app`? Preferir app.cli."""

from app.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
