# Textual & Rich — Widget and Rendering Reference
## For Cloudbits development

This document lists Textual widgets and Rich text objects relevant to
Cloudbits, organized by rendering path. See the Textual documentation at
https://textual.textualize.io and the Rich documentation at
https://rich.readthedocs.io for full details.

---

## 1. Canvas-Based Rendering (Grid and Comb Row)

These are low-level Textual rendering primitives used for the main grid
canvas and the Comb row — anywhere requiring direct cell-by-cell control
over foreground color, background color, and character.

### `Strip`
The fundamental unit of Textual rendering. A `Strip` is an immutable
sequence of `Segment` objects representing one row of terminal output.
Used in the `render_line()` method of custom widgets to produce canvas
output row by row.

### `Segment`
A single terminal cell or run of identically-styled cells: a string of
text plus a `Style`. The building block of `Strip`. Used directly for
chexel rendering — each half-block character (▀ ▄) with a specific
foreground/background pair is one `Segment`.

### `Style`
Textual/Rich style object specifying foreground color, background color,
bold, dim, reverse, etc. Used to style individual `Segment` objects.
Colors can be specified as hex strings (`"#ff8000"`), named colors, or
`Color` objects.

### `Color`
Rich/Textual color object. Supports hex, RGB, named terminal colors, and
256-color indices. Relevant for specifying the exact palette values in
the Cloudbits color table (Section 4.4).

### `Canvas` (if using textual-canvas or similar)
A higher-level widget that provides a drawing surface with methods for
painting characters, lines, and rectangles. Check current Textual version
for availability — the Strip/Segment approach may be preferred for full
control.

### Custom Widget with `render_line()`
The recommended approach for the Cloudbits grid: subclass `Widget` and
override `render_line(y)` to return a `Strip` for each row. This gives
complete control over every cell. The chexel system, FRAC highlighting,
perimeter margin, and diagonal ghost overlay all live here.

---

## 2. Rich Text Widgets (Control Panel, Status Bar, Labels)

These widgets render Rich markup strings and are appropriate for all
text-based UI elements outside the grid canvas.

### `Static`
Displays a single Rich-formatted string. Use for: mode labels (BUILD,
SATELLITE), the validation counter display, the History counter (7 / 12),
the NOTES placeholder in the right panel. Supports reactive updates via
`update()`.

### `Label`
Similar to Static but lighter-weight. Use for: panel headers (PATTERN
LIBRARY, HISTORY, COMB), the small attenuated "comb" label, column
headers (INTEGERS, PATTERNS).

### `RichLog`
A scrollable log widget that accepts Rich markup lines. Consider for:
the History timeline state list in the right panel, where each Kept state
is one line with its counter number and summary.

### `Input`
Single-line text input widget. Use for: the filename entry field that
appears in the Status Bar when Save is triggered. Supports placeholder
text and validation callbacks.

### `Button`
A clickable/pressable button widget. Use for: FLIP, INCLUDE, KEEP,
HISTORY, and the `+` spawner. Supports disabled state (grayed out) via
the `disabled` property — relevant for graying out controls in H mode.

### `RadioButton` / `RadioSet`
Textual's built-in radio button group. Use for: the BUILD / SATELLITE
mode group. `RadioSet` manages mutual exclusion. The H button should
*not* be part of this RadioSet — it is a separate Button.

### `Digits`
A large-format numeric display widget (uses seven-segment style digits).
Potentially useful for: the ROW / COLUMN coordinate display, where large
readability is specified.

### `ProgressBar`
Probably not needed, but noted in case the validation counter display
benefits from a bar representation alongside the numeric ratio.

---

## 3. Rich Text Markup Reference

These are Rich markup features usable inside any Rich-capable widget
(Static, Label, RichLog, etc.).

### Color spans
`[color]text[/color]` — inline foreground color.
Example: `"[#ff8000]BUILD[/#ff8000]"` for orange mode label.

### Background color
`[on color]text[/on color]` — inline background color.
Example: `"[on #6090c0] [/on #6090c0]"` for a gray-blue margin block.

### Bold / Dim
`[bold]text[/bold]`, `[dim]text[/dim]` — useful for distinguishing
active vs. inactive controls (dim for grayed-out controls in H mode).

### Underline
`[underline]T[/underline]ext` — for the initial-character underline
convention in control panel labels.

### Composite styles
`[bold #ff8000]SATELLITE[/bold #ff8000]` — color and weight combined.

---

## 4. Textual Reactive System (State-Driven Rendering)

These are not rendering objects but are central to how Cloudbits' Python
UX Logic Layer drives the Textual Rendering Layer.

### `reactive`
A Textual descriptor that triggers UI updates automatically when a value
changes. Use for: current mode (B/S/H), cursor position, validation
counter value, Satellite count badge, History counter. Declaring these as
`reactive` attributes means the rendering layer updates automatically
when AppState changes.

### `watch_*` methods
Automatically called when a `reactive` value changes. Use to trigger
canvas redraws, update Static widgets, enable/disable Buttons, etc.

### `on()` decorator / message system
Textual's event/message system. Use for: key bindings (arrow keys,
Spacebar, B, S, H, K, F, E, I, V, Tab, Shift-Tab, Escape, Return),
Button press events, RadioSet change events.

---

## 5. Notes on Half-Block Chexel Rendering

The chexel system uses Unicode half-block characters:

- `▀` (U+2580) UPPER HALF BLOCK — foreground color fills top half,
  background color fills bottom half
- `▄` (U+2584) LOWER HALF BLOCK — foreground color fills bottom half,
  background color fills top half

A 2×2 chexel uses two terminal cells stacked vertically. Each cell is
one `Segment` with a specific foreground/background pair. The
checkerboard pattern (even/odd cell parity) is achieved by alternating
which character is used.

Terminal color fidelity for the specified hex values (#ff8000, #40ff40,
#6090c0 etc.) requires a true-color terminal. The spec notes that
fallback 256-color mappings should be defined for each key color before
Phase 1 ships.

---

*Prepared April 2026*
*See: https://textual.textualize.io/widgets/*
*See: https://rich.readthedocs.io/en/stable/*
