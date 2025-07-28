# Windows Task Scheduler Frontend

This project provides a Streamlit-based interface to manage Python script tasks with Windows Task Scheduler.

## Features
- List tasks under `\PyTasks` namespace
- Create, edit, delete, enable/disable tasks
- View logs and run tasks immediately

## Setup
1. Install Python 3.8+ and pip.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   streamlit run app.py
   ```

## Packaging
To build a standalone EXE with PyInstaller:
```bash
pip install pyinstaller
pyinstaller --onefile app.py
```
The resulting executable will be in the `dist` directory.

## Example XML Template
See `templates/task_template.xml` for the base schedule task template used for creation.
