"""
CbitsCanvas.py — Cloudbits Textual Rendering Layer

Thin display wrapper around the Python UX Logic Layer (cloudbits/).
Makes no behavioural decisions; reads state and renders it.
"""
import os
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Input
from textual.widget import Widget
from textual.strip import Strip
from rich.segment import Segment
from rich.style import Style
from rich.color import Color

from cloudbits.app_state import AppState, Mode
from cloudbits.mode_manager import ModeManager
from cloudbits.cell_set_manager import CellSetManager
from cloudbits.cursor_controller import CursorController
from cloudbits.history_manager import HistoryManager, Snapshot
from cloudbits.validation_engine import ValidationEngine
from cloudbits.file_manager import FileManager

# ── colour palette (xterm-256) ────────────────────────────────────────────────
C_ORANGE     = Color.from_ansi(208)   # Build cursor
C_DARK_GREEN = Color.from_ansi(28)    # Build cells + B-mode margin
C_GRAY_BLUE  = Color.from_ansi(67)    # RefCell
C_BLACK      = Color.from_ansi(0)     # Grid background

GRID_MIN = -15
GRID_MAX = 15


# ── Grid widget ───────────────────────────────────────────────────────────────

class GridWidget(Widget):
    """
    31x31 chexel canvas.  Each grid cell maps to two terminal chars (▀▄)
    forming a 2x2 virtual checkerboard pixel with two independent colours.
    """

    DEFAULT_CSS = """
    GridWidget {
        width: 62;
        height: 31;
        background: black;
    }
    """

    def __init__(self, state: AppState, cells: CellSetManager) -> None:
        super().__init__()
        self._state = state
        self._cells = cells

    def render_line(self, y: int) -> Strip:
        if y < 0 or y > 30:
            return Strip([])
        grid_row = 15 - y
        segments: list = []
        for grid_col in range(GRID_MAX, GRID_MIN - 1, -1):
            primary, secondary = self._cell_colors(grid_row, grid_col)
            style = Style(color=primary, bgcolor=secondary)
            segments.append(Segment("▀", style))
            segments.append(Segment("▄", style))
        return Strip(segments)

    def _cell_colors(self, row: int, col: int) -> tuple:
        is_cursor  = (row == self._state.cursor_row and col == self._state.cursor_col)
        is_refcell = (row == 0 and col == 0)
        is_build   = (row, col) in self._cells.build_cells

        if is_cursor:
            if is_refcell:
                return C_ORANGE, C_GRAY_BLUE
            if is_build:
                return C_ORANGE, C_DARK_GREEN
            return C_ORANGE, C_ORANGE

        if is_refcell:
            return C_GRAY_BLUE, C_GRAY_BLUE
        if is_build:
            return C_DARK_GREEN, C_DARK_GREEN
        return C_BLACK, C_BLACK


# ── Main application ──────────────────────────────────────────────────────────

class CloudbitsApp(App):

    CSS = """
    Screen {
        align: center middle;
        background: black;
    }

    #main-container {
        width: 136;
        height: 44;
        layout: vertical;
        background: black;
    }

    /* title */
    #title-area  { height: 3; }
    .title-blank { height: 1; }
    #title-row   { height: 1; content-align: center middle; text-align: center; }

    /* header */
    #header-controls { height: 4; layout: horizontal; }
    #left-header     { width: 35; layout: horizontal; }
    #center-header   { width: 66; layout: horizontal; }
    #right-header    { width: 35; layout: horizontal; }

    /* header control box widths */
    .hb-grid    { width: 9; }
    .hb-save    { width: 7; }
    .hb-rowcol  { width: 13; }
    .hb-build   { width: 9; }
    .hb-sat     { width: 12; }
    .hb-plus    { width: 5; }
    .hb-flip    { width: 6; }
    .hb-edit    { width: 6; }
    .hb-include { width: 9; }
    .hb-keep    { width: 8; }
    .hb-hist    { width: 11; }

    /* spacers */
    .sp-1  { width: 1; }
    .sp-2  { width: 2; }
    .sp-3  { width: 3; }
    .sp-11 { width: 11; }
    .sp-17 { width: 17; }

    /* main content */
    #main-content  { height: 33; layout: horizontal; }
    #left-panel    { width: 35; layout: vertical; background: black; }
    #center-panel  { width: 66; layout: vertical; }
    #right-panel   { width: 35; layout: vertical; background: black; }

    /* grid assembly */
    #grid-with-margins { height: 33; layout: horizontal; }
    #left-grid-margin  { width: 2;  background: #008700; }
    #right-grid-margin { width: 2;  background: #008700; }
    #grid-core         { width: 62; layout: vertical; }
    #top-margin        { height: 1; background: #008700; }
    #bottom-margin     { height: 1; background: #008700; }
    #grid-container    { height: 31; background: black; }

    /* footer */
    #footer      { height: 4; layout: vertical; }
    #comb-area   { height: 2; background: $accent; content-align: center middle; }
    #status-area { height: 2; background: $primary; layout: vertical; padding-left: 1; }
    #status-text { height: 2; content-align: left middle; }
    #save-input  { height: 2; display: none; background: $primary; }
    """

    def __init__(self) -> None:
        super().__init__()
        self._state      = AppState()
        self._mode_mgr   = ModeManager(self._state)
        self._cells      = CellSetManager()
        self._cursor     = CursorController(self._state)
        self._history    = HistoryManager()
        self._validation = ValidationEngine()
        self._files      = FileManager()
        self._save_pending = False

    # ── layout ───────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        with Container(id="main-container"):

            with Container(id="title-area"):
                yield Static("", classes="title-blank")
                yield Static(
                    "c    l    o    u    d    b    i    t    s",
                    id="title-row",
                )
                yield Static("", classes="title-blank")

            with Horizontal(id="header-controls"):
                with Horizontal(id="left-header"):
                    yield Static(self._box("GRID",  "G", 9), classes="hb-grid",  id="ctrl-grid")
                    yield Container(classes="sp-2")
                    yield Static(self._box("saVe",  "V", 7), classes="hb-save",  id="ctrl-save")
                    yield Container(classes="sp-17")

                with Horizontal(id="center-header"):
                    yield Static(
                        self._box("Row  Col\n  0    0", "", 13),
                        classes="hb-rowcol", id="ctrl-rowcol",
                    )
                    yield Container(classes="sp-2")
                    yield Static(self._box("Build",     "B",  9), classes="hb-build",   id="ctrl-build")
                    yield Container(classes="sp-1")
                    yield Static(self._box("Satellite", "S", 12), classes="hb-sat",     id="ctrl-sat")
                    yield Container(classes="sp-1")
                    yield Static(self._box("+",         "+",  5), classes="hb-plus",    id="ctrl-plus")
                    yield Static(self._box("Flip",      "F",  6), classes="hb-flip",    id="ctrl-flip")
                    yield Container(classes="sp-1")
                    yield Static(self._box("Edit",      "E",  6), classes="hb-edit",    id="ctrl-edit")
                    yield Container(classes="sp-1")
                    yield Static(self._box("Include",   "I",  9), classes="hb-include", id="ctrl-include")

                with Horizontal(id="right-header"):
                    yield Container(classes="sp-3")
                    yield Static(self._box("Keep",    "K",  8), classes="hb-keep", id="ctrl-keep")
                    yield Container(classes="sp-2")
                    yield Static(self._box("History", "H", 11), classes="hb-hist", id="ctrl-hist")
                    yield Container(classes="sp-11")

            with Horizontal(id="main-content"):

                # left panel: Pattern Library placeholder (Phase 4)
                with Vertical(id="left-panel"):
                    yield Static(self._panel_header("PATTERN LIBRARY"))
                    yield Static(" INTEGERS   PATTERNS")

                # centre panel: grid with perimeter margins
                with Vertical(id="center-panel"):
                    with Horizontal(id="grid-with-margins"):
                        yield Container(id="left-grid-margin")
                        with Vertical(id="grid-core"):
                            yield Container(id="top-margin")
                            with Container(id="grid-container"):
                                yield GridWidget(self._state, self._cells)
                            yield Container(id="bottom-margin")
                        yield Container(id="right-grid-margin")

                # right panel: History, Validation, Notes
                with Vertical(id="right-panel"):
                    yield Static(self._panel_header("HISTORY"))
                    yield Static("K snapshots: 0", id="k-count")
                    yield Static(self._panel_header("VALIDATION"))
                    yield Static("—", id="val-counter")
                    yield Static(self._panel_header("NOTES / TAGS"))

            with Vertical(id="footer"):
                yield Static("── COMB ──", id="comb-area")
                with Container(id="status-area"):
                    yield Static(
                        "BUILD  ·  ARROWS move   SPACE toggle   K keep   V save",
                        id="status-text",
                    )
                    yield Input(
                        placeholder="filename (.ptn auto-added)",
                        id="save-input",
                        disabled=True,
                    )

    # ── startup ──────────────────────────────────────────────────────────────

    def on_mount(self) -> None:
        size = self.console.size
        if size.width < 136 or size.height < 44:
            self.exit(
                message=(
                    f"Cloudbits requires a 136×44 terminal.\n"
                    f"Current: {size.width}×{size.height}\n"
                    f"Use fullscreen (F11) or reduce font size (Ctrl -)."
                )
            )

    # ── key handling ─────────────────────────────────────────────────────────

    def on_key(self, event) -> None:
        key = event.key

        # while save prompt is open, only Escape is handled here;
        # all other input goes to the Input widget
        if self._save_pending:
            if key == "escape":
                self._cancel_save()
            return

        if key == "up":
            self._cursor.move(1, 0)
        elif key == "down":
            self._cursor.move(-1, 0)
        elif key == "left":
            self._cursor.move(0, 1)
        elif key == "right":
            self._cursor.move(0, -1)
        elif key == "space":
            r, c = self._cursor.position
            if (r, c) != (0, 0):
                self._cells.toggle_build_cell(r, c)
        elif key == "k":
            self._do_keep()
            return
        elif key == "v":
            self._begin_save()
            return
        else:
            return

        self._sync_rowcol()
        self._sync_validation()
        self.query_one(GridWidget).refresh()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if not self._save_pending:
            return
        filename = event.value.strip()
        if filename:
            self._do_save(filename)
        else:
            self._cancel_save()

    # ── save flow ─────────────────────────────────────────────────────────────

    def _begin_save(self) -> None:
        self._save_pending = True
        save_input = self.query_one("#save-input", Input)
        if self._state.bingo:
            multiplier = int(self._state.validation_ratio)
            save_input.value = f"I{multiplier}"
            prompt = (
                f"INTEGER save (×{multiplier})  ·  "
                f"Edit filename then Enter, or Esc to cancel:"
            )
        else:
            save_input.value = ""
            prompt = "PATTERN save  ·  Enter filename then Enter, or Esc to cancel:"
        self.query_one("#status-text", Static).update(prompt)
        save_input.disabled = False
        self.query_one("#save-input").display = True
        self.query_one("#save-input").focus()

    def _do_save(self, filename: str) -> None:
        coords = [[r, c] for r, c in self._cells.build_cells]
        cur_r, cur_c = self._cursor.position
        try:
            path = self._files.save_pattern(
                filename=filename,
                coordinates=coords,
                handle=(cur_r, cur_c),
                pattern_type="build",
                is_integer=self._state.bingo,
                multiplier=self._state.validation_ratio,
                testbed_seed=self._validation._seed,
                source_history_state=self._state.k_count,
            )
            saved_name = os.path.basename(path)
            self._cancel_save()
            self._set_status(f"Saved  ·  {saved_name}  ({len(coords)} cells)")
        except Exception as exc:
            self._cancel_save()
            self._set_status(f"Save failed: {exc}")

    def _cancel_save(self) -> None:
        self._save_pending = False
        self.query_one("#save-input").display = False
        save_input_w = self.query_one("#save-input", Input)
        save_input_w.disabled = True
        save_input_w.value = ""
        self._restore_status()

    def _restore_status(self) -> None:
        self._set_status(
            "BUILD  ·  ARROWS move   SPACE toggle   K keep   V save"
        )

    def _set_status(self, msg: str) -> None:
        self.query_one("#status-text", Static).update(msg)

    # ── K snapshot ────────────────────────────────────────────────────────────

    def _do_keep(self) -> None:
        snapshot = Snapshot(
            build_cells=frozenset(self._cells.build_cells),
            cursor_row=self._state.cursor_row,
            cursor_col=self._state.cursor_col,
            mode=self._state.mode.value,
            bingo=self._state.bingo,
            validation_ratio=self._state.validation_ratio,
        )
        count = self._history.keep(snapshot)
        self._state.k_count = count
        self.query_one("#k-count", Static).update(f"K snapshots: {count}")
        self._set_status(f"BUILD  ·  Kept state {count}")

    # ── UI sync ───────────────────────────────────────────────────────────────

    def _sync_rowcol(self) -> None:
        r, c = self._cursor.position
        self.query_one("#ctrl-rowcol", Static).update(
            self._box(f"Row  Col\n{r:4d} {c:4d}", "", 13)
        )

    def _sync_validation(self) -> None:
        ratio, bingo = self._validation.validate(self._cells.build_cells)
        self._state.validation_ratio = ratio
        self._state.bingo = bingo

        if not self._cells.build_cells:
            display = "—"
        elif bingo:
            n = int(ratio)
            display = f"[bold #ff8700]BINGO  ×{n}[/]"
        else:
            display = f"{ratio:.6g}"

        self.query_one("#val-counter", Static).update(display)

    # ── helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _box(label: str, key: str, width: int) -> str:
        content = f"{label}\n {key}" if key else label
        lines = content.split("\n")
        inner = width - 2
        top    = "┌" + "─" * inner + "┐"
        bottom = "└" + "─" * inner + "┘"
        rows = [top]
        for line in lines:
            rows.append(f"│{line.center(inner)}│")
        rows.append(bottom)
        return "\n".join(rows)

    @staticmethod
    def _panel_header(title: str) -> str:
        dashes = max(0, 31 - len(title))
        return f"─ {title} " + "─" * dashes


def main() -> None:
    CloudbitsApp().run()


if __name__ == "__main__":
    main()
