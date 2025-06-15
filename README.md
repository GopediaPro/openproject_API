## How to run bulk work package creation

1. Prepare an Excel file named `workpackages.xlsx` in the project root directory. The file should have the following columns:
   - subject (required)
   - project_id (required)
   - author_id (required)
   - type_id (optional, default: 1)
   - status_id (optional, default: 1)
   - priority_id (optional, default: 9)
   - assignee_id (optional)
   - category_id (optional)
   - start_date (optional, format: YYYY-MM-DD)
   - due_date (optional, format: YYYY-MM-DD)
   - description (optional)
   - duration (optional,but if there are start_date & due_date, required)

2. Activate your virtual environment and install dependencies if you haven't already:

```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

3. Run the bulk work package creation command:

```bash
python3 main.py bulk-create-work-packages
```

Each work package in the Excel file will be created via the OpenProject API, and the result will be printed for each row.

```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
python3 app.py
```
