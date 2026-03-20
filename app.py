import os
import re
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def valid_email(email: str) -> bool:
    return bool(_EMAIL_RE.match(email))


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables on first run."""
    with get_db() as conn:
        conn.executescript("""
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
        """)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/contact", methods=["POST"])
def contact():
    """Handle service / contact form submissions."""
    data = request.get_json(silent=True) or request.form.to_dict()

    name    = (data.get("name")    or "").strip()
    email   = (data.get("email")   or "").strip()
    phone   = (data.get("phone")   or "").strip()
    service = (data.get("service") or "").strip()
    message = (data.get("message") or "").strip()

    if not all([name, email, service, message]):
        return jsonify({"success": False, "error": "Please fill in all required fields."}), 400

    if not valid_email(email):
        return jsonify({"success": False, "error": "Please enter a valid email address."}), 400


        conn.execute(
            "INSERT INTO service_requests (name, email, phone, service, message, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (name, email, phone, service, message, datetime.utcnow().isoformat())
        )

    return jsonify({"success": True, "message": "Thank you! Your request has been received. I'll get back to you soon."})


@app.route("/api/order", methods=["POST"])
def order():
    """Handle product order submissions."""
    data = request.get_json(silent=True) or request.form.to_dict()

    name     = (data.get("name")     or "").strip()
    email    = (data.get("email")    or "").strip()
    phone    = (data.get("phone")    or "").strip()
    product  = (data.get("product")  or "").strip()
    message  = (data.get("message")  or "").strip()

    try:
        quantity = max(1, int(data.get("quantity") or 1))
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Invalid quantity value."}), 400

    if not all([name, email, product]):
        return jsonify({"success": False, "error": "Please fill in all required fields."}), 400

    if not valid_email(email):
        return jsonify({"success": False, "error": "Please enter a valid email address."}), 400


        conn.execute(
            "INSERT INTO product_orders (name, email, phone, product, quantity, message, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, email, phone, product, quantity, message, datetime.utcnow().isoformat())
        )

    return jsonify({"success": True, "message": "Order received! I'll contact you shortly to confirm the details."})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    init_db()
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug, host="0.0.0.0", port=5000)
