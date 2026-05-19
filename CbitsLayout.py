"""
Cloudbits - 2D Fibonacci Pattern Explorer
Phase 2: Complete layout implementation (Fixed v3)
"""
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static


class CloudbitsApp(App):
    """Main Cloudbits application."""
    
    CSS = """
    Screen {
        align: center middle;
        background: black;
    }
    
    #main-container {
        width: 136;
        height: 44;
        background: $surface;
        layout: vertical;
    }
    
    /* Title area */
    #title-area {
        height: 3;
        background: $surface;
    }
    
    .title-blank {
        height: 1;
    }
    
    #title-row {
        height: 1;
        content-align: center middle;
        text-align: center;
    }
    
    /* Header controls */
    #header-controls {
        height: 4;
        layout: horizontal;
    }
    
    #left-header {
        width: 35;
        content-align: center middle;
        text-align: center;
    }
    
    #center-header {
        width: 66;
        content-align: center middle;
    }
    
    .header-spacer-3 {
        width: 3;
    }
    
    .header-spacer-2 {
        width: 2;
    }
    
    .header-control-12 {
        width: 12;
    }
    
    .header-control-24 {
        width: 24;
    }
    
    .header-control-6 {
        width: 6;
    }
    
    .header-control-9 {
        width: 9;
    }
    
    #right-header {
        width: 35;
        content-align: center middle;
        text-align: center;
    }
    
    /* Main content area */
    #main-content {
        height: 33;
        layout: horizontal;
    }
    
    #left-panel {
        width: 35;
        layout: vertical;
    }
    
    #browser-slots {
        height: 33;
        layout: vertical;
        content-align: center top;
    }
    
    .browser-pair {
        height: 4;
        layout: horizontal;
        content-align: center middle;
    }
    
    .slot-spacer {
        width: 1;
    }
    
    .browser-slot-16 {
        width: 16;
    }
    
    #center-panel {
        width: 66;
        layout: vertical;
    }
    
    #grid-with-margins {
        height: 33;
        layout: horizontal;
    }
    
    #left-grid-margin {
        width: 2;
        background: $panel-lighten-1;
    }
    
    #grid-core {
        width: 62;
        layout: vertical;
    }
    
    #right-grid-margin {
        width: 2;
        background: $panel-lighten-1;
    }
    
    #top-margin {
        height: 1;
        background: $panel-lighten-1;
    }
    
    #grid-container {
        height: 31;
        background: $panel;
        content-align: center middle;
    }
    
    #bottom-margin {
        height: 1;
        background: $panel-lighten-1;
    }
    
    #right-panel {
        width: 35;
        layout: vertical;
        content-align: center top;
    }
    
    #history-toggle {
        height: 4;
        content-align: center middle;
        text-align: center;
    }
    
    #state-counter {
        height: 4;
        content-align: center middle;
        text-align: center;
    }
    
    #layer-counter {
        height: 4;
        content-align: center middle;
        text-align: center;
    }
    
    #right-commands {
        height: 4;
        content-align: center middle;
    }
    
    .right-commands-spacer-left {
        width: 2;
    }
    
    .command-spacer {
        width: 1;
    }
    
    .command-6 {
        width: 6;
    }
    
    .command-8 {
        width: 8;
    }
    
    .command-7 {
        width: 7;
    }
    
    #text-entry {
        height: 6;
        content-align: center middle;
        text-align: center;
    }
    
    #empty-space {
        height: 6;
    }
    
    #bottom-counters {
        height: 4;
        content-align: center middle;
    }
    
    .counter-margin-left {
        width: 2;
    }
    
    .counter-gap {
        width: 1;
    }
    
    .counter-margin-right {
        width: 2;
    }
    
    .counter-17 {
        width: 17;
    }
    
    .counter-13 {
        width: 13;
    }
    
    /* Footer */
    #footer {
        height: 4;
        layout: vertical;
    }
    
    #comb-area {
        height: 2;
        background: $accent;
        content-align: center middle;
    }
    
    #status-area {
        height: 2;
        background: $primary;
        content-align: left middle;
        padding-left: 1;
    }
    """

    def compose(self) -> ComposeResult:
        """Create the complete layout."""
        with Container(id="main-container"):
            # Title area (rows 1-3)
            with Container(id="title-area"):
                yield Static("", classes="title-blank")
                yield Static("c    l    o    u    d    b    i    t    s", id="title-row")
                yield Static("", classes="title-blank")
            
            # Header controls (rows 4-7)
            with Horizontal(id="header-controls"):
                # Left header: saVe
                yield Static(self._make_box("saVe", "V", 6), id="left-header")
                
                # Center header: Multiple controls
                with Horizontal(id="center-header"):
                    yield Static(self._make_box("Row  Col\n-15  -15", "", 12), classes="header-control-12")
                    yield Container(classes="header-spacer-3")
                    yield Static(self._make_box("Build Satellite Assert\n  B       S        A", "", 24), classes="header-control-24")
                    yield Container(classes="header-spacer-2")
                    yield Static(self._make_box("Flip\n F", "", 6), classes="header-control-6")
                    yield Container(classes="header-spacer-2")
                    yield Static(self._make_box("Edit\n E", "", 6), classes="header-control-6")
                    yield Container(classes="header-spacer-2")
                    yield Static(self._make_box("Include\n   I", "", 9), classes="header-control-9")
                
                # Right header: Keep
                yield Static(self._make_box("Keep", "K", 6), id="right-header")
            
            # Main content (rows 8-40)
            with Horizontal(id="main-content"):
                # Left panel: Browser slots (start at row 8)
                with Vertical(id="left-panel"):
                    with Vertical(id="browser-slots"):
                        for i in range(8):
                            with Horizontal(classes="browser-pair"):
                                yield Static(self._make_browser_slot(".bld", 16), classes="browser-slot-16")
                                yield Container(classes="slot-spacer")
                                yield Static(self._make_browser_slot(".ast", 16), classes="browser-slot-16")
                
                # Center panel: Grid with margins on all sides
                with Vertical(id="center-panel"):
                    with Horizontal(id="grid-with-margins"):
                        yield Container(id="left-grid-margin")
                        with Vertical(id="grid-core"):
                            yield Static("", id="top-margin")
                            yield Static("GRID: 31×31 chexels\n(62 chars)", id="grid-container")
                            yield Static("", id="bottom-margin")
                        yield Container(id="right-grid-margin")
                
                # Right panel: History controls
                with Vertical(id="right-panel"):
                    yield Static(self._make_box("History", "H", 9), id="history-toggle")
                    yield Static(self._make_state_counter(), id="state-counter")
                    yield Static(self._make_layer_counter(), id="layer-counter")
                    
                    # Command boxes (Mark, Branch, Layer, saVe)
                    with Horizontal(id="right-commands"):
                        yield Container(classes="right-commands-spacer-left")
                        yield Static(self._make_box("Mark", "M", 6), classes="command-6")
                        yield Container(classes="command-spacer")
                        yield Static(self._make_box("Branch", "B", 8), classes="command-8")
                        yield Container(classes="command-spacer")
                        yield Static(self._make_box("Layer", "L", 7), classes="command-7")
                        yield Container(classes="command-spacer")
                        yield Static(self._make_box("saVe", "V", 6), classes="command-6")
                    
                    yield Static(self._make_text_entry(), id="text-entry")
                    yield Static("", id="empty-space")
                    
                    # Bottom counters
                    with Horizontal(id="bottom-counters"):
                        yield Container(classes="counter-margin-left")
                        yield Static(self._make_box("Pattern Ordinal\n   # _ _ _ _", "", 17), classes="counter-17")
                        yield Container(classes="counter-gap")
                        yield Static(self._make_box("  Binomial\n _ _ _ G _ _ _", "", 13), classes="counter-13")
                        yield Container(classes="counter-margin-right")
            
            # Footer (rows 41-44)
            with Vertical(id="footer"):
                yield Static("COMB: 2 rows (63 cells, -31 to +31)", id="comb-area")
                yield Static("Status: Messages and mode indicators", id="status-area")

    def _make_box(self, label: str, key: str, width: int) -> str:
        """Create a Rich box with label and keybinding."""
        if key:
            content = f"{label}\n {key}"
        else:
            content = label
        
        lines = content.split('\n')
        top = "┌" + "─" * (width - 2) + "┐"
        bottom = "└" + "─" * (width - 2) + "┘"
        
        result = [top]
        for line in lines:
            padded = line.center(width - 2)
            result.append(f"│{padded}│")
        result.append(bottom)
        
        return "\n".join(result)
    
    def _make_browser_slot(self, extension: str, width: int) -> str:
        """Create a browser slot box."""
        top = "┌" + "─" * (width - 2) + "┐"
        filename = "  Filename".center(width - 2)
        ext_line = f" {extension}".ljust(width - 2)
        bottom = "└" + "─" * (width - 2) + "┘"
        
        return f"{top}\n│{filename}│\n│{ext_line}│\n{bottom}"
    
    def _make_state_counter(self) -> str:
        """Create the state counter box."""
        width = 30
        top = "┌" + "─" * (width - 2) + "┐"
        label = "current      last".center(width - 2)
        counter = "< A17* (=B1)  X  A23* >".center(width - 2)
        bottom = "└" + "─" * (width - 2) + "┘"
        
        return f"{top}\n│{label}│\n│{counter}│\n{bottom}"
    
    def _make_layer_counter(self) -> str:
        """Create the layer counter box."""
        width = 30
        top = "┌" + "─" * (width - 2) + "┐"
        label = "current Layer    last".center(width - 2)
        counter = "B (from A8)      D".center(width - 2)
        bottom = "└" + "─" * (width - 2) + "┘"
        
        return f"{top}\n│{label}│\n│{counter}│\n{bottom}"
    
    def _make_text_entry(self) -> str:
        """Create the text entry box."""
        width = 33
        top = "┌" + "─" * (width - 2) + "┐"
        lines = ["Caption text...".ljust(width - 2) for _ in range(4)]
        result = [top]
        for line in lines:
            result.append(f"│{line}│")
        result.append("└" + "─" * (width - 2) + "┘")
        
        return "\n".join(result)

    def on_mount(self) -> None:
        """Check minimum terminal size on startup."""
        terminal_size = self.console.size
        cols = terminal_size.width
        rows = terminal_size.height
        
        MIN_COLS = 136
        MIN_ROWS = 44
        
        if cols < MIN_COLS or rows < MIN_ROWS:
            self.exit(
                message=f"Cloudbits requires at least {MIN_COLS}×{MIN_ROWS}.\n"
                        f"Current terminal: {cols}×{rows}\n"
                        f"Please use fullscreen mode (F11) or reduce font size (Ctrl-)."
            )


def main():
    """Entry point for the application."""
    app = CloudbitsApp()
    app.run()


if __name__ == "__main__":
    main()
