# Cloudbits Patterns

This folder contains `.ptn` pattern files for Cloudbits — a 2D Fibonacci Pattern Explorer.

Each pattern is a validated arrangement of cells on the Cloudbits grid, confirmed against the underlying 31×31 Fibonacci integer sequence.

---

## File format

Pattern files use the `.ptn` extension. The format is defined in the [full specification](../SPEC.md) (Section on File I/O and the `.ptn` format). Key fields include:

- Grid cell coordinates for the Build set and any Satellite sets
- Handle position(s) for each Satellite
- Metadata: pattern name, creation date, validation status

*(Format details will be documented here once the file I/O module is implemented.)*

---

## Submitting your pattern

If you have created a pattern in Cloudbits that you would like to share:

1. Save it from within the application — this produces a `.ptn` file
2. Open an [Issue](../../issues) with the `.ptn` file attached and a brief description of the pattern
3. Patterns that validate correctly will be added to this folder

There are no style requirements — interesting, surprising, or beautiful arrangements are all welcome.

---

## Example patterns

*(Coming soon — example patterns will be added here as development progresses.)*
