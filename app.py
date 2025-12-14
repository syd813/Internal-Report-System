from flask import Flask, render_template, request, send_file, session, redirect, url_for, jsonify
from werkzeug.security import check_password_hash
from datetime import datetime
import tempfile, io, os, logging
from tools.Tool_1.generate_report import generate_pdf_report
from tools.Tool_2.generate_report import generate_cost_report
from functools import wraps

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = "scrypt:32768:8:1$npZSFtKm15iuaUk6$b2705e8cd58e8026cb3bb01cc05f75e0ac9ffbf03c8c5044d7caf7d1274d5617645f25213c7f3e37bad9af65bed540334ab835618e5207c61550d59dd25f9759"

# Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB upload limit

# Logging setup
os.makedirs("App/logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("App/logs/app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("CostReportApp")

# Login decorator
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

# Login route
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

# Home route
@app.route("/home")
@login_required
def home():
    return render_template("home.html")

# Tool 1 route
@app.route("/tool1", methods=["GET", "POST"])
@login_required
def tool1():
    if request.method == "POST":
        file = request.files.get("excel_file")
        as_of_date_str = request.form.get("as_of_date")

        if not file or not as_of_date_str:
            return jsonify({"error": "Missing file or date"}), 400
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            return jsonify({"error": "Invalid file type. Please upload Excel."}), 400

        as_of_date = datetime.strptime(as_of_date_str, "%Y-%m-%d").date()

        with tempfile.NamedTemporaryFile(suffix=".xlsx") as tmp:
            file.save(tmp.name)
            try:
                pdf_bytes = generate_pdf_report(tmp.name, as_of_date)
            except Exception as e:
                logger.exception("Tool1 report generation failed")
                return jsonify({"error": str(e)}), 400

        logger.info("Tool1 report generated for date: %s", as_of_date)
        return send_file(io.BytesIO(pdf_bytes),
                         mimetype="application/pdf",
                         as_attachment=True,
                         download_name=f"Cost_Report_{as_of_date}.pdf")

    return render_template("tool1.html")

# Tool 2 route
@app.route("/tool2", methods=["GET", "POST"])
@login_required
def tool2():
    if request.method == "POST":
        file = request.files.get("excel_file")
        date_from = request.form.get("date_from")
        date_till = request.form.get("date_till")
        cost_code = request.form.get("cost_code")

        if not file:
            return jsonify({"error": "No Excel file uploaded."}), 400
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            return jsonify({"error": "Invalid file type. Please upload Excel."}), 400

        with tempfile.NamedTemporaryFile(suffix=".xlsx") as tmp:
            file.save(tmp.name)
            try:
                pdf_buffer = generate_cost_report(tmp.name, date_from, date_till, cost_code)
            except ValueError as e:
                logger.warning("Tool2 validation error: %s", e)
                return jsonify({"error": str(e)}), 400
            except Exception as e:
                logger.exception("Tool2 report generation failed")
                return jsonify({"error": "Unexpected error generating report"}), 500

        logger.info("Tool2 report generated: date_from=%s, date_till=%s, cost_code=%s", date_from, date_till, cost_code)
        return send_file(pdf_buffer,
                         mimetype="application/pdf",
                         as_attachment=True,
                         download_name=f"Detailed_Report.pdf")
    return render_template("tool2.html")

# Logout route
@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
