# Image Toolbox — Project State

**Last updated:** 2026-07-19  
**Location:** `C:\Users\AiDA\ai_tools\ImageToolbox`  
**Status:** Stable — select/resize/convert workflow verified working end-to-end. Since the last update: a JPEG/WEBP quality slider (1–100, default 95) was added, and the GUI was rebuilt with ttk widgets (grouped LabelFrame sections, consistent spacing, a scrollbar on the file list) with no functional changes. No open bugs.

---

## 1. Project Overview

**Image Toolbox** is a small desktop GUI application for batch-resizing images. Users select one or more image files, choose an output folder, set target dimensions and output format, then process all images in one run.

| Layer | Technology |
|---|---|
| Language | Python 3.14.6 |
| GUI | tkinter (stdlib) |
| Image processing | Pillow (PIL) |
| Platform | Windows (primary target) |

**Entry point:** `main.py` creates a tkinter root window and launches `ImageToolboxGUI`.

---

## 2. Current File Structure

```
ImageToolbox/
├── main.py                        # Entry point — launches tkinter GUI
├── requirements.txt               # Python dependencies (Pillow)
├── run.ps1                        # PowerShell launcher script
├── run.bat                        # Windows batch launcher script
├── Image_Toolbox_Project_State.md # This document
└── app/
    ├── __init__.py                # Empty package marker
    ├── gui.py                     # tkinter UI (ImageToolboxGUI)
    └── image_processor.py         # Image resize/save logic (ImageProcessor)
```

**Git-tracked files (Initial commit):** `main.py`, `app/__init__.py`, `app/gui.py`, `app/image_processor.py`

**Untracked (not yet committed):** `requirements.txt`, `run.ps1`, `run.bat`, `Image_Toolbox_Project_State.md`

---

## 3. Dependencies

| Dependency | Version / Status | Notes |
|---|---|---|
| **Python** | 3.14.6 | Installed and on PATH (`python --version`) |
| **Pillow** | 12.3.0 | Required for image I/O and resizing. Listed in `requirements.txt` |
| **tkinter** | Bundled | Included with standard Python on Windows; no separate install |

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
| **Keep Aspect Ratio** | Checkbox. When checked, the image is scaled to fit inside the width/height box without distorting it. When unchecked, width and height are applied exactly (may stretch/squash) |
| **Output Format** | Dropdown: JPG, PNG, or WEBP |
| **Quality (JPEG/WEBP)** | Slider, 1–100, default 95. Only applied when saving as JPEG or WEBP; ignored for PNG |
| **Process Images** | Runs batch resize on all selected files; disabled while processing, re-enabled when done (success or error) |
| **Progress bar** | Shows per-file progress during processing |
| **Status label** | Displays ready state, selection count, and processing progress |
| **File listbox** | Shows basenames of selected images (with a scrollbar) |

### Processing behavior

- Processing runs on a **background thread** so the UI stays responsive.
- The **Process Images** button is disabled the moment processing starts and re-enabled when it finishes, whether it finishes successfully or with an error — this prevents overlapping runs from a double-click.
- Width and height are read from the entry fields at the moment **Process Images** is clicked and validated then (must be positive integers), rather than requiring a separate save step.
- If **Keep Aspect Ratio** is checked, each image is scaled to fit inside the width/height box while preserving its original proportions. If unchecked, the image is resized to the exact width and height entered (may stretch/squash).
- Output filenames keep the original basename with the chosen extension (e.g. `photo.jpg` → `photo.png`).
- If a file with the target output name already exists, the new file is saved as `name (1).ext`, `name (2).ext`, etc. instead of overwriting it.
- **JPG output:** RGBA and LA images are composited onto a white background before saving.
- For JPEG and WEBP output, the **Quality** slider value (1–100, default 95) is passed to Pillow's save; PNG ignores it since PNG is lossless.
- A completion dialog reports how many images were processed successfully.

### Typical workflow

1. Click **Select Images**
2. Click **Select Output Folder**
3. Enter width and height
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
- **Error handling:** exceptions during a single image return `False` (failure is not surfaced per file in the UI)

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

**Untracked:** `requirements.txt`, `run.ps1`, `run.bat`, `Image_Toolbox_Project_State.md`, `__pycache__/` directories

---

## 10. Known Limitations / Next Steps

### Completed improvements

- [x] **Disable "Process Images" button while processing** — completed 2026-07-19. Prevents overlapping background threads from racing on the same temp file. Tested and confirmed working.
- [x] **Remove the "Save Resize Values" button** — completed 2026-07-19. Width/height are now read and validated directly when **Process Images** is clicked. Tested and confirmed working.
- [x] **Prevent overwriting existing output files** — completed 2026-07-19. Output files that would collide with an existing name are now auto-numbered (`name (1).ext`, `name (2).ext`, ...). Tested and confirmed working.
- [x] **Add aspect-ratio preserve toggle** — completed 2026-07-19. A "Keep Aspect Ratio" checkbox fits the image inside the requested width/height box without distorting it when checked; unchecked behavior (exact stretch) is unchanged. Tested and confirmed working.
- [x] **Add a JPEG/WEBP quality slider** — completed 2026-07-19. Slider ranges 1–100, defaults to 95, and only affects JPEG/WEBP saves (PNG ignores it). Tested and confirmed working.
- [x] **Improve the GUI layout with ttk widgets** — completed 2026-07-19. Rebuilt with `ttk` widgets, grouped sections (Files / Resize Options / Output Options), consistent spacing, and a scrollbar on the file list. No functionality changed. Tested and confirmed working.

### Current limitations

- **Silent per-file failures** — if one image fails (corrupt file, permission error), it is skipped; only the success count is shown.
- **No README** — this document serves as the project reference for now.
- **Launch scripts not committed** — `requirements.txt`, `run.ps1`, and `run.bat` are still untracked.

### Next recommended improvement

**Show per-file error messages in the UI.** Right now a failed image is silently skipped and only the aggregate success count is shown at the end, so if some images fail there's no way to tell which ones or why without checking the output folder manually. Surfacing the filename and error reason for each failure (e.g. in the status label, a scrollable log area, or the completion dialog) would make failures actionable instead of just a lower number. This was already the recommended next step before the quality slider and ttk redesign were implemented, and remains the highest-value item still open.

### Other possible improvements (backlog)

- Add a `README.md` with quick-start instructions
- Pin Pillow version in `requirements.txt` (e.g. `Pillow>=12.3.0`)
- Commit launch scripts and `requirements.txt`
- Add drag-and-drop for image selection
- Add `.gitignore` for `__pycache__/`

---

## Quick Reference

| Task | Command |
|---|---|
| Run app | `cd C:\Users\AiDA\ai_tools\ImageToolbox` then `python main.py` |
| Install deps | `pip install -r requirements.txt` |
| PowerShell launch | `.\run.ps1` |
| Batch launch | Double-click `run.bat` |
