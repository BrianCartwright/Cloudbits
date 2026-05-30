# spec-seq2d-investigation.md

## What this does

This module extends `seq2d_utils.py` with a coefficient grid approach to 2DSeq
investigation and validation. Every cell in a 2DSeq is a linear combination of the four
SeedMatrix values `a, b, c, d`. The coefficient grid makes this explicit by storing a
CoeffTuple at each cell rather than an integer, so equality questions become algebraic
rather than seed-specific. A result that holds in the coefficient grid holds universally
for all seeds.

This is the canonical validation algorithm for Cloudbits. It replaces the numeric integer
testbed, which could not distinguish universal equalities from seed-specific artifacts.

## Where it fits

The coefficient grid uses the same recurrence structure as `make_2dseq()` in
`seq2d_utils.py`, operating on CoeffTuples rather than integers. `make_2dseq()` is
refactored as a convenience wrapper for backward compatibility. The sparse algebraic
functions (`build_gpower_matrix`, `extend_seed_row`) are not touched.

---

## The CoeffTuple class

CoeffTuple is a fixed-length container of integers representing the linear combination of
seed components at a given cell. For a 2DSeq the components are `[ca, cb, cc, cd]` where
the cell's value equals `ca*a + cb*b + cc*c + cd*d`. The internal representation is a
fixed-length list or tuple of integers with no named fields, so the class generalizes to
2^n components for an n-dimensional sequence without redesign.

Key operations on CoeffTuple:

- Addition and subtraction are element-wise, mirroring the recurrence.
- `is_bingo()` returns `k` if all components after the first are zero — that is, the
  tuple is `[k, 0, 0, 0]` — and `None` otherwise. The check is
  `all(v == 0 for v in t[1:])`. This generalizes to any dimension.
- `is_qpair()` returns True when `t[1] == 0 and t[2] == 0 and t[0] == t[3]`,
  identifying patterns that are integer multiples of `[1,0,0,1]` — the 2D analog of Q.
  This condition has a natural generalization to higher dimensions.
- Dot product with a seed `(a, b, c, d)` evaluates the cell's numeric value.

---

## Function group 1: Coefficient grid construction

`make_coeff_grid(half)` generates the coefficient grid. The four Lens cells are seeded
with unit CoeffTuples at their canonical positions: `[1,0,0,0]` at `(0,0)`,
`[0,1,0,0]` at `(-1,0)`, `[0,0,1,0]` at `(0,-1)`, and `[0,0,0,1]` at `(-1,-1)`. The
axes and all four quadrants are then filled using the same recurrence as `make_2dseq()`,
with element-wise CoeffTuple addition and subtraction replacing integer arithmetic. The
result is a dict mapping `(i,j)` to a CoeffTuple, covering the same index range as
`make_2dseq()` for the same value of `half`.

`evaluate_grid(coeff_grid, a, b, c, d)` applies a seed by taking the dot product at each
cell, returning a numeric dict identical in shape to what `make_2dseq()` produces for the
same seed. `make_2dseq()` is refactored as a wrapper around these two functions. Since
`make_coeff_grid()` is O(n²) in `half`, callers that produce multiple numeric grids for
different seeds should cache the coefficient grid and call `evaluate_grid()` directly
rather than going through the wrapper each time.

---

## Function group 2: Algebraic equality testing

`is_universal_multiple(coeff_grid, i, j)` returns the integer `k` if the CoeffTuple at
`(i,j)` satisfies `is_bingo()` — meaning `f(i,j)` is always exactly `k * f(0,0)` for
all seeds — and `None` otherwise.

`coeff_scan(coeff_grid, half)` applies `is_universal_multiple` to every cell and returns
two lists: `(i, j, k)` triples for cells that are universal multiples of `f(0,0)`, and
`(i, j)` pairs for cells that are not.

`lens_discriminant(a, b, c, d)` computes `(a*d) - (b*c)` for a given seed. This term is
not yet in the Glossary and should be added; it is the proposed 2D analog of the 1D
sequence norm. Its role in constraining equality structure is an open research question.

---

## Function group 3: Pattern testing

`test_pattern(coeff_grid, cells)` takes a list of absolute `(i,j)` coordinates, sums
their CoeffTuples element-wise, and returns the resulting CoeffTuple. The caller
interprets the result: `is_bingo()` confirms a universal integer multiple of `f(0,0)`;
matching an anchor cell's CoeffTuple confirms the pattern equals that anchor universally;
`is_qpair()` identifies a potential 2D QInt pattern.

`scan_pattern(coeff_grid, offsets, half)` takes a list of relative `(di, dj)` offsets,
anchors them at every valid position `(i,j)` in the grid, and returns a dict mapping each
anchor to the CoeffTuple sum from `test_pattern`. Anchors where any offset cell falls
outside the grid bounds are skipped silently.

One named offset pattern is defined as a module-level constant:

`QPAIR = [(0,0), (-1,-1)]` encodes the diagonal pair `f(0,0) + f(-1,-1)`, the 2D analog
of the Q pattern from 1D sequences, where the Bitrep "101" corresponds to the sum of two
members at offset 2. The Lens contributes the `a+d` structure, giving QPAIR the
CoeffTuple form `[1,0,0,1]`. Scanning QPAIR across the grid and applying `is_qpair()` to
results at each anchor is the primary tool for investigating 2D QInt analogs.

---

## Function group 4: Orthogonal variants

`transpose_coeff_grid(coeff_grid, half)` produces the orthogonal Pyramid variant by
mapping every cell `(i,j)` to `(j,i)`. This is equivalent to seeding with `(a,c,b,d)`
rather than `(a,b,c,d)` — swapping `b` and `c` — and the transposed grid's Lens should
carry `[1,0,0,0]`, `[0,0,1,0]`, `[0,1,0,0]`, `[0,0,0,1]` at positions `(0,0)`,
`(-1,0)`, `(0,-1)`, `(-1,-1)` respectively, confirming the swap.

---

## Cloudbits integration

The coefficient grid is computed once at application startup by calling
`make_coeff_grid(half)`. On every cell-set change, `validation_engine.py` calls
`test_pattern(coeff_grid, cells)` and inspects the result with `is_bingo()`. Bingo fires
when the result is `[k, 0, 0, 0]`, and `k` is displayed as the integer ratio. Patterns
with non-zero components beyond the first are seed-dependent and are treated as non-Bingo.
No numeric testbed seed is needed for validation. The G grid mode is cosmetic and requires
no seed.

The Integers category in the Pattern Library now means universally true for all seeds —
algebraically guaranteed — rather than integer for a configured seed. This is a strictly
stronger definition, and the spec language at §9.3 should be updated to reflect
CoeffTuple validation. QPair validation — identifying patterns as integer multiples of
`[1,0,0,1]` using `is_qpair()` — is a candidate second category for the Pattern Library
in a future phase, at the same level as Integers.

---

## What success looks like

- The Lens cells of `make_coeff_grid()` carry the expected unit CoeffTuples at their
  canonical positions.
- `evaluate_grid(coeff_grid, 19, 3, 8, 7)` matches every reference value from the
  existing `make_2dseq()` smoke test in `seq2d_utils.py`.
- `transpose_coeff_grid` produces a Lens where the `b` and `c` unit vectors are swapped.
- `coeff_scan` on `half=15` produces non-empty lists in both categories.
- `scan_pattern(coeff_grid, QPAIR, 15)` runs without error; `is_qpair()` applied to each
  result reflects consistent algebraic structure across the grid.

---

## What this does not do

This spec does not define what a 2D integer is. It does not implement Pyramid display or
terminal rendering. It does not resolve the role of the prime discriminant condition in
constraining equality structure. It does not define the 2D QInt class — QPAIR and
`scan_pattern` are investigative tools for that question, not its answer. The F[]
primitives algorithm for computing CoeffTuples directly from sequence values rather than
recursively is the right architecture for n>2 but is deferred; the recursive construction
is adequate for 2D. The connection between `make_coeff_grid()` and `extend_seed_row()` is
left for a later investigation.
