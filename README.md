# Image Toolbox

A small desktop GUI application for batch-resizing images, built with Python and tkinter.

## Features

- Select multiple images (JPG, JPEG, PNG, WEBP)
- Choose an output folder
- Set a target width and height (applied exactly, no aspect-ratio lock)
- Choose output format: JPG, PNG, or WEBP
- Batch process on a background thread with a progress bar

## Requirements

| Dependency | Notes |
|---|---|
| Python 3.14+ | Must be installed and on PATH |
| Pillow | Listed in `requirements.txt` |
| tkinter | Bundled with standard Python on Windows |

## Installation

```powershell
cd C:\Users\AiDA\ai_tools\ImageToolbox
pip install -r requirements.txt
```

## Usage

### Run

```powershell
cd C:\Users\AiDA\ai_tools\ImageToolbox
python main.py
```

Or use one of the launch scripts:

```powershell
.\run.ps1
```

Or double-click `run.bat` in File Explorer.

### Workflow

1. Click **Select Images**
2. Click **Select Output Folder**
3. Enter **Width** and **Height**, then click **Save Resize Values**
4. Choose an **Output Format** (default: JPG)
5. Click **Process Images**

## Project Structure

```
ImageToolbox/
├── main.py                # Entry point — launches the tkinter GUI
├── requirements.txt       # Python dependencies (Pillow)
├── run.ps1                # PowerShell launcher script
├── run.bat                # Windows batch launcher script
└── app/
    ├── __init__.py
    ├── gui.py              # tkinter UI (ImageToolboxGUI)
    └── image_processor.py  # Image resize/save logic (ImageProcessor)
```

## Known Limitations

- Resize values must be saved (via **Save Resize Values**) before processing.
- No aspect-ratio lock — images may appear stretched or squashed.
- Per-file failures are silent; only the total success count is shown.
- Existing files in the output folder with the same name are overwritten without confirmation.
