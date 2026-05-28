# CLAUDE.md — Cloudbits

This file provides guidance to Claude Code when working with the Cloudbits
codebase.

## What This Project Is

Cloudbits is a 2D Fibonacci Pattern Explorer — a standalone terminal TUI
application built with Textual and Rich. It has no dependency on the broader
Nnumerics codebase. Its validation logic uses a self-contained 31×31 integer
matrix computed at startup.

The full design specification is in `SPEC.md`. Read it before making
architectural decisions. Status markers in the spec ([SETTLED], [PROVISIONAL],
[TBD], [DEFERRED]) indicate confidence level for each decision.

## Two-Layer Architecture

The application is divided into two strict layers. This boundary must be
maintained at all times.

**Python UX Logic Layer** — all behavioral decisions live here. No Textual
imports. Pure Python. Testable without a terminal.

**Textual Rendering Layer** — a thin display wrapper. Its only job is to read
state from the Python layer and render it. It makes no behavioral decisions.
Textual Reactives are the appropriate mechanism for observing Python layer
state.

If you find yourself putting logic into the Textual layer, stop and move it
up into the Python layer.

## Domain Objects (Python UX Logic Layer)

| Domain | Responsibility |
|---|---|
| AppState | Current mode (B/S/H/G), cursor position, active cell sets, validation state |
| ModeManager | B/S/H/G transitions, H suspension logic, Satellite count tracking |
| CellSetManager | Coordinate collections for Build and all Satellite sets; active/inactive flags; Handle positions |
| CursorController | Orange cursor (Build), Handle position(s) (Satellite), Edit cursor, boundary enforcement |
| ValidationEngine | Testbed sequence, unified integer validation, legal pattern detection, Keep gating |
| HistoryManager | Linear state timeline, K snapshots, H mode navigation |
| PatternLibrary | Loads, parses, and indexes .ptn files |
| GridBackground | Active background elements, opacity levels, daisy shift offset and Flip variant |
| CombEngine | [PENDING] Diagonal translation, bit representation, Pord computation |

Cell sets are stored as **separate coordinate collections** — never as a
single monolithic set. Each Satellite set carries: coordinates,
active/inactive flag, Handle position, and animation state. This is required
from Phase 1 to avoid refactoring when multiple Satellites are added in
Phase 3b.

## Grid & Coordinates

- 31×31 grid; center cell is (0,0); coordinates range ±15 in both axes
- Reference Cell (RefCell) is always at (0,0); cannot be selected as a Build cell
- User coordinate formula: `user_coord = display_index - 15` (0-indexed)
- Axis orientation (row direction) must be confirmed against rendering before Phase 1

## Visual Rendering

Cells are rendered as **chexels**: 2×2 half-block Unicode characters (▀▄)
creating a virtual checkerboard pixel — two colors per terminal cell.
The grid is a single canvas object; no alleys or gutters between cells.

Key chexel combinations are listed in §4.2 of the spec. Rendering priority
when Satellite and Build cells share coordinates: Satellite color wins.

Animation (2–4 Hz for active Satellites) is a **runtime display attribute
only**. It is never captured in K snapshots and must not affect application
state.

## Phase Boundaries

**Phases 1 and 2 are ready to implement.** Start here.

| Phase | Scope |
|---|---|
| 1 | Canvas grid, Build mode, orange cursor, RefCell, basic K |
| 2 | Testbed, validation counter, Bingo highlight, Save (Build) |
| 3a | Satellite mode — S toggle, Handle, single Satellite, Include, stamping |
| 3b | Multiple Satellites, + spawning, Tab/Return cycling, animation, Edit, Flip (S), Satellite Save |
| 4+ | Pattern Library, History, G mode, K gating, Comb — see spec §15 |

**Explicitly excluded from Phases 1–2:** Satellite spawning, Pattern Library
loading, History/H mode, full K, Include, Edit, loading to non-empty grid,
G mode, Comb.

**K gating is a Phase 7 feature.** In Phases 1–6, K always succeeds
regardless of adjacency or collision conditions. Do not build partial
validation logic ahead of Phase 7.

## Key Design Constraints

- **Single cursor rule**: only one primary cursor visible at any time
- **Spacebar** toggles cell selection in the active cell set
- **No mouse support** in this iteration
- **Boundary enforcement**: cursor and Handle movement disabled at grid edge (±15)
- The orange Build cursor and the gray-blue Satellite Handle are distinct;
  they are never both visible simultaneously
- Build cells are always fully visible and never dimmed, even in S mode

## Running the Application

```bash
# (venv or direct python once dependencies are installed)
python -m cloudbits
# or
python CbitsCanvas.py
```

Dependencies: `textual`, `rich` (see `requirements.txt`).
Target terminal: 136 columns × 44 rows minimum.

## Working Conventions

- Discuss structural design and function signatures before writing code
- Implement in small incremental pieces; each phase should be demonstrable
- After 2–3 revisions without progress, reconsider the approach rather than
  continuing to patch
- The spec uses [SETTLED] to mark confirmed decisions — do not revisit these
  without a design discussion
- Open Questions (§16 of spec) are explicitly deferred; do not attempt to
  resolve them during implementation
