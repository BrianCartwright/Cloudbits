# Cloudbits

**Cloudbits** is a 2D Fibonacci Pattern Explorer — a standalone terminal application (TUI) for building, validating, and sharing patterns based on Fibonacci arithmetic and G-Base representation.

> **Status: Work in progress.** The design specification is thorough and complete (see [SPEC.md](SPEC.md)). The terminal layout is implemented; mode logic and pattern validation are under active development.

---

## What it does

On a fixed 136×44 terminal grid, you place and manipulate cells to build two-dimensional Fibonacci patterns. Each pattern is validated in real time against a 31×31 sequence of integers. Patterns can be saved as `.ptn` files, loaded, and shared with the community.

The application has four modes:

- **Build (B)** — place and edit cells with the orange cursor
- **Satellite (S)** — define independent pattern sets, each with its own Handle position
- **History (H)** — suspend the current state and explore prior snapshots
- **Grid (G)** — set background options including checkerboard parity and FRAC overlay

Cloudbits is designed to be satisfying as a mathematical game in the terminal, and the pattern format and validation logic are intended to support an eventual mobile or web port.

---

## Requirements

- Python 3.10+
- [Textual](https://textual.textualize.io/) — TUI framework
- [Rich](https://rich.readthedocs.io/) — terminal text rendering

```bash
pip install textual rich
```

A true-color terminal is recommended for correct color rendering (the spec defines specific hex palette values). Minimum terminal size: **136 columns × 44 rows**.

---

## Running

```bash
python CbitsLayout.py
```

The terminal layout and panel structure are implemented. Full mode interaction is in progress — see [SPEC.md](SPEC.md) for the complete design.

---

## Documentation

- [SPEC.md](SPEC.md) — Full design specification (v0.5). Covers architecture, all four modes, cursor behavior, color palette, History system, pattern file format, and phased implementation plan.
- [CbitsTextualReference.md](CbitsTextualReference.md) — Reference guide to Textual widgets and Rich rendering objects used in this project, with notes on the chexel (half-block character) rendering approach.

---

## Patterns

The [`patterns/`](patterns/) folder contains example `.ptn` files demonstrating valid Fibonacci patterns. See [patterns/README.md](patterns/README.md) for the file format and how to submit your own patterns.

---

## Contributing

Contributions are welcome at any level:

- **Python / TUI developers** — the spec is detailed; pick up any unimplemented module and build against it
- **Mobile / web developers** — the validation core is a 31×31 integer matrix with no external dependencies; a port would be self-contained
- **Pattern creators** — share your patterns via the `patterns/` folder (see [patterns/README.md](patterns/README.md))

If you have questions about the spec or want to discuss the design before diving in, open an Issue.

---

*Cloudbits is part of a broader mathematics exploration project. It is designed to run as a fully self-contained application.*
