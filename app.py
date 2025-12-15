from flask import Flask, render_template, request, send_file
from werkzeug.security import check_password_hash
from datetime import datetime
import tempfile, io, os, logging, traceback

from App.Tool_1.generate_report import generate_pdf_report, ReportError
from App.Tool_2.generate_report import generate_cost_report, ReportError as Tool2ReportError

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = "scrypt:32768:8:1$npZSFtKm15iuaUk6$b2705e8cd58e8026cb3bb01cc05f75e0ac9ffbf03c8c5044d7caf7d1274d5617645f25213c7f3e37bad9af65bed540334ab835618e5207c61550d59dd25f9759"

app = Flask(__name__)

# Logging setup (single source of truth)
os.makedirs("App/logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("App/logs/app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# Login
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            return render_template("home.html")

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


# Tool 1
@app.route("/tool1", methods=["GET", "POST"])
def tool1():
    if request.method == "POST":
        file = request.files.get("excel_file")
        as_of_date_str = request.form.get("as_of_date")

        if not file or not as_of_date_str:
            return "Missing file or date", 400

        try:
            as_of_date = datetime.strptime(as_of_date_str, "%Y-%m-%d").date()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
                file.save(tmp.name)
                pdf_bytes = generate_pdf_report(tmp.name, as_of_date)

            return send_file(
                io.BytesIO(pdf_bytes),
                mimetype="application/pdf",
                as_attachment=True,
                download_name=f"Cost_Report_{as_of_date}.pdf"
            )

        except ReportError as e:
            logger.warning("Tool1 validation error: %s", str(e))
            return str(e), 400

        except Exception:
            logger.error("Tool1 crash")
            logger.debug(traceback.format_exc())
            return "Internal server error", 500

        finally:
            if "tmp" in locals() and os.path.exists(tmp.name):
                os.remove(tmp.name)

    return render_template("tool1.html")


# Tool 2
@app.route("/tool2", methods=["GET", "POST"])
def tool2():
    if request.method == "POST":
        file = request.files.get("excel_file")
        date_from = request.form.get("date_from")
        date_till = request.form.get("date_till")
        cost_code = request.form.get("cost_code")

        if not file:
            return "No Excel file uploaded.", 400

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
                file.save(tmp.name)
                pdf_buffer = generate_cost_report(tmp.name, date_from, date_till, cost_code)

            return send_file(
                pdf_buffer,
                mimetype="application/pdf",
                as_attachment=True,
                download_name="Detailed_Report.pdf"
            )

        except Tool2ReportError as e:
            logger.warning("Tool2 validation error: %s", str(e))
            return str(e), 400

        except Exception:
            logger.error("Tool2 crash")
            logger.debug(traceback.format_exc())
            return "Internal server error", 500

        finally:
            if "tmp" in locals() and os.path.exists(tmp.name):
                os.remove(tmp.name)

    return render_template("tool2.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
