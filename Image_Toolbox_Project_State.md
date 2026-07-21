# Image Toolbox — Project State

**Last updated:** 2026-07-19  
**Location:** `C:\Users\AiDA\ai_tools\ImageToolbox`  
**Status:** Stable — select/resize/convert workflow verified working end-to-end. Since the last update: a full code review was completed — removed 4 unused getter methods from `ImageProcessor`, deduplicated repeated widget-manipulation code in `ImageToolboxGUI` into small helper methods, and added clarifying comments. No behavior changed (full regression suite re-run and passing). Also fixed a documentation gap: `.gitignore` was missing from `README.md`'s Project Structure diagram. No open bugs.

---

## 1. Project Overview

**Image Toolbox** is a small desktop GUI application for batch-resizing images. Users select one or more image files, choose an output folder, set target dimensions and output format, then process all images in one run.

| Layer | Technology |
|---|---|
| Language | Python 3.14.6 |
| GUI | tkinter (stdlib) |
| Image processing | Pillow (PIL) |
| Platform | Windows (primary target) |

**Entry point:** `main.py` creates a `TkinterDnD.Tk()` root window (a drop-in, drag-and-drop-capable subclass of `tk.Tk`) and launches `ImageToolboxGUI`.

---

## 2. Current File Structure

```
ImageToolbox/
├── main.py                        # Entry point — launches drag-and-drop-capable tkinter GUI
├── requirements.txt               # Python dependencies (Pillow, tkinterdnd2)
├── README.md                      # User-facing quick-start and feature overview
├── .gitignore                     # Ignores __pycache__/, *.pyc, settings.json
├── run.ps1                        # PowerShell launcher script
├── run.bat                        # Windows batch launcher script
├── Image_Toolbox_Project_State.md # This document
├── settings.json                  # Auto-generated: persisted GUI settings (created on first save)
└── app/
    ├── __init__.py                # Empty package marker
    ├── gui.py                     # tkinter UI (ImageToolboxGUI)
    └── image_processor.py         # Image resize/save logic (ImageProcessor)
```

**Git-tracked files (Initial commit):** `main.py`, `app/__init__.py`, `app/gui.py`, `app/image_processor.py`

**Untracked (not yet committed):** `requirements.txt`, `README.md`, `run.ps1`, `run.bat`, `Image_Toolbox_Project_State.md`

---

## 3. Dependencies

| Dependency | Version / Status | Notes |
|---|---|---|
| **Python** | 3.14.6 | Installed and on PATH (`python --version`) |
| **Pillow** | >=12.3.0 (pinned) | Required for image I/O and resizing. Listed in `requirements.txt` |
| **tkinter** | Bundled | Included with standard Python on Windows; no separate install |
| **tkinterdnd2** | >=0.6.2 (pinned) | Required for drag-and-drop support. Listed in `requirements.txt` |

### Install dependencies

```powershell
cd C:\Users\AiDA\ai_tools\ImageToolbox
pip install -r requirements.txt
```

Or install Pillow directly:

```powershell
pip install Pillow
```

---

## 4. How to Run

### Option A — Change directory, then run (recommended)

```powershell
cd C:\Users\AiDA\ai_tools\ImageToolbox
python main.py
```

### Option B — Run without changing directory

```powershell
python C:\Users\AiDA\ai_tools\ImageToolbox\main.py
```

Use `py` instead of `python` if that is how Python is registered on your system:

```powershell
py C:\Users\AiDA\ai_tools\ImageToolbox\main.py
```

### Option C — Launch scripts

**PowerShell** (from any directory):

```powershell
C:\Users\AiDA\ai_tools\ImageToolbox\run.ps1
```

Or from inside the project folder:

```powershell
.\run.ps1
```

**Batch file:** double-click `run.bat` in File Explorer, or run from a command prompt.

Both scripts `cd` into the project directory before calling `python main.py`:

- `run.ps1` — `Set-Location $PSScriptRoot`
- `run.bat` — `cd /d "%~dp0"`

**Expected result:** A window titled **"Image Toolbox"** opens (900×650, minimum 800×600).

---

## 5. PowerShell Error That Was Fixed

### What went wrong

In PowerShell, typing a bare path does **not** open or enter that folder:

```powershell
# Wrong — PowerShell tries to EXECUTE the path as a command
C:\Users\AiDA\ai_tools\ImageToolbox
```

Because `ImageToolbox` is a **directory** (not an `.exe`, `.bat`, or `.ps1`), PowerShell raises:

```
CommandNotFoundException: The term 'C:\Users\AiDA\ai_tools\ImageToolbox' is not recognized...
```

### Correct approach

Use `cd` to change into the folder, then run the app:

```powershell
cd C:\Users\AiDA\ai_tools\ImageToolbox
python main.py
```

Or use a launch script (`run.ps1` / `run.bat`) that handles the directory change automatically.

---

## 6. GUI Features

The UI is implemented in `app/gui.py` as class `ImageToolboxGUI`, built with `ttk` widgets (grouped into "Files", "Resize Options", and "Output Options" sections) for a cleaner, better-spaced layout.

### Controls

| Control | Purpose |
|---|---|
| **Select Images** | Opens a file dialog for JPG, JPEG, PNG, WEBP; populates the file list |
| **Select Output Folder** | Chooses where processed images are saved |
| **Width / Height** | Text fields for target pixel dimensions; read directly when **Process Images** is clicked (no separate save step) |
| **Resize Preset** | Combobox with 10 common sizes (64×64 up to 3840×2160 (4K)) plus **Custom**. Choosing a preset fills Width/Height and locks them; choosing **Custom** unlocks them for manual entry |
| **Keep Aspect Ratio** | Checkbox. When checked, the image is scaled to fit inside the width/height box without distorting it. When unchecked, width and height are applied exactly (may stretch/squash) |
| **Output Format** | Dropdown: JPG, PNG, or WEBP |
| **Quality (JPEG/WEBP)** | Slider, 1–100, default 95. Only applied when saving as JPEG or WEBP; ignored for PNG |
| **Process Images** | Runs batch resize on all selected files; disabled while processing, re-enabled when done (success or error) |
| **Progress bar** | Shows per-file progress during processing |
| **Status label** | Displays ready state, selection count, and processing progress |
| **File listbox** | Shows basenames of selected images (with a scrollbar) |
| **Drag & Drop** | Not a widget — drop JPG/JPEG/PNG/WEBP files anywhere on the main window to add them to the file list (in addition to, not replacing, files already selected) |

### Processing behavior

- Processing runs on a **background thread** so the UI stays responsive.
- The **Process Images** button is disabled the moment processing starts and re-enabled when it finishes, whether it finishes successfully or with an error — this prevents overlapping runs from a double-click.
- Width and height are read from the entry fields at the moment **Process Images** is clicked and validated then (must be positive integers), rather than requiring a separate save step.
- The **Resize Preset** combobox can fill Width/Height automatically; selecting a preset disables those fields (their filled-in values are still read normally when processing), and selecting **Custom** re-enables manual editing.
- If **Keep Aspect Ratio** is checked, each image is scaled to fit inside the width/height box while preserving its original proportions. If unchecked, the image is resized to the exact width and height entered (may stretch/squash).
- Output filenames keep the original basename with the chosen extension (e.g. `photo.jpg` → `photo.png`).
- If a file with the target output name already exists, the new file is saved as `name (1).ext`, `name (2).ext`, etc. instead of overwriting it.
- **JPG output:** RGBA and LA images are composited onto a white background before saving.
- For JPEG and WEBP output, the **Quality** slider value (1–100, default 95) is passed to Pillow's save; PNG ignores it since PNG is lossless.
- A completion dialog reports how many images were processed successfully.
- **Settings persistence:** Output Folder, Width, Height, Output Format, Resize Preset, and Keep Aspect Ratio are saved automatically to `settings.json` (in the project root) whenever they change — on output folder selection, preset selection, format/checkbox toggle, leaving a width/height field, or closing the window — and are restored automatically the next time the app starts.
- **Drag & drop:** dropping files onto the main window filters them to `.jpg`/`.jpeg`/`.png`/`.webp` (case-insensitive), skips anything already in the selection (no duplicates), and adds the rest to both the internal file list and the listbox. Unsupported files dropped alongside supported ones are silently ignored rather than blocking the whole drop.

### Typical workflow

1. Click **Select Images**
2. Click **Select Output Folder**
3. Pick a **Resize Preset**, or leave it on **Custom** and enter width/height manually
4. Optionally check **Keep Aspect Ratio**
5. Choose output format (default: JPG)
6. Click **Process Images**

---

## 7. Image Processing (`app/image_processor.py`)

Class `ImageProcessor` holds state and performs the actual resize/save:

- **State:** selected files, output folder, width, height, output format, keep-aspect-ratio flag, quality (default 95)
- **`set_resize_values()`** — validates that width and height are digit strings
- **`set_keep_aspect_ratio()`** — stores whether resizing should preserve the original aspect ratio
- **`set_quality()`** — stores the JPEG/WEBP save quality (1–100)
- **`resize_image()`** — opens image with Pillow; computes target dimensions (exact width/height, or a fitted size if aspect ratio is preserved), resizes, converts for JPG if needed, and saves to the output folder with the quality setting applied for JPEG/WEBP. If the target filename already exists, appends ` (1)`, ` (2)`, etc. to avoid overwriting.
- **Error handling:** on success returns the output path; on failure, raises the underlying exception (e.g. `ValueError` for unset output folder/resize values, `PIL.UnidentifiedImageError` for a corrupt/unreadable file, `OSError`/`FileNotFoundError` for missing files) with its original message intact, so the caller can report which file failed and why. The temp-file cleanup (`finally` block) still runs regardless of success or failure.
- Note: `get_resize_values()`, `get_output_format()`, `get_keep_aspect_ratio()`, and `get_quality()` were removed in the 2026-07-19 code review — they were unused getters left over from earlier iterations of the GUI. Only the `set_*` half of each pair and `get_selected_files()`/`get_output_folder()` (both still used by `app/gui.py`) remain.

---

## 8. Recent Changes

Changes made during the ImageToolbox setup session:

1. **Diagnosed PowerShell error** — bare path treated as executable; documented correct `cd` + `python main.py` workflow
2. **Installed Pillow** — `pip install Pillow` (v12.3.0 verified)
3. **Added `requirements.txt`** — lists `Pillow` for reproducible installs
4. **Added `run.ps1`** — PowerShell launcher with `Set-Location $PSScriptRoot`
5. **Added `run.bat`** — batch launcher with `cd /d "%~dp0"`
6. **Verified environment** — Python 3.14.6, Pillow, and tkinter all available
7. **Created this document** — `Image_Toolbox_Project_State.md`
8. **Fixed: "Process Images" button stayed clickable during processing** — repeated clicks could start overlapping background threads that raced to write the same temp file, occasionally producing a corrupted/unopenable output image. `app/gui.py` now disables the button as soon as processing starts (`start_processing()`) and re-enables it in a `finally` block inside `resize_images()`, so it re-enables even if an error occurs. No other behavior was changed; `app/image_processor.py` was not modified.
9. **Removed the "Save Resize Values" button** — `app/gui.py` no longer has a separate save step; width and height are now read straight from the entry fields and validated at the moment **Process Images** is clicked. `app/image_processor.py` was not modified for this change.
10. **Prevented overwriting existing output files** — `app/image_processor.py`'s `resize_image()` now checks whether the target filename already exists and, if so, appends ` (1)`, ` (2)`, etc. until it finds an unused name (e.g. `photo.jpg` → `photo (1).jpg`). `app/gui.py` was not modified for this change.
11. **Added a "Keep Aspect Ratio" checkbox** — `app/gui.py` adds the checkbox next to the width/height fields; `app/image_processor.py` gained `set_keep_aspect_ratio()` and, in `resize_image()`, computes a fitted size (preserving the original proportions) when the checkbox is on, instead of forcing the exact width/height. Existing exact-resize behavior is unchanged when the checkbox is off.
12. **Added a JPEG/WEBP quality slider (1–100, default 95)** — `app/gui.py` adds a `tk.Scale` next to the output format dropdown. `app/image_processor.py` gained `set_quality()`/`get_quality()` and now passes `quality` to Pillow's save only when the format is JPEG or WEBP; PNG saves are unaffected.
13. **Rebuilt the GUI with ttk widgets** — `app/gui.py` was rewritten using `ttk.Button`, `ttk.Label`, `ttk.Entry`, `ttk.Checkbutton`, and `ttk.Combobox` (replacing the old `tk.OptionMenu`), grouped into "Files", "Resize Options", and "Output Options" `ttk.LabelFrame` sections with consistent padding, plus a scrollbar added to the file list. The quality slider stays a `tk.Scale` (ttk's Scale has no integer-step "resolution" option and could otherwise feed non-integer values to the quality setting). No functional behavior changed; `app/image_processor.py` was not modified for this change.
14. **Added a Resize Preset system** — `app/gui.py` adds a `ttk.Combobox` named "Resize Preset" with 10 common sizes (64×64, 128×128, 256×256, 512×512, 800×600, 1024×768, 1280×720 (HD), 1920×1080 (Full HD), 2048×2048, 3840×2160 (4K)) plus "Custom". Selecting a preset fills Width/Height and disables those fields (via `on_preset_selected()`); selecting "Custom" re-enables manual editing. Disabled fields still report their value through `.get()`, so processing logic is unaffected. `app/image_processor.py` was not modified for this change.
15. **Re-verified "Keep Aspect Ratio" and overwrite-prevention against expanded requirements** — no code changes. Confirmed the aspect-ratio toggle produces correctly fitted output both when a **Resize Preset** is selected (e.g. 1920×1080 → 960×1080 for the test image) and with manually-entered **Custom** values (e.g. 400×400 → 356×400). Confirmed the overwrite-prevention naming (`name (1).ext`, `name (2).ext`, `name (3).ext`, ...) behaves identically across JPG, PNG, and WEBP.
16. **Added persistent application settings** — `app/gui.py` now saves Output Folder, Width, Height, Output Format, Resize Preset, and Keep Aspect Ratio to `settings.json` (stored next to `main.py`, via `_settings_path()`) through a new `save_settings()`/`load_settings()` pair. Saves are triggered automatically: after picking an output folder, after a preset selection, on format/keep-aspect changes (`trace_add`), when a width/height field loses focus, and on window close (`WM_DELETE_WINDOW`). `load_settings()` restores everything at startup, including re-locking Width/Height if a non-Custom preset was saved. A `save` flag on `on_preset_selected()` prevents `load_settings()` from writing a partially-restored state back to disk mid-load. Missing or unreadable `settings.json` is treated as "no saved settings" (falls back to current defaults) rather than raising an error. `app/image_processor.py` was not modified for this change.
17. **Added Drag & Drop support** — required the new `tkinterdnd2` dependency (`pip install tkinterdnd2`, v0.6.2 verified; not yet added to `requirements.txt`). `main.py` now creates the root window with `TkinterDnD.Tk()` instead of `tk.Tk()` (a drop-in subclass) so drag-and-drop events are available. `app/gui.py` registers the main window as a drop target (`DND_FILES`) and adds an `on_drop()` handler: it parses the dropped-path string with `self.root.tk.splitlist()` (correctly handles brace-quoted paths with spaces), filters to `.jpg`/`.jpeg`/`.png`/`.webp` (case-insensitive), skips files already selected, and adds the rest to both `ImageProcessor`'s selected-files list and the listbox — same end state as clicking **Select Images**, but additive rather than replacing the current selection. `app/image_processor.py` was not modified for this change.
18. **Received the real `README.md` and `requirements.txt` and synced them with actual behavior** — previously only described in this document, never actually available to edit. `requirements.txt` gained the `tkinterdnd2` line it was missing since drag & drop was added (item 17). `README.md` was fully rewritten: it had described an old version of the app (a "Save Resize Values" button that no longer exists, no mention of Resize Presets, Keep Aspect Ratio, the quality slider, drag & drop, or settings persistence, and it incorrectly stated existing output files get overwritten). The new `README.md` documents the current feature set, workflow, and project structure accurately. Re-confirmed (no code change) that overwrite-prevention still produces `name (1).ext` / `(2)` / `(3)` correctly for JPG, PNG, and WEBP.
19. **Improved batch processing error reporting** — `app/image_processor.py`'s `resize_image()` no longer swallows exceptions and returns `False`; it now raises the original exception (with message intact) after the pre-flight checks were converted from silent `return False` to `raise ValueError(...)`. The `finally` block still cleans up the `.tmp` file on any failure. `app/gui.py`'s `resize_images()` loop now wraps each `resize_image()` call in `try/except`, collecting `(filename, error_message)` pairs into a `failures` list while continuing to the next file — one bad image no longer silently reduces the count with no explanation. At the end, a summary dialog shows `Successful: X` / `Failed: Y`, and if there were any failures, a new scrollable `show_failures_dialog()` (a `Toplevel` with a read-only `tk.Text` + `ttk.Scrollbar`) lists every failed filename and its exact error message. The status label was updated to `"X succeeded, Y failed"`. Tested with a mix of a valid image, a corrupt file, and a missing file: processing continued past both failures, the correct filenames/messages were captured, and the failures dialog was only triggered when `failures` was non-empty. Also re-ran the full preset/aspect-ratio/quality/drag-drop regression suite to confirm nothing else broke.
20. **Pinned dependency versions in `requirements.txt`** — changed `Pillow` / `tkinterdnd2` (unpinned) to `Pillow>=12.3.0` / `tkinterdnd2>=0.6.2`, matching the versions already verified working (§3). Confirmed `pip install -r requirements.txt` resolves correctly with the pins (dry-run tested). `README.md`'s Requirements table updated to show the pinned minimums. No code files changed.
21. **Added `.gitignore`** — new file at the project root ignoring `__pycache__/`, `*.pyc`, and `settings.json`. Verified with a throwaway `git init` + `git add -A` test that a `__pycache__/*.pyc` file and `settings.json` are excluded while `main.py` and every file under `app/` (source code) are staged normally. No source files are ignored.
22. **Reviewed the repository for first public release** — no functionality changes; documentation-only. Reconstructed the full documented project structure (`main.py`, `requirements.txt`, `README.md`, `.gitignore`, `run.ps1`, `run.bat`, `Image_Toolbox_Project_State.md`, `app/__init__.py`, `app/gui.py`, `app/image_processor.py`, plus a `settings.json` and a stray `__pycache__/*.pyc`) in a throwaway `git init` + `git add -A` test: confirmed every source and documentation file gets staged, and `settings.json`/`__pycache__/` are correctly excluded by `.gitignore`. Checked for standard public-release files (`LICENSE`, `CHANGELOG.md`, `CONTRIBUTING.md`, `.gitattributes`) — all absent except `.gitignore`. **Finding: no `LICENSE` file exists.** This is the one real gap for a public release; adding one requires the user to pick a license (MIT, Apache-2.0, GPL, etc.) since that's a legal/licensing decision, not something to choose unilaterally.
23. **Full code review** — read every project file, then cleaned up `app/image_processor.py` and `app/gui.py` with no behavior change (verified with a 6-part regression suite: preset fill/lock, Custom unlock, file-list population, drag-drop dedup, settings persistence round-trip, and mixed-success/failure error reporting — all passed after the changes). Specifically: (1) **Dead code removed** — `get_resize_values()`, `get_output_format()`, `get_keep_aspect_ratio()`, `get_quality()` in `ImageProcessor` were confirmed unused anywhere in the project (grepped) and deleted. (2) **Duplicate code removed** — `app/gui.py` gained two helpers: `_set_entry_value()` (replace-and-optionally-disable an Entry, previously hand-written 3–4 times across `on_preset_selected()` and `load_settings()`) and `_populate_file_list()` (insert basenames + refresh the status label, previously duplicated between `select_images()` and `on_drop()`). `on_preset_selected()` was also simplified from two separate `if save:` branches with an early return into one shared trailing check. (3) **Readability** — removed a redundant `RESIZE_PRESETS` local variable that was immediately aliased to `self.resize_presets` (now assigned directly). (4) **Comments improved** — added rationale comments for the `ttk.Style` theme fallback, the `save` parameter on `on_preset_selected()`, and the restore-order dependency in `load_settings()` (preset before Custom width/height). Also fixed a `README.md` accuracy gap found during the review: `.gitignore` was missing from the Project Structure diagram.

---

## 9. Git Status

| Item | Value |
|---|---|
| **Branch** | `main` |
| **Remote** | Not configured / not pushed |
| **Commits** | 2 |

```
ef90387 Initial commit
e1a470e firest commit
```

**Tracked:** `main.py`, `app/__init__.py`, `app/gui.py`, `app/image_processor.py`

**Untracked:** `requirements.txt`, `README.md`, `.gitignore`, `run.ps1`, `run.bat`, `Image_Toolbox_Project_State.md` (`settings.json` and `__pycache__/` are now covered by `.gitignore` and would be excluded automatically once other files are committed)

---

## 10. Known Limitations / Next Steps

### Completed improvements

- [x] **Disable "Process Images" button while processing** — completed 2026-07-19. Prevents overlapping background threads from racing on the same temp file. Tested and confirmed working.
- [x] **Remove the "Save Resize Values" button** — completed 2026-07-19. Width/height are now read and validated directly when **Process Images** is clicked. Tested and confirmed working.
- [x] **Prevent overwriting existing output files** — completed 2026-07-19, re-verified 2026-07-19. Output files that would collide with an existing name are auto-numbered (`name (1).ext`, `name (2).ext`, `name (3).ext`, ...) instead of overwritten. Confirmed working identically for JPG, PNG, and WEBP.
- [x] **Add aspect-ratio preserve toggle** — completed 2026-07-19, re-verified 2026-07-19. A "Keep Aspect Ratio" checkbox fits the image inside the requested width/height box without distorting it when checked; unchecked behavior (exact stretch) is unchanged. Confirmed working with both **Resize Preset** selections and manually-entered **Custom** sizes.
- [x] **Add a JPEG/WEBP quality slider** — completed 2026-07-19. Slider ranges 1–100, defaults to 95, and only affects JPEG/WEBP saves (PNG ignores it). Tested and confirmed working.
- [x] **Improve the GUI layout with ttk widgets** — completed 2026-07-19. Rebuilt with `ttk` widgets, grouped sections (Files / Resize Options / Output Options), consistent spacing, and a scrollbar on the file list. No functionality changed. Tested and confirmed working.
- [x] **Add a Resize Preset system** — completed 2026-07-19. A "Resize Preset" `ttk.Combobox` offers 10 common sizes (up to 3840×2160 (4K)) plus "Custom"; picking a preset auto-fills and locks Width/Height, and "Custom" unlocks manual entry. Tested and confirmed working.
- [x] **Add persistent application settings** — completed 2026-07-19. Output Folder, Width, Height, Output Format, Resize Preset, and Keep Aspect Ratio are auto-saved to `settings.json` and auto-restored on startup. Tested across preset and Custom sessions (save → close → relaunch, values matched).
- [x] **Add Drag & Drop support** — completed 2026-07-19. Dropping JPG/JPEG/PNG/WEBP files onto the main window adds them to the file list (deduplicated, additive to the existing selection); unsupported files are ignored. Requires the new `tkinterdnd2` dependency. Tested: single file, multiple files (including space-containing paths), duplicate drop, and unsupported-file drop.
- [x] **Improve batch processing error reporting** — completed 2026-07-19. Failures no longer stop or silently reduce the count: each failure is caught, logged with filename + exact error message, and processing continues. A `Successful: X / Failed: Y` summary always shows, with a scrollable dialog listing failures when there are any. Tested with valid/corrupt/missing files mixed in one batch.
- [x] **Pin dependency versions in `requirements.txt`** — completed 2026-07-19. `Pillow>=12.3.0`, `tkinterdnd2>=0.6.2`. Verified installable via `pip install -r requirements.txt` dry-run.
- [x] **Add `.gitignore`** — completed 2026-07-19. Ignores `__pycache__/`, `*.pyc`, `settings.json`; verified source code is never ignored.
- [x] **Review repository for first public release** — completed 2026-07-19 (documentation-only, no functionality changes). Verified all important files are tracked/correctly ignored via a simulated full-structure `git add -A`. Identified one gap: no `LICENSE` file.
- [x] **Full code review** — completed 2026-07-19, no behavior change (regression-tested). Removed 4 dead `ImageProcessor` getters, deduplicated repeated GUI widget-manipulation code into two helper methods, simplified a redundant local variable, and added clarifying comments. Also fixed a `.gitignore` omission in `README.md`'s structure diagram.

### Current limitations

- **No `LICENSE` file** — needed before a genuinely public release; blocked on the user choosing a license type (MIT, Apache-2.0, GPL, etc.), which isn't something to pick automatically.
- **`README.md`, `requirements.txt`, `.gitignore`, and the launch scripts are still uncommitted** — they exist on disk and are current, but `git status` still shows them as untracked (see §9); nothing has actually run `git add`/`git commit` on them yet.

### Next recommended improvement

**Add a `LICENSE` file, then commit everything.** The repository is otherwise release-ready — all files are accounted for and `.gitignore` is correct — but it's missing a license, and none of the current documentation/config files (`README.md`, `requirements.txt`, `.gitignore`, `run.ps1`, `run.bat`) have actually been committed yet. Once a license is chosen, both of these can be resolved together with a single `git add -A && git commit`.

### Other possible improvements (backlog)

_None currently — LICENSE + committing (above) are the only open items._

---

## Quick Reference

| Task | Command |
|---|---|
| Run app | `cd C:\Users\AiDA\ai_tools\ImageToolbox` then `python main.py` |
| Install deps | `pip install -r requirements.txt` |
| PowerShell launch | `.\run.ps1` |
| Batch launch | Double-click `run.bat` |
