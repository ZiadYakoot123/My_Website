import os
import re
import smtplib
import sqlite3
from datetime import datetime
from email.message import EmailMessage

from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

DB_PATH = os.environ.get("DATABASE_PATH", os.path.join(os.path.dirname(__file__), "database.db"))
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "change-this-secret-key")
app.config["TEMPLATES_AUTO_RELOAD"] = True

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD_HASH = os.environ.get(
    "ADMIN_PASSWORD_HASH", generate_password_hash(os.environ.get("ADMIN_PASSWORD", "admin123"))
)

_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "ziadyakout6@gmail.com")


def send_service_request_email(name: str, email: str, phone: str, service: str, message: str) -> bool:
    """Send a service request notification when SMTP is configured."""
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_username = os.environ.get("SMTP_USERNAME")
    smtp_password = os.environ.get("SMTP_PASSWORD")

    if not all([smtp_host, smtp_username, smtp_password, CONTACT_EMAIL]):
        return False

    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    sender = os.environ.get("SMTP_FROM", smtp_username)
    email_message = EmailMessage()
    email_message["Subject"] = f"New service request: {service}"
    email_message["From"] = sender
    email_message["To"] = CONTACT_EMAIL
    email_message["Reply-To"] = email
    email_message.set_content(
        "A new service request was submitted from your portfolio website.\n\n"
        f"Name: {name}\n"
        f"Email: {email}\n"
        f"Phone: {phone or 'Not provided'}\n"
        f"Service: {service}\n\n"
        "Project details:\n"
        f"{message}\n"
    )

    try:
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=15) as smtp:
                smtp.login(smtp_username, smtp_password)
                smtp.send_message(email_message)
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as smtp:
                smtp.starttls()
                smtp.login(smtp_username, smtp_password)
                smtp.send_message(email_message)
    except (OSError, smtplib.SMTPException, ValueError):
        app.logger.exception("Could not send service request email")
        return False

    return True


def valid_email(email: str) -> bool:
    return bool(_EMAIL_RE.match(email))


DEFAULT_PROJECTS = [
    {
        "title": "AI Digital Twin for Tablet Compression",
        "description": "An AI framework for reducing physical trial-and-error in pharmaceutical manufacturing.",
        "challenge": "Pharmaceutical teams need to tune compression settings while protecting quality and reducing material waste.",
        "solution": "Forward models using Random Forest and XGBoost predict tablet weight, thickness, and friability. Inverse modeling with Histogram-based Gradient Boosting proposes fill depth and compression force settings.",
        "impact": "A data-driven route to faster process development, more consistent tablets, and fewer experimental cycles.",
        "badge": "Pharma AI",
        "tags": "Digital Twin, Random Forest, XGBoost, Process Optimization",
        "media_type": "none",
        "media_path": "",
        "icon": "💊",
    },
    {
        "title": "SOPs & Guidelines Chatbot",
        "description": "A GMP-grounded assistant for fast, traceable answers to SOP and guideline questions.",
        "challenge": "Teams lose time searching across controlled documents and risk relying on outdated or incomplete guidance.",
        "solution": "Retrieval-Augmented Generation fetches current, approved SOPs and returns concise answers with source citations.",
        "impact": "Faster knowledge access, fewer interpretation errors, and audit-ready responses grounded in approved content.",
        "badge": "GMP Automation",
        "tags": "RAG, LLMs, GMP, Document Retrieval",
        "media_type": "none",
        "media_path": "",
        "icon": "📚",
    },
    {
        "title": "Smart Deviation & Risk Assessment Agent",
        "description": "An automated QA workflow that turns BMS alarms into structured review-ready documentation.",
        "challenge": "Alarm investigations require teams to correlate sensor history, procedures, and context before a deviation can be assessed.",
        "solution": "The agent captures BMS sensor data, retrieves knowledge-base documents, and drafts the deviation report, likely causes, corrective actions, and risk assessment for QA review.",
        "impact": "Shorter investigation cycles, more consistent documentation, and better use of QA expertise where human judgment matters most.",
        "badge": "Quality Systems",
        "tags": "AI Agents, BMS, Root Cause Analysis, QA",
        "media_type": "none",
        "media_path": "",
        "icon": "⚠️",
    },
    {
        "title": "AI Diagnosis Software for Gastrointestinal Endoscopes",
        "description": "An intelligent endoscopy platform that supports clinicians during diagnosis and training.",
        "challenge": "Junior staff and endoscopists need timely visual and procedural support while building diagnostic confidence.",
        "solution": "NLP, LLM transformers, and computer vision detect diseases, generate interactive diagnostic descriptions, and respond to voice commands for zooming or image capture.",
        "impact": "A more accessible learning curve and richer real-time decision support. Research accepted at the International Congress of AI in Health 2024.",
        "badge": "Healthcare AI",
        "tags": "Computer Vision, NLP, LLM Transformers, Medical Devices",
        "media_type": "none",
        "media_path": "",
        "icon": "🔬",
    },
    {
        "title": "Bearing RUL Fault Detection",
        "description": "Predictive maintenance models for detecting bearing faults and estimating remaining useful life.",
        "challenge": "Unexpected bearing failures create downtime, maintenance cost, and avoidable production disruption.",
        "solution": "Machine learning models analyze equipment signals to identify fault patterns and estimate Remaining Useful Life before failure.",
        "impact": "Earlier intervention, better maintenance planning, and improved equipment availability across industrial operations.",
        "badge": "Predictive Maintenance",
        "tags": "RUL Estimation, Fault Detection, Condition Monitoring, ML",
        "media_type": "none",
        "media_path": "",
        "icon": "⚙️",
    },
    {
        "title": "General Automation & AI Systems",
        "description": "End-to-end automation for complex industrial and business workflows.",
        "challenge": "Disconnected tools and repetitive manual processes slow decisions and make operational knowledge difficult to scale.",
        "solution": "I design system architectures, develop Python automations, connect data sources, and deploy AI solutions around real operational constraints.",
        "impact": "Streamlined workflows, clearer information flow, and practical AI adoption that connects engineering effort to measurable business value.",
        "badge": "Automation",
        "tags": "Python, System Architecture, Workflow Automation, Deployment",
        "media_type": "none",
        "media_path": "",
        "icon": "🤖",
    },
]


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables and seed default projects on first run."""
    with get_db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS service_requests (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL,
                email       TEXT    NOT NULL,
                phone       TEXT,
                service     TEXT    NOT NULL,
                message     TEXT    NOT NULL,
                created_at  TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS product_orders (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL,
                email       TEXT    NOT NULL,
                phone       TEXT,
                product     TEXT    NOT NULL,
                quantity    INTEGER NOT NULL DEFAULT 1,
                message     TEXT,
                created_at  TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS projects (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT    NOT NULL,
                description TEXT    NOT NULL,
                challenge   TEXT    NOT NULL DEFAULT '',
                solution    TEXT    NOT NULL DEFAULT '',
                impact      TEXT    NOT NULL DEFAULT '',
                badge       TEXT,
                tags        TEXT,
                media_type  TEXT    NOT NULL DEFAULT 'image',
                media_path  TEXT,
                icon        TEXT    DEFAULT '🚀',
                created_at  TEXT    NOT NULL
            );
            """
        )


        columns = {row[1] for row in conn.execute("PRAGMA table_info(projects)").fetchall()}
        for column in ("challenge", "solution", "impact"):
            if column not in columns:
                conn.execute(f"ALTER TABLE projects ADD COLUMN {column} TEXT NOT NULL DEFAULT ''")
        existing_titles = {
            row["title"] for row in conn.execute("SELECT title FROM projects").fetchall()
        }
        now = datetime.utcnow().isoformat()
        for project in DEFAULT_PROJECTS:
            if project["title"] not in existing_titles:
                conn.execute(
                    """
                    INSERT INTO projects (
                        title, description, challenge, solution, impact, badge,
                        tags, media_type, media_path, icon, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        project["title"],
                        project["description"],
                        project["challenge"],
                        project["solution"],
                        project["impact"],
                        project["badge"],
                        project["tags"],
                        project["media_type"],
                        project["media_path"],
                        project["icon"],
                        now,
                    ),
                )


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------


def is_admin_logged_in() -> bool:
    return bool(session.get("admin_logged_in"))


def require_admin():
    if not is_admin_logged_in():
        return redirect(url_for("admin_login"))
    return None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.route("/")
def index():
    with get_db() as conn:
        projects = conn.execute("SELECT * FROM projects ORDER BY id DESC").fetchall()
    return render_template("index.html", projects=projects)


@app.route("/api/contact", methods=["POST"])
def contact():
    """Handle service / contact form submissions."""
    data = request.get_json(silent=True) or request.form.to_dict()

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    phone = (data.get("phone") or "").strip()
    service = (data.get("service") or "").strip()
    message = (data.get("message") or "").strip()

    if not all([name, email, service, message]):
        return jsonify({"success": False, "error": "Please fill in all required fields."}), 400

    if not valid_email(email):
        return jsonify({"success": False, "error": "Please enter a valid email address."}), 400

    with get_db() as conn:
        conn.execute(
            "INSERT INTO service_requests (name, email, phone, service, message, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (name, email, phone, service, message, datetime.utcnow().isoformat()),
        )

    email_sent = send_service_request_email(name, email, phone, service, message)
    if not email_sent and os.environ.get("SMTP_HOST"):
        return jsonify(
            {
                "success": False,
                "error": "Your request was saved, but the email notification could not be sent. Please try again or contact me directly.",
            }
        ), 503

    return jsonify(
        {
            "success": True,
            "message": "Thank you! Your request has been received. I'll get back to you soon.",
        }
    )


@app.route("/api/order", methods=["POST"])
def order():
    """Handle product order submissions."""
    data = request.get_json(silent=True) or request.form.to_dict()

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    phone = (data.get("phone") or "").strip()
    product = (data.get("product") or "").strip()
    message = (data.get("message") or "").strip()

    try:
        quantity = max(1, int(data.get("quantity") or 1))
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Invalid quantity value."}), 400

    if not all([name, email, product]):
        return jsonify({"success": False, "error": "Please fill in all required fields."}), 400

    if not valid_email(email):
        return jsonify({"success": False, "error": "Please enter a valid email address."}), 400

    with get_db() as conn:
        conn.execute(
            "INSERT INTO product_orders (name, email, phone, product, quantity, message, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, email, phone, product, quantity, message, datetime.utcnow().isoformat()),
        )

    return jsonify(
        {
            "success": True,
            "message": "Order received! I'll contact you shortly to confirm the details.",
        }
    )


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if is_admin_logged_in():
        return redirect(url_for("admin_dashboard"))

    error = None
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))

        error = "Invalid username or password."

    return render_template("admin_login.html", error=error)


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_login"))


@app.route("/admin")
def admin_dashboard():
    auth_redirect = require_admin()
    if auth_redirect:
        return auth_redirect

    with get_db() as conn:
        projects = conn.execute("SELECT * FROM projects ORDER BY id DESC").fetchall()
        service_requests = conn.execute(
            "SELECT * FROM service_requests ORDER BY id DESC LIMIT 100"
        ).fetchall()
        product_orders = conn.execute(
            "SELECT * FROM product_orders ORDER BY id DESC LIMIT 100"
        ).fetchall()

    return render_template(
        "admin_dashboard.html",
        projects=projects,
        service_requests=service_requests,
        product_orders=product_orders,
    )


@app.route("/admin/projects", methods=["POST"])
def admin_add_project():
    auth_redirect = require_admin()
    if auth_redirect:
        return auth_redirect

    title = (request.form.get("title") or "").strip()
    description = (request.form.get("description") or "").strip()
    badge = (request.form.get("badge") or "").strip()
    tags = (request.form.get("tags") or "").strip()
    media_type = (request.form.get("media_type") or "image").strip().lower()
    media_path = (request.form.get("media_path") or "").strip()
    icon = (request.form.get("icon") or "🚀").strip()

    if not title or not description:
        return redirect(url_for("admin_dashboard"))

    if media_type not in {"image", "video", "none"}:
        media_type = "image"

    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO projects (title, description, badge, tags, media_type, media_path, icon, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                description,
                badge,
                tags,
                media_type,
                media_path,
                icon,
                datetime.utcnow().isoformat(),
            ),
        )

    return redirect(url_for("admin_dashboard"))


@app.route("/admin/projects/<int:project_id>/delete", methods=["POST"])
def admin_delete_project(project_id: int):
    auth_redirect = require_admin()
    if auth_redirect:
        return auth_redirect

    with get_db() as conn:
        conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))

    return redirect(url_for("admin_dashboard"))


# Ensure DB and seed data exist before serving requests in both local and
# production (gunicorn) runs.
init_db()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug, host="0.0.0.0", port=5000)
