# Image Toolbox

A small desktop GUI application for batch-resizing images, built with Python, tkinter, and ttk.

## Features

- Select multiple images (JPG, JPEG, PNG, WEBP) via a file dialog, or **drag and drop** them onto the main window
- Choose an output folder
- Pick a **Resize Preset** (64×64 up to 3840×2160 (4K)) or enter a **Custom** width/height
- Optional **Keep Aspect Ratio** — fits the image inside the requested box instead of stretching/squashing it
- Choose output format: JPG, PNG, or WEBP, with a **Quality** slider (1–100, default 95) for JPG/WEBP
- Never overwrites an existing output file — automatically saves as `name (1).ext`, `name (2).ext`, etc.
- Batch process on a background thread with a progress bar; the **Process Images** button is disabled while running
- If some images fail, a summary shows how many succeeded/failed and a scrollable dialog lists each failed filename with its error message; processing continues past individual failures
- Remembers your settings (output folder, size, format, preset, aspect-ratio choice) between runs

## Requirements

| Dependency | Notes |
|---|---|
| Python 3.14+ | Must be installed and on PATH |
| Pillow >=12.3.0 | Listed in `requirements.txt` |
| tkinterdnd2 >=0.6.2 | Listed in `requirements.txt` — enables drag-and-drop |
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

1. Click **Select Images**, or drag image files onto the window
2. Click **Select Output Folder**
3. Pick a **Resize Preset**, or leave it on **Custom** and enter Width/Height manually
4. Optionally check **Keep Aspect Ratio**
5. Choose an **Output Format** (default: JPG) and, for JPG/WEBP, adjust the **Quality** slider if needed
6. Click **Process Images**

Your choices are saved automatically and restored the next time you open the app.

## Project Structure

```
ImageToolbox/
├── main.py                # Entry point — launches the drag-and-drop-capable tkinter GUI
├── requirements.txt       # Python dependencies (Pillow, tkinterdnd2)
├── .gitignore              # Ignores __pycache__/, *.pyc, settings.json
├── run.ps1                # PowerShell launcher script
├── run.bat                # Windows batch launcher script
├── settings.json           # Auto-generated: your saved settings (created on first run)
└── app/
    ├── __init__.py
    ├── gui.py              # tkinter/ttk UI (ImageToolboxGUI)
    └── image_processor.py  # Image resize/save logic (ImageProcessor)
```

## Known Limitations

_None currently known._
