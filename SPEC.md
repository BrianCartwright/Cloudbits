## "think about" -- :edit!
# Cloudbits Design Specification v0.5

**Status:** Working draft — prepared for phased implementation
**Supersedes:** v0.1 through v0.4 and all Addenda

**Key changes in v0.5:**
- G mode (Grid Background) added as a new mode
- FRAC and checkerboard parity moved from always-on to G mode options
- All color values now provisional xterm-256 palette entries; 
  [SETTLED] removed from color decisions
- History streamlined: auto-Keep on H entry, asterisk marker for saved states
- Non-Included Satellite sets removed on B exit (with unsaved warning)
- Comb deferred to [PENDING]; removed from early phases
- Pattern Library identified as shared Nnumerics resource
- Handle cell selectable in S mode; Handle position stored in .ptn file
- Pattern loading (S mode): Handle remains active after commit for positioning
- Command-line argument for Pattern Library path; auto-save on shutdown added
- Footer key reminders added as general UI feature

---

## Status Markers

| Marker        |      Meaning                               |
|---------------|--------------------------------------------|
| [SETTLED]     | Confirmed design decision                  |
| [PROVISIONAL] | Likely, subject to testing or refinement   |
| [TBD]         | Decision needed                            |
| [PENDING]     | Concept defined, design deferred           |
| [DEFERRED]    | Explicitly postponed to a future version   |

---

## 1. Application Overview

**[SETTLED]** Cloudbits is a 2D Fibonacci Pattern Explorer — a standalone TUI 
application and detachable component of the Nnumerics desktop math sandbox. 

Its purposes are:

- Educational exploration of 2D Fibonacci sequences and recursive arithmetic
- Interactive visualization of G-Base representations in two dimensions
- A gateway application for community engagement with Nnumerics
- Generation and sharing of validated mathematical patterns

**[SETTLED]** Target platform: terminal TUI application, minimum 136 columns 
x 44 rows. No multi-screen or mobile considerations for this iteration. 
Future GUI development dependent on appropriate collaboration.

**[SETTLED]** Development methodology: Chat discussion -> Cowork Markdown 
specification -> Claude Code design critique -> phased implementation.

**[SETTLED]** Assert mode has been removed from the roadmap. Its validation 
concept belongs to a future analysis tool not yet designed. The mode group is 
B/S only.

---

## 2. Two-Layer Architecture

**[SETTLED]** The application is structured as two distinct layers. This 
specification describes the Python UX Logic Layer in full. Specific Textual 
widget choices are left to implementation.

### 2.1 Python UX Logic Layer

Domain :  Responsibilities

AppState : Current mode (B/S/H/G), cursor position, 
  active cell sets, validation state

ModeManager : B/S/H/G transitions, H suspension logic, Satellite count tracking

CellSetManager : Coordinate collections for Build and all Satellite sets; 
  active/inactive flags; Handle positions 

CursorController : Orange cursor (Build), Handle position(s) (Satellite)
  Edit cursor, boundary enforcement

ValidationEngine : Testbed sequence, unified integer validation, 
  legal pattern detection, Keep gating

CombEngine : Diagonal translation, bit representation, Pord computation [PENDING]

HistoryManager : Linear state timeline, K snapshots, H mode navigation 

FileWatcher : Monitors Pattern Library directory for external changes

PatternLibrary : Loads, parses, and indexes .ptn files

GridBackground : Active background elements, opacity levels, 
  daisy shift offset and Flip variant

**[SETTLED]** Cell sets are stored as separate coordinate collections — 
never as a single monolithic set. 
Each Satellite set carries: coordinates, active/inactive flag, 
Handle position, and animation state. 
This architecture is required from Phase 1 to avoid refactoring when multiple 
Satellites are added in Phase 3.

### 2.2 Textual Rendering Layer

A thin display wrapper. Its only job is to read from the Python layer and 
render current state. It does not make behavioral decisions. Textual 
Reactives are the appropriate rendering mechanism — observing Python layer 
state and updating the display — which is fully consistent with this layer 
boundary.

---

## 3. Coordinate System & Grid

### 3.1 Grid Dimensions

**[SETTLED]** The central grid is 31x31 cells. This is the primary visual 
focus of the application; all other panel sizes are adjusted to preserve the 
grid's size and square aspect ratio.

**[SETTLED]** User coordinate system: the center cell is (0,0). Coordinates 
range +-15 in both axes. The coordinate translation formula `user_coord = 
display_index - 15` (0-indexed) places (0,0) at display position (15,15). 

**[VERIFY]** Axis orientation (row direction) should be confirmed against 
rendering implementation before Phase 1.

### 3.2 Reference Cell

**[SETTLED]** The cell at (0,0) is the Reference Cell (RefCell). It is always 
visible in medium gray-blue. It cannot be selected as a Build cell. It is the 
mathematical identity reference for all integer pattern validation — all 
validation compares a cell set's testbed sum against the RefCell's testbed 
value. It is the default coordinate origin for all saved pattern files.

**[SETTLED]** At session start, the orange Build cursor is co-located with 
the RefCell, displayed as an orange/gray-blue chexel.

### 3.3 Terminal Layout

**[PROVISIONAL]** The reference layout targets 136x44 terminal characters, 
established by the current layout implementation.

```
Title area:       3 rows
Header controls:  4 rows
Main content:    33 rows  (left panel 35 cols | center 66 cols | right panel 35 cols)
Footer:           4 rows  (Comb 2 rows + Status Bar 2 rows)
                 --------
Total:           44 rows x 136 cols
```

**[SETTLED]** Layout priority: 
  grid size and squareness  >  side panels  >  top/bottom panels.

---

## 4. Visual Design

### 4.1 Rendering

**[SETTLED]** The grid is rendered as a single canvas object. This gives full 
control over cell rendering, chexel compositing, and multi-layer visual 
state. There are no alleys or gutters between cells. All previous designs 
featuring outline cells in alley space are deprecated.

### 4.2 Chexel Rendering

**[SETTLED]** A chexel is a 2x2 arrangement of half-block Unicode characters 
that creates a virtual checkerboard pixel, allowing two colors within a 
single terminal cell. Three-way collisions are not possible given the 
single-cursor rule (Section 8.1), so two-color chexels are sufficient for all 
states.

**[SETTLED]** Known chexel combinations:

| Combination | Colors |
|---|---|
| Cursor + RefCell | Orange / gray-blue |
| Cursor + Build cell | Orange / dark green |
| Cursor + Satellite cell | Orange / bright green |
| Handle + Build cell (Handle cell selected) | Gray-blue / dark green |
| Handle cell selected as Satellite cell | Gray-blue / bright green |

### 4.3 Default Background

**[SETTLED]** The default grid background has no shading. Only the RefCell is 
persistently marked (medium gray-blue). All optional background patterns are 
configured via G mode (Section 13) and are never included in saved patterns 
or K snapshots.

**[SETTLED]** The RefCell always displays in medium gray-blue. It is 
superseded only by the cursor chexel when the cursor is co-located.

### 4.4 Color Palette

**[SETTLED]** All colors are specified as xterm-256 palette indices. All 
entries below are provisional pending terminal testing. No color decision is 
considered settled until terminal testing is complete.

| Element              | 256 |   Hex   |       Notes        |
|----------------------|-----|---------|---|
| RefCell              | 67  | #5f87af | Medium gray-blue [TBD] :test        |
| Build cells          | 28  | #008700 | Dark green; [TBD] terminal test     |
| Active Sat cells     | 83  | #5fff5f | Bright green, 2-4 Hz animate; [TBD] |
| Inactive Sat cells   | 83  | #5fff5f | Same color, static (no animation)   |
| Build cursor         | 208 | #ff8700 | Bright orange; [TBD]                |
| Satellite Handle     | TBD | TBD     | :different from RefCell blue; [TBD] |
| Flip preview A       | 203 | #ff5f5f | Red; [TBD]                          |
| Flip preview B       | 63  | #5f5fff | Blue; [TBD]                         |
| Perim margin: B mode | 67  | #5f87af | Matches RefCell; [TBD]              |
| Perim margin: S mode | TBD | TBD     | See OQ-05                           |
| Even cells (G mode)  | 255 | #eeeeee | Checkerboard shading                |
| Odd cells (G mode)   | 231 | #ffffff | Checkerboard base                   |
| Mod4 grid (G mode)   | 252 | #d0d0d0 | Grid line shading                   |
| Daisy (G mode option) | TBD | TBD | [TBD] |
| Validation counter highlight | TBD | TBD | [TBD] |
| R/C counter -- B mode | TBD | TBD | Bright color; [TBD] |
| R/C counter -- S/Edit mode | TBD | TBD | Cyan; [TBD] |

The two greens (Build cells and Satellite cells) must be clearly 
distinguishable after terminal testing.

### 4.5 Perimeter Margin

**[SETTLED]** A solid-color margin surrounds the grid: 2 characters wide on 
left and right, 1 row tall at top and bottom. Primary ambient signal for mode 
state.

**[PROVISIONAL]** Margin color states: Build mode default = gray-blue 
(matches RefCell); Satellite mode = TBD (see OQ-05). Bingo state: no margin 
flash — validation counter highlights instead.

---

## 5. Mode System

### 5.1 Overview

**[SETTLED]** The application has four modes: Build (B), Satellite (S), 
History (H), and Grid Background (G). 
B and S are a radio button pair. 
H suspends the current B/S editing state. 
G is a display configuration overlay accessible from any mode.

**[SETTLED]** The G button is positioned to the left of the B/S pair in the 
top panel and is highlighted while G mode is active.

### 5.2 Build Mode (B)

**[SETTLED]** Default mode at session start. The orange cursor navigates the 
grid; Spacebar selects/deselects Build cells (dark green). The RefCell cannot 
be selected as a Build cell.

**[SETTLED]** Build cells are always fully visible and never dimmed, even 
when Satellite mode is active.

**[SETTLED]** Pressing B from Satellite mode: all active and inactive 
Satellite sets are removed from the grid. If any Satellite sets have unsaved 
changes, the user receives a warning before removal. The orange cursor 
reappears.

### 5.3 Satellite Mode (S)

**[SETTLED]** S is a radio button toggle. Pressing S from B mode spawns the 
first Satellite: the orange cursor transforms to a gray-blue Handle at the 
current cursor position. Pressing S again (or pressing B) returns to Build 
mode.

**[SETTLED]** The Handle is initialized at the cursor position when S is 
pressed. It is invariant relative to its cell set — moving the Handle moves 
the entire set as a group. The Handle cell is selectable as part of the 
Satellite set, producing a gray-blue/bright green chexel.

**[SETTLED]** The S mode button displays a count badge: `S[1]`, `S[2]`, etc. 
The badge disappears when returning to Build mode.

**[SETTLED]** Additional Satellites are spawned via the `+` control while in 
S mode. Each `+` press spawns a new Handle at the current active Handle's 
position. The previously active Satellite becomes inactive (static). The new 
Satellite becomes active (animating 2-4 Hz).

**[SETTLED]** Multiple Satellite management:

- **Tab**: cycles through all Satellites; each sparkles briefly 
  (1-2 seconds) as preview 
- **Return**: activates the previewed Satellite (continuous animation); 
  previous active becomes inactive 
- **Delete**: removes the currently active Satellite; 
  other Satellites unaffected

**[SETTLED]** Loading a pattern from the Pattern Library while in S mode: the 
current active Satellite becomes inactive; the loaded pattern becomes the new 
active Satellite.

### 5.4 History Mode (H)

**[SETTLED]** H suspends the current B or S mode and enters read-only review. 
Pressing H also triggers an automatic K snapshot of the current grid state 
before entering H mode. This applies whether entering from B or S mode.

**[SETTLED]** In H mode: the B/S group and all editing controls 
  (FLIP, EDIT, INCLUDE, KEEP) gray out.

**[SETTLED]** H mode controls:
- **Tab / Shift-Tab**: walk forward and back through kept states 
- **Counter**: shows position in timeline (e.g., `7 / 12`); 
  an asterisk marks states that have been saVed (e.g., `7* / 12`) 
- **Delete**: remove the currently displayed state; counter decrements 
- **V (saVe)**: save the currently displayed state's pattern to the Pattern Library 
- **Escape**: exit H; return to the grid state from before H was entered; 
  timeline intact 
- **Return**: exit H destructively; return to editing at the current review 
position; all subsequent states are discarded (user warned before executing)

**[SETTLED]** On any H exit: the active editing mode is restored to whichever 
mode was active before H was entered, not the mode stored in the snapshot.

**[SETTLED]** K is not available during H mode.

### 5.5 Grid Background Mode (G)

See Section 13 for full specification.

---

## 6. Keep (K) -- Snapshot Behavior

**[SETTLED]** K snapshots the current full grid state onto the linear 
  History timeline and remains in the current editing mode. 
  No interruption to workflow.

## think about the following:
**[SETTLED]** Each K snapshot captures: all cell set coordinates (Build + all 
Satellites with Handle positions and active/inactive flags), cursor/Handle 
position, current mode, validation state, Comb value.

**[SETTLED]** K is disabled when any illegal pattern condition exists 
(Section 9.4). When K is disabled, H mode entry is also blocked.

**[SETTLED]** Automatic K is triggered by: entering H mode, completing an 
Include, and a saVe.

---

## 7. Top Control Panel

### 7.1 Layout

**[SETTLED]** The top panel spans the full width of the screen with a label 
row above and controls below. Labels are uppercase monospaced with the 
initial character underlined (except saVe with V underlined).

**[SETTLED]** Label row (left to right):

  `GRID | SAVE | ROW COLUMN | BUILD SATELLITE | + 
  | FLIP | EDIT INCLUDE | KEEP | HISTORY`

**[SETTLED]** Control groupings:

- `GRID` -- standalone display configuration; leftmost; highlighted when G active
- `BUILD  SATELLITE` -- radio button pair
- `+` -- Satellite spawner; S mode only
- `FLIP` -- available in B and S modes
- `EDIT  INCLUDE` -- Satellite-only controls
- `SAVE`, `KEEP`, `HISTORY` -- session-level controls

### 7.2 Individual Controls

| Control | Key | Available | Behavior |
|---|---|---|---|
| GRID      | G | B, S, H  | Opens G mode background panel
| SAVE      | V | B, S, H  | Writes .ptn to Pattern Library (see Section 11)
| ROW/COL   |   | B, S     | Live coordinate display;counter in History mode
| BUILD     | B | Always   | Switches to Build mode 
| SATELLITE | S | Always   | Toggles Satellite mode 
| +         | + | S only   | Spawns additional Satellite at curr Handle pos
| FLIP      | F | B, S     | Diagonal mirror (see Section 10.1)
| EDIT      | E | S only   | Decouples Handle; spawns Edit cursor
| INCLUDE   | I | S only   | Merges active Satellite into Build
| KEEP      | K | B, S     | Snapshots grid state to History timeline
| HISTORY   | H | B, S     | Enters read-only History review

### 7.3 Footer Key Reminders

**[SETTLED]** The Status Bar footer displays a context-sensitive key reminder 
strip that updates to reflect the currently active mode. This reduces the 
learning curve without requiring persistent documentation on screen. Specific 
reminder text is an implementation detail.

---

## 8. Cursor & Navigation

### 8.1 Single Cursor Rule

**[SETTLED]** Only one primary cursor is visible at any time:

- Bright orange = Build mode
- Gray-blue Handle = Satellite mode (default navigation)
- Edit cursor (active alongside static Handle in S+Edit mode)
- No cursor = History mode

### 8.2 Navigation

**[SETTLED]**

- **Build mode**: arrow keys move orange cursor 
- **Satellite mode (default)**: arrow keys move Handle and S set as a group 
- **Satellite mode (Edit active)**: arrow keys move Edit cursor 
  independently; Handle remains stationary relative to set 
- **History mode**:  Tab / Shift-Tab step through timeline states; 
  arrow keys disabled 
- **G mode**: arrow keys shift the daisy tiling when daisy element 
  is focused in the G panel (Section 13)

**[SETTLED]** Boundary enforcement: cursor and Handle movement disabled at 
grid edge (+-15). See OQ-07 for feedback mechanism.

**[SETTLED]** Spacebar: toggles cell selection in the active cell set. Not 
available in H mode.

**[SETTLED]** No mouse support in this iteration.

### 8.3 Row/Column Display

**[SETTLED]**

- **Build mode**: cursor position in user coordinates relative to (0,0) 
- **Satellite mode (default)**: active Handle position relative to (0,0); 
  color: cyan [TBD] 
- **Satellite mode (Edit active)**: Edit cursor position relative to the 
  Handle (not the RefCell) 
- **History mode**: display replaced by History counter 
  (e.g., `7 / 12` or `7* / 12`)

---

## 9. Validation System

### 9.1 Testbed Sequence

**[SETTLED]** A 961-value dictionary keyed by user coordinates (row, col) for 
all cells -15 to +15. Computed at startup via recursive Fibonacci from a 2x2 
seed matrix of relatively prime integers. Never displayed to the user. Seed 
supplied as command-line argument or default used.

### 9.2 Unified Validation

**[SETTLED]** Validation sums the testbed values of all cells in the active 
cell set and compares the result to the RefCell testbed value.

- **Build mode**: active set = Build cell set
- **Satellite mode**: active set = active (animating) Satellite cell set

**[SETTLED]** Validation runs continuously in the background, updating as 
cells are added, removed, or the Satellite moves.

### 9.3 Bingo

## think about: really want this?
**[SETTLED]** A live numerical counter displays the current ratio of the 
active set's testbed sum to the RefCell testbed value. When the ratio is an 
exact integer, the counter highlights. No perimeter margin flash.

**[SETTLED]** Save to the Integers column requires an exact integer Bingo 
state in B mode. Save in S mode requires no validation. Include is always 
enabled in S mode regardless of Bingo state.

### 9.4 Legal Pattern Requirements & Keep Gating

**[SETTLED]** Illegal conditions:

1. Two cells at (r, c) and (r, c+1) -- horizontal adjacency (implied carry)
2. Two cells at (r, c) and (r+1, c) -- vertical adjacency (implied carry)
3. A Build cell and a Satellite cell at the same grid position -- collision
## Think: Need to highlight illegal cells?

**[SETTLED]** Diagonal adjacency -- (r, c) and (r+1, c+1) -- is permitted. 
Cross-set adjacency (Build and Satellite cells adjacent but not co-located) 
is also permitted; the visual distinction between dark green and bright green 
makes such relationships unambiguous.

**[SETTLED]** K is disabled when any illegal condition exists. No automatic 
corrections; user resolves manually. Illegal patterns may exist temporarily 
during editing -- Keep gating is the validation boundary, not the editing 
boundary.

**[SETTLED]** Status Bar displays error messages for illegal conditions 
(e.g., "Satellite overlap", "Adjacency error"). See OQ-11 for hint system 
design.

### 9.5 Comb Row [PENDING]

The Comb row displays the diagonal sums of the current cell set across 
positions -30 to +30 (61 positions), where each position corresponds to a 
value of `row + col`. If multiple cells share a diagonal, the Comb entry at 
that position displays an integer greater than 1 -- an accurate compressed 
representation of the grid state, analogous to a Pipe Expression in Composer. 
Positions with values greater than 1 are rendered in a distinct color to 
signal that the position requires attention before the pattern can be saved 
as a legal bit representation.

Expanding a compressed Comb entry into a valid bit sequence is a non-trivial 
algebraic operation outside the scope of Cloudbits. The intended workflow 
involves copying the Comb row to the Composer page, which provides the 
environment for rewriting and validating the expansion. This is a primary 
planned integration point between Cloudbits and Composer in the Nnumerics 
roadmap.

Full Comb and Pord design -- including update frequency, Handle-relative 
computation in S mode, Pord calculation method, and Composer integration -- 
is [DEFERRED]. The CombEngine domain is retained in the architecture for 
future implementation.

---

## 10. Pattern Operations

### 10.1 Flip

**[SETTLED]** Transformation: (r, c) -> (c, r). Diagonal mirror across the 
NW-SE axis. Produces a pattern with the same testbed validation result and 
Comb value as the original.

**[SETTLED]**

- **Build mode**: Flip relative to (0,0). Immediate. Triggers automatic K. 
- **Satellite mode**: Flip relative to Handle. 
  Dual-variant preview: both variants shown simultaneously in contrasting 
  colors (see OQ-12). Spacebar toggles between variants; Return commits; 
  Escape cancels. Committed Flip triggers automatic K.

**[SETTLED]** Symmetrical patterns (identical when flipped) are flagged with 
`S` in the filename. The variant-selection step is skipped for symmetrical 
patterns.

### 10.2 Include

## think about: Handle can disappear but Handle location should remain visible 
## maybe need a new entity: half-chexel placeholder??

**[SETTLED]** Merges the active Satellite's cells into the Build set. 
Satellite cells (bright green) become Build cells (dark green). The active 
Handle disappears. Remaining inactive Satellites are unaffected. If no 
Satellites remain, the orange cursor reappears. Triggers automatic K.

**[SETTLED]** Stamping workflow: position Handle at target location -> 
Include (Handle reappears at same position) -> move Handle to next target -> 
Include again. Flip may be applied between Includes for variant compositions.

### 10.3 Edit (Satellite Mode Only)

**[SETTLED]** Not displayed or available in Build mode. In S mode: decouples 
Handle from group movement. An Edit cursor spawns from the Handle position 
and navigates independently with arrow keys. Spacebar toggles individual 
Satellite cells. The R/C display shows the Edit cursor position relative to 
the Handle. Toggling Edit off re-couples the Handle to the set.

### 10.4 Clipboard Operations

**[PROVISIONAL]** Ctrl-C, Ctrl-V, Ctrl-X for copy, paste, and cut of cell 
sets using relative coordinates. Cross-mode clipboard (Build -> Satellite) 
supported. Selection mechanics and collision handling deferred. See OQ-08.

---

## 11. Save Behavior & Pattern Library

### 11.1 Save Rules by Mode

**[SETTLED]**

| Mode | Condition | Destination | Filename prefix |
|-----------------|-------------------|-----------------|----------------
| Build (int)     | Bingo required    | Integers column | (`I17abc.ptn`)
| Build (non-int) | No gate           | Patterns column | (`C299abc.ptn`)
| Satellite       | No gate           | Patterns column |  TBD 
| History         | Rules = edit mode | Per above       | Per above

## think about this; I didn't write this...
**[SETTLED]** In Satellite mode, only the active Satellite's cells are saved. 
  The Build set on display is not included. Saved cell coordinates are 
  expressed relative to the grid's (0,0) RefCell -- the universal coordinate 
  reference for all Cloudbits patterns. The Handle's grid position 
  (also in RefCell coordinates) is stored separately in the file as a 
  session reference for the saved pattern.

**[SETTLED]** saVe is not automatic in any mode; it must be user-confirmed.

### 11.2 Pattern Library Display

**[SETTLED]** Two columns: 
- **Integers** (validated integer multiples of RefCell testbed value) and 
- **Patterns** (all other saved cell sets: non-integer Build patterns, 
  Satellite patterns, composite results, Flip variants, working patterns). 

Display capacity: approximately 15-20 slots per column. Curated working set, 
not a full file browser.

**[SETTLED]** The Pattern Library is a shared Nnumerics resource. 
Cloudbits monitors it via FileWatcher and refreshes the display when files 
change externally, but does not own or manage the library. 
Full file management is handled via the OS file manager or Nnumerics.

**[SETTLED]** Read-only display within Cloudbits.

**[PROVISIONAL]** QInt column (multiples of sqrt(5)) to be added when 
Q-validation is defined.

**[PROVISIONAL]** The Patterns column will carry a metadata slot for user 
annotations and provenance notes. Design deferred.

### 11.3 Pattern Loading Workflow

**[SETTLED]** Loading always presents both Flip variants simultaneously in 
contrasting preview colors.

**[SETTLED]** Workflow:

1. User selects slot -> both variants appear on grid in preview colors
2. Spacebar toggles highlighted variant (selected = full brightness, 
   other = dimmed)
3. Return commits selected variant, cells turn bright green S color
4. Escape cancels -> both variants disappear; grid returns to pre-load state

**[SETTLED]** After commit:

- **Build mode**: cells transform to dark green at their RefCell-relative 
  coordinates; orange cursor remains free 
- **Satellite mode**: cells transform to bright green with Handle active, 
  placed at the upper-left of the pattern's bounding box; user moves the set 
  to the desired position using normal S mode navigation before proceeding

**[SETTLED]** All .ptn files are mode-neutral. Build/Satellite distinction is 
determined by the current mode at load time.

### 11.4 Filename Conventions

**[SETTLED]** Metadata flags:

- `I_` -- validated integer Build pattern (e.g., `I17abc.ptn`)
- `C_` -- Comb ordinal pattern (e.g., `C299abc.ptn`)
- `S` -- symmetrical (Flip-invariant)
- Additional characters ensure filename uniqueness; user may append custom suffix

**[PROVISIONAL]** `Q` flag for QInt (multiple of sqrt(5)). Definition and 
validation method not yet specified.

---

## 12. History

### 12.1 Linear Timeline

**[SETTLED]** History is a linear timeline of K-snapshotted grid states. No 
branching. States are numbered sequentially from 1. History is 
session-persistent but not cross-session.

### 12.2 K -- Adding States

**[SETTLED]** K snapshots the current grid state to the end of the timeline 
without entering H mode. Full snapshot includes: all cell sets with 
coordinates and flags, Handle positions, cursor position, current mode, Comb 
value, validation state.

**[SETTLED]** K is available in B and S modes only. Disabled for illegal 
patterns (and therefore H entry is also blocked when K is disabled).

**[SETTLED]** Automatic K on: entering H mode, Include, Delete of a 
Satellite, accepted Flip, saVe.

### 12.3 H Mode -- Reviewing States

**[SETTLED]** Tab / Shift-Tab step through states. Counter shows current 
position and total (e.g., `7 / 12`). An asterisk marks any state that has 
been saVed (e.g., `7* / 12`).

**[SETTLED]** Available actions in H mode: Delete (removes current state, 
counter decrements); saVe (V key, writes current state's pattern to Library, 
marks with asterisk).

**[SETTLED]** Exit options:

- **Escape**: return to pre-H editing state; timeline intact 
- **Return**: destructive -- return to editing at current review position; 
  all subsequent states discarded; user warned before executing

**[SETTLED]** On any H exit: active editing mode is restored to whichever 
mode was active before H was entered.

### 12.4 Right Panel Layout

**[SETTLED]** The right panel contains the History timeline display (counter, 
state indicator) in the upper region. The lower region is occupied by the G 
mode panel when G is active (Section 13.5), and reserved for a future 
NOTES/TAGS metadata area when G is inactive. The reserved area should appear 
as a labeled placeholder to communicate design intent.

---

## 13. Grid Background (G Mode)

### 13.1 Overview

**[SETTLED]** G mode is a display configuration overlay. It is accessible 
from B, S, and H modes. Selecting and adjusting background elements has no 
effect on cell sets, validation, History snapshots, or saved patterns. No 
background configuration persists across sessions.

**[SETTLED]** The G button is in the top panel to the left of the B/S pair. 
It is highlighted while G mode is active. Pressing G opens the G mode panel 
and shifts key focus to it; pressing Return or Escape exits G mode.

### 13.2 Background Elements

**[SETTLED]** Available background elements:

| Element             | Description                    | Shiftable | Flippable
|---------------------|-------------------------------------|----|-----
| Checkerboard parity | Shade if (row+col)%2 == 0           | No | No
| Mod4 lines (full)   | Rows and cols at -12,-8,-4,0,4,8,12 | No | No 
| Mod4 (reduced)      | Rows and cols at -12,-4,4,12        | No | No 
| Daisy               | Full-grid daisy tiling              | Yes| Yes

**[SETTLED]** The default state is no background element active (RefCell only).

**[SETTLED]** Active pattern cells (Build, Satellite, RefCell) always occlude 
background elements at the same position. No chexel compositing is used for 
background layers.

**[SETTLED]** Each element supports 4 opacity levels (dim, low, medium, 
full), simulated via color proximity to the grid background. Opacity is 
independent per element.

**[PROVISIONAL]** Checkerboard and mod4 lines may be stacked with independent 
opacity settings. Other stacking combinations to be determined.

### 13.3 Daisy Pattern

**[SETTLED]** The daisy is a full-grid tiling of the Fibonacci cell 
substitution relationship -- the property that any cell's testbed value 
equals the sum of three cells in a fixed spatial arrangement (e.g., (0,0) = 
(1,-2) + (-1,-1) + (-2,-1), or its Flip equivalent). The pattern tiles with 
period 5 in both axes.

**[SETTLED]** The daisy is displayed as a uniform tiling with a single 
visual treatment for all highlighted cells. No "Handle" or distinction is 
made between "center" and "triplet" positions -- the user reads substitution 
relationships by inspection.

**[SETTLED]** The daisy has two spatial variants related by the Flip 
transformation. The current shift offset (2D, period 5 per axis) and the 
active Flip variant are preserved within the session when switching between 
B/S/H and G modes.

### 13.4 G Mode Controls

**[SETTLED]**

| Key | Action |
|---|---|
| Tab / Shift-Tab | Cycle focus between elements in the G mode panel
| Space           | Toggle focused element on/off
| `<` / `>`       | Step opacity down / up for focused element
| Arrow keys      | Shift only daisy tiling by one step in given direction
| F               | Toggle only daisy cells with Flip variant
| Return          | Commit configuration and exit G mode
| Escape          | Revert to previous configuration and exit G mode

### 13.5 G Mode Panel

**[SETTLED]** The G mode panel occupies the lower region of the right panel 
when G is active and is hidden otherwise. It displays one row per available 
background element, showing element name, on/off state, and opacity bar. 
No numeric readout of daisy offset is shown -- the grid canvas communicates 
daisy position in real time.

**[PROVISIONAL]** Example panel layout:

```
DAISY    [F] ████░░
CHECKER      ██░░░░
MOD4 R       ████░░
MOD4 F       ░░░░░░
```

(`[F]` indicates active Flip variant; opacity bar shows current level; dimmed 
rows are inactive.)

---

## 14. File Formats

### 14.1 Pattern File (.ptn)

**[SETTLED]** Format: JSON. Self-contained -- all metadata within the file. 
All cell coordinates are expressed relative to the grid's (0,0) RefCell.

**[PROVISIONAL]** Structure:

```json
{
  "cloudbits_version": "1.0",
  "pattern": {
    "coordinates": [[row, col], "..."],
    "handle": [row, col],
    "pattern_type": "build | satellite",
    "flip_variants": "both | single"
  },
  "validation": {
    "is_integer": true,
    "multiplier": 17,
    "comb_value": 487,
    "testbed_seed": [a, b, c, d]
  },
  "session_data": {
    "created": "ISO timestamp",
    "source_history_state": 7
  }
}
```

**[OPEN]** OQ-15: File format subject to change; version number supports 
future migration.

### 14.2 Session and Configuration

**[SETTLED]** A command-line argument specifies the Pattern Library directory 
path at startup. Default path used if not provided.

**[SETTLED]** On application shutdown, the current grid state is 
automatically saved. The specific mechanism (session file, auto-snapshot to 
History, or auto-save to Patterns column) is [PROVISIONAL].

**[PROVISIONAL]** Grid background configuration (active elements, opacity 
levels, daisy state) may be saved as a lightweight session config file, 
separate from .ptn format.

---

## 15. Development Phases

**[SETTLED]** Each phase is a shippable increment. Phase 1 architecture must 
support future phases: separate cell collections, rendering ready for 
animation, state management ready for multiple Satellites.

| Phase | Scope | Status for implementation stages:

1 Canvas grid, Build mode, orange cursor, RefCell, basic K
  Ready to implement | 

2 Testbed, unified validation counter, Bingo highlight, Save (Build)
  Ready to implement

3 Satellite mode -- S toggle, Handle, + spawning, multiple Satellites, 
  Tab/Return cycling, 2-4 Hz animation, Edit, Include, Flip dual-variant, 
  stamping workflow, Satellite Save
  Specified 

4 Pattern Library panel, .ptn file I/O, dual-variant load preview, 
  file watching | Follows Phase 3 | 

5 History panel, full K behavior, H mode navigation 
  Follows Phase 4

6 G mode, Grid Background panel, all background elements, daisy with shift/Flip
  Follows Phase 5

7 Clipboard (Ctrl-C/V/X), legal pattern detection, K gating, hint system
  Follows Phase 6

8 Comb row display and Pord computation
  [DEFERRED]

9 Comb interaction, Pord input, searchlight, Composer integration
  [SPECULATIVE]

**[SETTLED]** Explicitly excluded from Phases 1-2: 
  Satellite spawning, Pattern Library loading, History/H mode, 
  full K, Include, Edit, loading to non-empty grid, G mode, Comb.

---

## 16. Open Questions

| ID | Topic | Description |
|---|---|---|
| OQ-05 | Satellite margin color | Specific color TBD; priority order 
| when multiple states apply |

| OQ-07 | Boundary feedback | How to communicate that movement is 
| disabled at grid edge |

| OQ-08 | Clipboard paste | Collision handling; pasting into a mode with 
| existing cells |

| OQ-11 | Illegal pattern hints | Communicating which cells are causing 
| illegality and what options exist |

| OQ-12 | Preview color pair | Dual-variant Flip/load display colors; 
| must not conflict with mode colors |

| OQ-15 | File format versioning | Migration strategy as format evolves |

| QInt | Q-integer | Definition and validation method for multiples of 
| sqrt(5) |

**Closed:** 
OQ-01 (Edit in Build: S-mode only)
OQ-02 (Merge dropped), 
OQ-03 (+ spawns at current active Handle position)
OQ-04a (Handle chexel form: TBD pending visual testing)
OQ-04b (green values: TBD pending terminal testing)
OQ-06 (Assert mode: dropped)
OQ-09 (Include gating: always enabled in S mode), 
OQ-10 (Comb deferred), 
OQ-13 (History/Slides: linear timeline only).

---

*End of Cloudbits Design Specification v0.5* *Status: Working draft -- 
prepared for phased implementation* *Supersedes: v0.1 through v0.4 and 
all Addenda*
