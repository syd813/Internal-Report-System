# INTERNAL REPORT SYSTEM

A Flask-based web application for generating **cost reports in PDF format** from Excel files. The system provides **two reporting tools**, secure admin login, centralized logging, validation, and automatic cleanup of temporary files.

---

## Features

* Secure admin login (hashed password)
* Two PDF reporting tools (Summary & Detailed)
* Excel validation with clear error messages
* Centralized logging (file + console)
* Automatic temporary file cleanup
* Clean separation of app logic and report tools

---

## Project Structure

```
project/
│
├── app.py
│
├── App/
│   ├── Tool_1/
│   │   └── generate_report.py
│   └── Tool_2/
│       └── generate_report.py
│
├── templates/
│   ├── home.html
│   ├── tool1.html
│   ├── tool2.html
│   └── login.html
│
├── static/
│   ├── css/
│   │   ├── home.css
│   │   ├── tool1.css
│   │   ├── tool2.css
│   │   └── login.css
│   └── js/
│       ├── home.js
│       ├── tool1.js
│       ├── tool2.js
│       └── login.js
│
├── App/logs/
│   └── app.log
│
├── requirements.txt
└── README.md
```

---

## Installation

### 1. Create virtual environment (recommended)

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux / macOS
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

**Required packages**

* Flask
* pandas
* reportlab
* openpyxl
* werkzeug

---

## Running the Application

```bash
python app.py
```

Open in browser:

```
http://localhost:5000/
```

---

## Authentication

* **Username:** `admin`
* **Password:** Stored securely as a hash in `app.py`

Login is required to access both tools.

---

## Tool 1 — Summary Cost Report

### Purpose

Generates a **grouped summary PDF** with totals and grand totals.

### Usage

1. Login
2. Navigate to `/tool1`
3. Upload Excel file
4. Select **As Of Date**
5. Generate PDF

### Required Excel Columns

* `Group Name`
* `Cost Code`
* `Cost Description`
* `Budget`
* `Actual`
* `Provision`
* `Total Cost`
* `Variance`

### Optional Columns

* `Project Number`
* `Date` (used for filtering by *As Of* date)

### Output

* Group-wise totals
* Grand total at bottom
* A3 landscape PDF

---

## Tool 2 — Detailed Cost Report

### Purpose

Generates a **detailed transactional PDF** with optional filters.

### Usage

1. Login
2. Navigate to `/tool2`
3. Upload Excel file
4. Optionally provide:

   * Date From
   * Date Till
   * Cost Code
5. Generate PDF

### Required Excel Columns

* `Date`
* `Cost Code`
* `Cost Description`
* `Actual`

### Optional Columns

* `Narration`
* `Supplier name`
* `LPO NO`
* `MRIR NO`
* `PV REF NO`

### Output

* Row-level cost details
* Total amount summary
* A4 landscape PDF

---

## Error Handling & Validation

* Missing or invalid columns are detected early
* Invalid dates and numeric values are handled safely
* Empty results return clear validation errors
* Tools raise domain-specific exceptions
* `app.py` controls HTTP responses and user messaging

---

## Logging

Logging is configured centrally in `app.py`:

* Application events
* Validation errors
* Tool failures
* Unexpected crashes

Logs are written to:

```
App/logs/app.log
```

---

## Security Notes

* Passwords are never stored in plain text
* File uploads are validated
* Temporary files are deleted after processing
* Debug mode should be disabled in production

---

## Production Checklist

* Disable `debug=True`
* Add `.gitignore` (venv, logs, `__pycache__`)
* Rotate logs if needed
* Set secret keys via environment variables

---

## License

Internal use o
