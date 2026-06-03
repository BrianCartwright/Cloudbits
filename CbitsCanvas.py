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
from cloudbits.cell_set_manager import CellSetManager, SatelliteSet
from cloudbits.cursor_controller import CursorController, GRID_MIN, GRID_MAX
from cloudbits.history_manager import HistoryManager, Snapshot
from cloudbits.validation_engine import ValidationEngine
from cloudbits.file_manager import FileManager, SessionFolder

# ── colour palette (xterm-256) ────────────────────────────────────────────────
C_ORANGE      = Color.from_ansi(208)   # Build cursor
C_DARK_GREEN  = Color.from_ansi(28)   # Build cells + B-mode margin
C_GRAY_BLUE   = Color.from_ansi(67)   # Handle / RefCell
C_BLACK       = Color.from_ansi(0)    # Grid background
C_DRAW        = Color.from_ansi(110)  # #87afd7  Draw cursor
C_SAT         = Color.from_ansi(32)   # Satellite cells
C_BRIGHT_GREEN = Color.from_ansi(40)  # Handle-selected; S+B overlap

# ── S mode command bar text ────────────────────────────────────────────────────
_CMD_BUILD = (
    "[cyan]B[/]uild    [cyan]S[/]atellite    [cyan]F[/]lip  ·  ·"
    "  [cyan]  +  [/]    [cyan]E[/]dit   [cyan]I[/]nclude"
)
_CMD_SAT       = "[cyan]D[/]raw   [cyan]M[/]ove   [cyan]  +  [/]   [cyan]I[/]nclude"
_CMD_SAT_FLASH = "[cyan]D[/]raw   [cyan]M[/]ove   [cyan]  +  [/]   [bold white]I[/]nclude"

# Arrow key → (Δrow, Δcol) matching existing cursor convention
_SAT_DIRS = {"up": (1, 0), "down": (-1, 0), "left": (0, 1), "right": (0, -1)}


# ── Grid widget ───────────────────────────────────────────────────────────────

class GridWidget(Widget):
    """
    31×31 chexel canvas.  Each grid cell maps to two terminal chars (▀▄)
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
        for grid_col in range(15, -16, -1):
            primary, secondary = self._cell_colors(grid_row, grid_col)
            style = Style(color=primary, bgcolor=secondary)
            segments.append(Segment("▀", style))
            segments.append(Segment("▄", style))
        return Strip(segments)

    def _cell_colors(self, row: int, col: int) -> tuple:
        is_refcell = (row == 0 and col == 0)
        is_build   = (row, col) in self._cells.build_cells

        if self._state.mode == Mode.SATELLITE:
            is_handle = (row == self._state.handle_row
                         and col == self._state.handle_col)
            is_draw   = (self._state.sat_phase == "draw"
                         and row == self._state.draw_row
                         and col == self._state.draw_col)
            active  = self._cells.active_satellite
            is_sat  = (active is not None and (row, col) in active.coordinates)

            if is_draw:
                if is_sat and is_build:
                    bg = C_BRIGHT_GREEN
                elif is_sat:
                    bg = C_BRIGHT_GREEN if is_handle else C_SAT
                elif is_handle:
                    bg = C_GRAY_BLUE
                elif is_build:
                    bg = C_DARK_GREEN
                elif is_refcell:
                    bg = C_GRAY_BLUE
                else:
                    bg = C_DRAW
                return C_DRAW, bg

            if is_handle:
                return C_GRAY_BLUE, (C_BRIGHT_GREEN if is_sat else C_GRAY_BLUE)
            if is_sat and is_build:
                return C_BRIGHT_GREEN, C_DARK_GREEN
            if is_sat:
                return C_SAT, C_SAT
            if is_refcell:
                return C_GRAY_BLUE, C_GRAY_BLUE
            if is_build:
                return C_DARK_GREEN, C_DARK_GREEN
            return C_BLACK, C_BLACK

        # B mode / H mode — orange cursor hidden in H mode
        is_cursor = (self._state.mode != Mode.HISTORY
                     and row == self._state.cursor_row
                     and col == self._state.cursor_col)
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
        height: 40;
        layout: vertical;
        background: black;
    }

    /* title + command bar */
    #title-area  { height: 3; }
    #title-blank { height: 1; }
    #title-row   { height: 1; content-align: center middle; text-align: center; }

    /* command bar (row 3) */
    #cmd-bar    { height: 1; layout: horizontal; }
    #cmd-left   { width: 35; content-align: center middle; }
    #cmd-center { width: 66; layout: horizontal; }
    #cmd-right  { width: 35; layout: horizontal; }

    /* width utilities (command bar items and spacers) */
    .w1   { width: 1;   }
    .w4   { width: 4;   }
    .w5   { width: 5;   }
    .w6   { width: 6;   }
    .w7   { width: 7;   }
    .w9   { width: 9;   }
    .w13  { width: 13;  }
    #cmd-center-label { width: 1fr; content-align: center middle; }

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

    /* right panel: row/col counter aligned to grid row 0 */
    #rowcol-spacer { height: 9; }

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
        self._history_index: int = 0
        self._pre_history_cells: set = set()
        self._pre_history_cursor: tuple = (0, 0)
        self._restore_pending: bool = False
        self._session: object = None       # SessionFolder, created on first K
        self._last_tsv_name: str = ""
        self._tag_eligible: bool = False   # True briefly after K, allows T
        self._tagging: bool = False        # True while KT tag input is open
        self._sat_exit_pending: bool = False
        self._sat_illegal: bool = False

    # ── layout ───────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        with Container(id="main-container"):

            with Container(id="title-area"):
                yield Static(
                    "c    l    o    u    d    b    i    t    s",
                    id="title-row",
                )
                yield Static("", id="title-blank")
                with Horizontal(id="cmd-bar"):
                    # Left (35): saVe only, centered above Pattern Library
                    yield Static("sa[cyan]V[/]e", id="cmd-left")

                    # Center (66): mode-sensitive command bar
                    with Horizontal(id="cmd-center"):
                        yield Static(_CMD_BUILD, id="cmd-center-label")

                    # Right (35): Keep History, positions match old box centres
                    with Horizontal(id="cmd-right"):
                        yield Container(classes="w5")
                        yield Static("[cyan]K[/]eep",    classes="w4")
                        yield Container(classes="w6")
                        yield Static("[cyan]H[/]istory", classes="w7")
                        yield Container(classes="w13")

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

                # right panel: History, Validation, Notes, Row/Col counter
                with Vertical(id="right-panel"):
                    yield Static(self._panel_header("HISTORY"))
                    yield Static("K snapshots: 0", id="k-count")
                    yield Static(self._panel_header("VALIDATION"))
                    yield Static("—", id="val-counter")
                    yield Static(self._panel_header("NOTES / TAGS"))
                    yield Container(id="rowcol-spacer")
                    yield Static(
                        self._box("Row  Col\n  0    0", "", 13),
                        id="ctrl-rowcol",
                    )

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
        if size.width < 136 or size.height < 40:
            self.exit(
                message=(
                    f"Cloudbits requires a 136×40 terminal.\n"
                    f"Current: {size.width}×{size.height}\n"
                    f"Use fullscreen (F11) or reduce font size (Ctrl -)."
                )
            )

    # ── key handling ─────────────────────────────────────────────────────────

    def on_key(self, event) -> None:
        key = event.key

        if self._save_pending:
            if key == "escape":
                self._cancel_save()
            return

        if self._tagging:
            if key == "escape":
                self._cancel_tag()
            return  # all other input goes to the Input widget

        # H mode: slideshow navigation only — all other keys are blocked
        if self._state.mode == Mode.HISTORY:
            if self._restore_pending:
                if key in ("return", "enter", "ctrl+m"):
                    self._confirm_restore()
                else:
                    self._restore_pending = False
                    self._load_snapshot(self._history_index)
            elif key == "h":
                self._exit_history()
            elif key == "left":
                self._history_step(-1)
            elif key == "right":
                self._history_step(1)
            elif key in ("return", "enter", "ctrl+m"):
                self._begin_restore()
            return

        # S mode
        if self._state.mode == Mode.SATELLITE:
            if self._sat_exit_pending:
                if key == "b":
                    self._do_exit_satellite()
                else:
                    self._sat_exit_pending = False
                    self._update_sat_status()
            elif key == "b":
                self._begin_exit_satellite()
            elif key in ("up", "down", "left", "right"):
                if self._state.sat_phase == "draw":
                    self._sat_draw_move(key)
                else:
                    self._sat_move_handle(key)
            elif key == "space":
                if self._state.sat_phase == "draw":
                    self._sat_toggle_cell()
            elif key in ("return", "enter", "ctrl+m"):
                self._sat_toggle_phase()
            elif key == "i":
                if not self._sat_illegal:
                    self._do_include()
            return

        # KT: if K was just pressed and T follows, begin tagging
        if self._tag_eligible:
            self._tag_eligible = False
            if key == "t":
                self._begin_tag()
                return
            # any other key: fall through and process normally

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
        elif key == "h":
            if self._history.count > 0:
                self._enter_history()
            return
        elif key == "s":
            self._enter_satellite()
            return
        else:
            return

        self._sync_rowcol()
        self._sync_validation()
        self.query_one(GridWidget).refresh()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if self._save_pending:
            filename = event.value.strip()
            if filename:
                self._do_save(filename)
            else:
                self._cancel_save()
        elif self._tagging:
            text = event.value.strip()
            if text:
                self._confirm_tag(text)
            else:
                self._cancel_tag()

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

    # ── KT tag flow ───────────────────────────────────────────────────────────

    def _begin_tag(self) -> None:
        self._tagging = True
        inp = self.query_one("#save-input", Input)
        inp.value = ""
        inp.disabled = False
        self.query_one("#save-input").display = True
        self.query_one("#save-input").focus()
        self._set_status(
            f"Tag for {self._last_tsv_name}  ·  Enter to save   Esc to cancel:"
        )

    def _confirm_tag(self, text: str) -> None:
        self._session.write_tag(self._last_tsv_name, text)
        self._tagging = False
        inp = self.query_one("#save-input", Input)
        inp.disabled = True
        inp.value = ""
        self.query_one("#save-input").display = False
        txt_name = self._last_tsv_name[:-4] + ".txt"
        self._set_status(f"Tagged: {txt_name}")

    def _cancel_tag(self) -> None:
        self._tagging = False
        inp = self.query_one("#save-input", Input)
        inp.disabled = True
        inp.value = ""
        self.query_one("#save-input").display = False
        self._restore_status()

    def _restore_status(self) -> None:
        self._set_status(
            "BUILD  ·  ARROWS move   SPACE toggle   S satellite   K to Keep  KT to tag"
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
        if self._session is None:
            self._session = SessionFolder()
        coeff = self._validation.coeff_sum(self._cells.build_cells)
        self._last_tsv_name = self._session.write_tsv(
            GRID_MAX, self._cells.build_cells, coeff
        )
        self._tag_eligible = (self._state.mode == Mode.BUILD)
        self._set_status(f"Kept: {self._last_tsv_name}  ·  T to tag")

    # ── H mode (history slideshow) ────────────────────────────────────────────

    def _enter_history(self) -> None:
        self._pre_history_cells = set(self._cells.build_cells)
        self._pre_history_cursor = self._cursor.position
        self._history_index = self._history.count - 1
        self._mode_mgr.enter_history()
        self._load_snapshot(self._history_index)

    def _exit_history(self) -> None:
        self._restore_pending = False
        self._mode_mgr.exit_history()
        self._cells.build_cells = self._pre_history_cells
        self._state.cursor_row, self._state.cursor_col = self._pre_history_cursor
        self._sync_rowcol()
        self._sync_validation()
        self.query_one(GridWidget).refresh()
        self._restore_status()

    def _history_step(self, delta: int) -> None:
        new_index = self._history_index + delta
        if 0 <= new_index < self._history.count:
            self._history_index = new_index
            self._load_snapshot(self._history_index)

    def _begin_restore(self) -> None:
        self._restore_pending = True
        n = self._history_index + 1
        discard = self._history.count - n
        if discard > 0:
            tail = f"subsequent state{'s' if discard != 1 else ''}"
            msg = (f"HISTORY  ·  Restore snapshot {n} and discard "
                   f"{discard} {tail}?  Return to confirm   H to cancel")
        else:
            msg = (f"HISTORY  ·  Restore snapshot {n} as current build "
                   f"state?  Return to confirm   H to cancel")
        self._set_status(msg)

    def _confirm_restore(self) -> None:
        snap = self._history.snapshots[self._history_index]
        self._history.truncate_after(self._history_index)
        self._restore_pending = False
        self._mode_mgr.exit_history()
        self._cells.build_cells = set(snap.build_cells)
        self._state.cursor_row = 0
        self._state.cursor_col = 0
        count = self._history.count
        self._state.k_count = count
        self.query_one("#k-count", Static).update(f"K snapshots: {count}")
        self._sync_rowcol()
        self._sync_validation()
        self.query_one(GridWidget).refresh()
        self._restore_status()

    def _load_snapshot(self, index: int) -> None:
        snap = self._history.snapshots[index]
        self._cells.build_cells = set(snap.build_cells)
        self._state.cursor_row = snap.cursor_row
        self._state.cursor_col = snap.cursor_col
        n, total = index + 1, self._history.count
        self._set_status(
            f"HISTORY  ·  {n} of {total}  ·  ← → browse   H to exit"
        )
        self._sync_rowcol()
        self._sync_validation()
        self.query_one(GridWidget).refresh()

    # ── S mode (Satellite) ───────────────────────────────────────────────────

    def _enter_satellite(self) -> None:
        sat = SatelliteSet()
        self._cells.satellite_sets = [sat]
        self._cells._active_idx = 0
        self._state.handle_row = self._state.cursor_row
        self._state.handle_col = self._state.cursor_col
        self._state.draw_row   = self._state.cursor_row
        self._state.draw_col   = self._state.cursor_col
        self._state.sat_phase  = "draw"
        self._state.mode       = Mode.SATELLITE
        self._sat_illegal      = False
        self._update_cmd_center()
        self._update_sat_status()
        self._sync_rowcol()
        self.query_one(GridWidget).refresh()

    def _begin_exit_satellite(self) -> None:
        active = self._cells.active_satellite
        if active and active.coordinates:
            self._sat_exit_pending = True
            self._set_status(
                "SATELLITE set non-empty  ·  B again to exit and discard   other key to stay"
            )
        else:
            self._do_exit_satellite()

    def _do_exit_satellite(self) -> None:
        self._sat_exit_pending = False
        self._state.cursor_row = self._state.handle_row
        self._state.cursor_col = self._state.handle_col
        self._cells.satellite_sets = []
        self._cells._active_idx   = -1
        self._state.mode          = Mode.BUILD
        self._sat_illegal         = False
        self._update_cmd_center()
        self._sync_rowcol()
        self._restore_status()
        self.query_one(GridWidget).refresh()

    def _sat_draw_move(self, key: str) -> None:
        dr, dc = _SAT_DIRS[key]
        new_r = self._state.draw_row + dr
        new_c = self._state.draw_col + dc
        if GRID_MIN <= new_r <= GRID_MAX and GRID_MIN <= new_c <= GRID_MAX:
            self._state.draw_row = new_r
            self._state.draw_col = new_c
        self._sync_rowcol()
        self.query_one(GridWidget).refresh()

    def _sat_toggle_cell(self) -> None:
        r, c   = self._state.draw_row, self._state.draw_col
        active = self._cells.active_satellite
        if active is None:
            return
        if (r, c) in active.coordinates:
            active.coordinates.discard((r, c))
        else:
            active.coordinates.add((r, c))
        self._check_sat_legality()
        self.query_one(GridWidget).refresh()

    def _sat_move_handle(self, key: str) -> None:
        dr, dc     = _SAT_DIRS[key]
        active     = self._cells.active_satellite
        sat_coords = active.coordinates if active else set()
        new_hr = self._state.handle_row + dr
        new_hc = self._state.handle_col + dc
        if not (GRID_MIN <= new_hr <= GRID_MAX and GRID_MIN <= new_hc <= GRID_MAX):
            return
        for r, c in sat_coords:
            if not (GRID_MIN <= r + dr <= GRID_MAX and GRID_MIN <= c + dc <= GRID_MAX):
                return
        self._state.handle_row = new_hr
        self._state.handle_col = new_hc
        if active:
            active.coordinates = {(r + dr, c + dc) for r, c in sat_coords}
        self._check_sat_legality()
        self._sync_rowcol()
        self.query_one(GridWidget).refresh()

    def _sat_toggle_phase(self) -> None:
        if self._state.sat_phase == "draw":
            self._state.sat_phase = "move"
        else:
            self._state.sat_phase  = "draw"
            self._state.draw_row   = self._state.handle_row
            self._state.draw_col   = self._state.handle_col
        self._update_sat_status()
        self._sync_rowcol()
        self.query_one(GridWidget).refresh()

    def _check_sat_legality(self) -> None:
        active = self._cells.active_satellite
        if not active:
            self._sat_illegal = False
            return
        build = self._cells.build_cells
        for r, c in active.coordinates:
            for dr, dc in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                if (r + dr, c + dc) in build:
                    self._sat_illegal = True
                    return
        self._sat_illegal = False

    def _do_include(self) -> None:
        active = self._cells.active_satellite
        if active is None or self._sat_illegal:
            return
        for r, c in active.coordinates:
            self._cells.build_cells.add((r, c))
        self._do_keep()
        self._tag_eligible = False
        self.query_one("#cmd-center-label", Static).update(_CMD_SAT_FLASH)
        self.set_timer(0.4, self._restore_cmd_center)
        self._set_status(f"SATELLITE  ·  Included → {self._last_tsv_name}")
        self._check_sat_legality()
        self._sync_validation()
        self.query_one(GridWidget).refresh()

    def _update_cmd_center(self) -> None:
        text = _CMD_SAT if self._state.mode == Mode.SATELLITE else _CMD_BUILD
        self.query_one("#cmd-center-label", Static).update(text)

    def _restore_cmd_center(self) -> None:
        if self._state.mode == Mode.SATELLITE:
            self.query_one("#cmd-center-label", Static).update(_CMD_SAT)

    def _update_sat_status(self) -> None:
        if self._state.sat_phase == "draw":
            self._set_status(
                "SATELLITE DRAW  ·  ARROWS move cursor   SPACE toggle"
                "   Return → Move   I include"
            )
        else:
            self._set_status(
                "SATELLITE MOVE  ·  ARROWS move set   Return → Draw   I include"
            )

    # ── UI sync ───────────────────────────────────────────────────────────────

    def _sync_rowcol(self) -> None:
        if self._state.mode == Mode.SATELLITE:
            if self._state.sat_phase == "draw":
                r, c = self._state.draw_row, self._state.draw_col
            else:
                r, c = self._state.handle_row, self._state.handle_col
        else:
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
