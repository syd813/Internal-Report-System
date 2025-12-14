# INTERNAL REPORT SYSTEM

A Flask-based web application for generating **cost reports in PDF format**. The system contains **two tools**:

* **Tool 1:** Summary cost report.
* **Tool 2:** Detailed cost report with optional filters.

Includes secure admin login, file validation, logging, and automatic cleanup of temporary files.

---

## Project Structure

```
project/
├── app.py                     # Main Flask app
├── App/
│   ├── Tool_1/
│   │   └── generate_report.py # Summary report logic
│   └── Tool_2/
│       └── generate_report.py # Detailed report logic
├── templates/                 # HTML templates
│   ├── login.html
│   ├── home.html
│   ├── tool1.html
│   └── tool2.html
├── static/                    # CSS and JS
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
└── README.md                  # This file
```

---

Install dependencies:

```bash
pip install flask pandas reportlab openpyxl werkzeug
```

---

## Setup & Running

1. **Create a virtual environment** (recommended):

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or source venv/bin/activate  # Linux/Mac
```

2. **Install dependencies**:

```bash
pip install -r requirements.txt
```

3. **Run the Flask app**:

```bash
python app.py
```

4. **Open in browser**:

```
http://localhost:5000/
```

---

## Login

* Admin username: `admin`
* Admin password: *(provide separately; stored securely as a hash)*

---

## Tool 1 – Summary Cost Report

### Usage

1. Go to `/tool1` after login.
2. Upload an Excel file.
3. Select the **"As of" date**.
4. Click **Generate PDF**.
5. PDF will download automatically.

### Excel Requirements

* Required columns:

  * `Group Name`
  * `Cost Code`
  * `Cost Description`
  * `Budget`, `Actual`, `Provision`, `Total Cost`, `Variance`
* Optional:

  * `Project Number`

### Features

* Groups costs by `Group Name` and `Cost Code`.
* Calculates **group totals** and **grand total**.
* Safely handles numeric columns.

---

## Tool 2 – Detailed Cost Report

### Usage

1. Go to `/tool2` after login.
2. Upload an Excel file.
3. Optionally, provide:

   * **Date From**
   * **Date Till**
   * **Cost Code**
4. Click **Generate PDF**.
5. PDF will download automatically.

### Excel Requirements

* Required columns:

  * `Date`
  * `Cost Code`
  * `Cost Description`
  * `Actual`
* Optional columns:

  * `Narration`
  * `Supplier name`
  * `LPO NO`, `MRIR NO`, `PV REF NO`

### Features

* Shows detailed entries with all relevant columns.
* Summarizes **total amount** at the bottom.
* Filters applied automatically if provided.
* Handles invalid or missing data gracefully.

---

## Security & Logging

* Login required for both tools.
* Maximum upload size: 10 MB.
* Temporary files are cleaned automatically.
* Logging:

  * Successful and failed login attempts
  * Report generation events
  * Validation errors and unexpected exceptions

---

