from dataclasses import dataclass
from enum import Enum


class Mode(Enum):
    BUILD = "B"
    SATELLITE = "S"
    HISTORY = "H"
    GRID_BG = "G"


@dataclass
class AppState:
    mode: Mode = Mode.BUILD
    cursor_row: int = 0
    cursor_col: int = 0
    bingo: bool = False
    validation_ratio: float = 0.0
    k_count: int = 0
    # S mode
    sat_phase: str = "draw"    # "draw" or "move"
    handle_row: int = 0
    handle_col: int = 0
    draw_row: int = 0
    draw_col: int = 0
