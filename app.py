import os
import re
import sqlite3
from datetime import datetime

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


def valid_email(email: str) -> bool:
    return bool(_EMAIL_RE.match(email))


DEFAULT_PROJECTS = [
    {
        "title": "Smart Glasses - AI Vision Assistant",
        "description": (
            "An assistive wearable device for visually impaired users with real-time "
            "object detection, OCR, and voice feedback."
        ),
        "badge": "AI Vision",
        "tags": "Python, YOLO, Raspberry Pi, OpenCV, TTS",
        "media_type": "image",
        "media_path": "images/projects/smart-glasses.jpg",
        "icon": "👓",
    },
    {
        "title": "AI Medical Endoscope",
        "description": (
            "AI-enhanced endoscopy system that assists doctors in real-time lesion "
            "detection and clinical diagnosis support."
        ),
        "badge": "Medical AI",
        "tags": "TensorFlow, Computer Vision, Edge AI, Medical Devices",
        "media_type": "image",
        "media_path": "images/projects/medical-endoscope.jpg",
        "icon": "🔬",
    },
    {
        "title": "AI Vein Detection System",
        "description": (
            "Near-infrared imaging with computer vision to map veins for medical "
            "procedures and reduce patient discomfort."
        ),
        "badge": "Healthcare",
        "tags": "OpenCV, NIR Imaging, Raspberry Pi, PyTorch",
        "media_type": "image",
        "media_path": "images/projects/vein-detection.jpg",
        "icon": "🩺",
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
                badge       TEXT,
                tags        TEXT,
                media_type  TEXT    NOT NULL DEFAULT 'image',
                media_path  TEXT,
                icon        TEXT    DEFAULT '🚀',
                created_at  TEXT    NOT NULL
            );
            """
        )

        count = conn.execute("SELECT COUNT(*) AS c FROM projects").fetchone()["c"]
        if count == 0:
            now = datetime.utcnow().isoformat()
            for project in DEFAULT_PROJECTS:
                conn.execute(
                    """
                    INSERT INTO projects (title, description, badge, tags, media_type, media_path, icon, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        project["title"],
                        project["description"],
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


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=debug, host="0.0.0.0", port=port)


# Ensure DB and seed data exist in both local and production (gunicorn) runs.
init_db()
