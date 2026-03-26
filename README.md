# Sales Pipeline Tracker

A desktop GUI app for tracking leads, managing pipeline stages, setting follow-up dates, filtering by status, and exporting data to JSON or CSV.

## Features

- add new leads
- edit existing leads
- delete leads
- stage tracking
- follow-up date tracking
- status filtering
- dashboard stats for total leads, active deals, overdue follow-ups, and open pipeline value
- overdue follow-up highlighting directly in the table
- local autosave to JSON
- manual export to JSON
- manual export to CSV
- clean desktop GUI

## Why this project exists

Sales and technical-sales work often involve managing multiple leads, tracking deal stages, and keeping follow-up timing organized. This project is a lightweight local tool designed to make pipeline tracking simple without needing a full CRM.

## Tech Stack

- Python 3
- Tkinter GUI
- JSON / CSV export
- Standard library only

## Project Structure

```bash
sales-pipeline-tracker/
├── pipeline_tracker.py
├── sample_pipeline.json
├── run_tracker.bat
├── launch_tracker.sh
├── app_icon.svg
├── app_icon.png
├── app_icon.ico
├── build_exe_instructions.md
├── requirements.txt
├── .gitignore
└── README.md
```

## How to Run

### Windows
Double-click:

```bash
run_tracker.bat
```

### Linux / macOS
```bash
python3 pipeline_tracker.py
```

or:

```bash
bash launch_tracker.sh
```

## Data Behavior

- The app autosaves local data into `pipeline_data.json`
- You can also export a clean copy to JSON or CSV anytime
- You can import a JSON file back into the tracker

## Future Improvements

- search and sorting
- reminders for overdue follow-ups
- summary dashboard metrics
- drag-and-drop import
- packaged standalone executable

## License

MIT
