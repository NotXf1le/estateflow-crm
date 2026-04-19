# EstateFlow CRM

EstateFlow CRM is a fully offline desktop CRM for a real estate agency built with Python and CustomTkinter. It is designed as a compact but production-oriented single-office product for daily operations: lead management, listings, deal pipeline, viewings, follow-ups, interaction history, reporting, CSV exports, and safe local backups.

## Features

- Local login and session flow with hashed passwords stored in `users.csv`
- Automatic first-run admin bootstrap
- Sidebar-driven desktop UI with CustomTkinter and grid-based layouts throughout
- Dashboard with KPI cards, recent activity, upcoming appointments, and stage summary
- Full CRUD for:
  - users/agents
  - clients/leads
  - properties/listings
  - deals/pipeline
  - appointments/viewings
  - tasks/follow-ups
  - interaction history
- CSV repository layer with deterministic schemas and atomic writes
- Safe-delete rules for referenced records
- Import/export workflows for entity tables
- Reporting screen with operational summaries and CSV export
- Backup snapshot creation for all CSV data files
- Audit log for important business actions
- Automated unit and smoke tests using the standard library

## Tech Stack

- Python 3.11+ recommended
- CustomTkinter for the application shell and forms
- `ttk.Treeview` for tabular grids
- CSV files as the only persistence layer
- Standard library for hashing, validation, logging, export, backup, and tests

## Project Structure

```text
estateflow-crm/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   ├── appointments.csv
│   ├── audit_log.csv
│   ├── clients.csv
│   ├── deals.csv
│   ├── interactions.csv
│   ├── properties.csv
│   ├── tasks.csv
│   └── users.csv
├── crm/
│   ├── bootstrap.py
│   ├── config.py
│   ├── enums.py
│   ├── formatters.py
│   ├── models.py
│   ├── utils.py
│   ├── validators.py
│   ├── repositories/
│   ├── services/
│   └── ui/
└── tests/
    ├── common.py
    ├── test_bootstrap.py
    ├── test_repository.py
    ├── test_services.py
    └── test_utils_and_validators.py
```

## Installation

1. Install Python 3.11 or newer.
2. Make sure your Python installation includes Tcl/Tk support.
3. Create and activate a virtual environment.
4. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Run the Application

```powershell
python app.py
```

On first launch the application initializes any missing CSV files inside `data/` and creates a default administrator account if `users.csv` is empty.

### Default Login

- Username: `admin`
- Password: `Admin123!`

## CSV Storage Design

All business data is stored in UTF-8 CSV files under `data/`. The application treats CSV as a real persistence layer rather than as a quick export format:

- Each file has a deterministic schema and column order
- Missing files are auto-created with headers
- Writes use a temporary file plus replace strategy for atomic updates
- Timestamps are stored in ISO format
- Validation runs before data is persisted
- Linked-record checks block unsafe deletes
- Audit events are written to `audit_log.csv`
- Backup snapshots copy all CSV files into timestamped folders under `backups/`

## Reports Included

- Deals by stage
- Revenue and commission summary
- Active listings by city and property type
- Overdue tasks by agent
- Appointments by status

## Testing

Run the automated suite with:

```powershell
python -m unittest discover -s tests -v
```

The suite covers:

- repository CRUD behavior
- initialization of missing CSV files
- validation rules
- ID generation
- commission auto-calculation
- query/filter helpers
- dependency-safe delete behavior
- bootstrap smoke initialization

## Local Architecture Limitations

- CSV storage is suitable for a local office workflow, but not for multi-user concurrent editing over a network share
- There is no remote sync, server process, or background job runner
- Reporting is operational rather than analytical BI
- Role support is intentionally lightweight: admin and agent
- Backup creation is file-based, not versioned snapshotting

## Screenshots

Screenshot placeholders can be added here after launching the application on a machine with a working Tk/Tcl runtime.

## Important Note

If `python app.py` fails with a Tk/Tcl initialization error, the issue is with the local Python/Tk installation rather than the CRM code. Install a Python build that includes a working Tcl/Tk runtime and rerun the app.
