# Build a Windows .exe for Sales Pipeline Tracker

## 1) Open terminal in the project folder

```bash
cd path\to\sales-pipeline-tracker
```

## 2) Optional virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

## 3) Install PyInstaller

```bash
pip install pyinstaller
```

## 4) Build the .exe

```bash
pyinstaller --onefile --windowed --name SalesPipelineTracker --icon app_icon.ico pipeline_tracker.py
```

## 5) Finished executable

```bash
dist\SalesPipelineTracker.exe
```

## Notes
- `--windowed` keeps it as a GUI app
- `--onefile` bundles it into one executable
- `--icon app_icon.ico` gives it a cleaner branded icon
