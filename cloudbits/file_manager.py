"""
Phase 2: .ptn JSON file I/O, filename prompt, Bingo-gated integer save.
Phase 14.2: session restore (grid state only).
"""
import json
import os
from datetime import datetime, timezone

PTN_VERSION = "1.0"


class FileManager:

    def __init__(self, library_dir: str = "") -> None:
        self._library_dir = library_dir or os.path.join(
            os.path.expanduser("~"), ".cloudbits", "patterns"
        )

    @property
    def library_dir(self) -> str:
        return self._library_dir

    def save_pattern(
        self,
        filename: str,
        coordinates: list,
        handle: tuple,
        pattern_type: str,
        is_integer: bool,
        multiplier: float,
        source_history_state: int = 0,
    ) -> str:
        """Write a .ptn file. Returns the full path written."""
        os.makedirs(self._library_dir, exist_ok=True)
        if not filename.endswith(".ptn"):
            filename += ".ptn"
        path = os.path.join(self._library_dir, filename)
        data = {
            "cloudbits_version": PTN_VERSION,
            "pattern": {
                "coordinates": coordinates,
                "handle": list(handle),
                "pattern_type": pattern_type,
                "flip_variants": "both",
            },
            "validation": {
                "is_integer": is_integer,
                "multiplier": multiplier,
                "comb_value": None,
            },
            "session_data": {
                "created": datetime.now(timezone.utc).isoformat(),
                "source_history_state": source_history_state,
            },
        }
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
        return path

    def load_pattern(self, path: str) -> dict:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)

    def list_patterns(self) -> list:
        """Returns sorted list of .ptn filenames in library_dir."""
        if not os.path.isdir(self._library_dir):
            return []
        return sorted(f for f in os.listdir(self._library_dir) if f.endswith(".ptn"))


class SessionFolder:
    """
    One timestamped folder per app session.  On first K, a folder is created
    under ~/.cloudbits/sessions/<YYYYMMDD_HHMMSS>/.  Each K writes the next
    kNNN.tsv; an optional KT tag writes a sidecar kNNN.txt.

    TSV format (no headers):
        line 1          grid half-size (integer)
        lines 2..N-1    occupied cell coords, one per line: row<TAB>col
        line N          CoeffTuple: ca<TAB>cb<TAB>cc<TAB>cd
    """

    _BASE = os.path.join(os.path.expanduser("~"), ".cloudbits", "sessions")

    def __init__(self, base_dir: str = "") -> None:
        root = base_dir or self._BASE
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._dir = os.path.join(root, ts)
        os.makedirs(self._dir, exist_ok=True)
        self._count = 0

    @property
    def directory(self) -> str:
        return self._dir

    def write_tsv(self, grid_half: int, cells, coeff: tuple) -> str:
        """Write the next kNNN.tsv and return its filename."""
        self._count += 1
        name = f"k{self._count:03d}.tsv"
        rows = [str(grid_half)]
        for r, c in sorted(cells):
            rows.append(f"{r}\t{c}")
        rows.append("\t".join(str(v) for v in coeff))
        with open(os.path.join(self._dir, name), "w", encoding="utf-8") as fh:
            fh.write("\n".join(rows) + "\n")
        return name

    def write_tag(self, tsv_name: str, text: str) -> None:
        """Write a sidecar kNNN.txt alongside the given TSV."""
        txt_name = tsv_name[:-4] + ".txt"
        with open(os.path.join(self._dir, txt_name), "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
