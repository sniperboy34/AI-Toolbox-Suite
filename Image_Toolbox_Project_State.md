# Image Toolbox — Project State

**Last updated:** 2026-07-18  
**Location:** `C:\Users\AiDA\ai_tools\ImageToolbox`

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

The UI is implemented in `app/gui.py` as class `ImageToolboxGUI`.

### Controls

| Control | Purpose |
|---|---|
| **Select Images** | Opens a file dialog for JPG, JPEG, PNG, WEBP; populates the file list |
| **Select Output Folder** | Chooses where processed images are saved |
| **Width / Height** | Text fields for target pixel dimensions |
| **Save Resize Values** | Validates and stores width/height (must be positive integers) |
| **Output Format** | Dropdown: JPG, PNG, or WEBP |
| **Process Images** | Runs batch resize on all selected files |
| **Progress bar** | Shows per-file progress during processing |
| **Status label** | Displays ready state, selection count, and processing progress |
| **File listbox** | Shows basenames of selected images |

### Processing behavior

- Processing runs on a **background thread** so the UI stays responsive.
- Each image is resized to the exact width and height entered (no aspect-ratio preservation).
- Output filenames keep the original basename with the chosen extension (e.g. `photo.jpg` → `photo.png`).
- **JPG output:** RGBA and LA images are composited onto a white background before saving.
- A completion dialog reports how many images were processed successfully.

### Typical workflow

1. Click **Select Images**
2. Click **Select Output Folder**
3. Enter width and height, then click **Save Resize Values**
4. Choose output format (default: JPG)
5. Click **Process Images**

---

## 7. Image Processing (`app/image_processor.py`)

Class `ImageProcessor` holds state and performs the actual resize/save:

- **State:** selected files, output folder, width, height, output format
- **`set_resize_values()`** — validates that width and height are digit strings
- **`resize_image()`** — opens image with Pillow, resizes, converts for JPG if needed, saves to output folder
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

### Current limitations

- **Resize values must be saved first** — clicking **Process Images** without **Save Resize Values** shows an error even if fields are filled in.
- **No aspect-ratio lock** — width and height are applied independently; images may appear stretched or squashed.
- **Silent per-file failures** — if one image fails (corrupt file, permission error), it is skipped; only the success count is shown.
- **No overwrite confirmation** — existing files in the output folder with the same name are overwritten.
- **No README** — this document serves as the project reference for now.
- **Launch scripts not committed** — `requirements.txt`, `run.ps1`, and `run.bat` are still untracked.

### Possible improvements

- Add a `README.md` with quick-start instructions
- Pin Pillow version in `requirements.txt` (e.g. `Pillow>=12.3.0`)
- Commit launch scripts and `requirements.txt`
- Add aspect-ratio preserve toggle
- Show per-file error messages in the UI
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
