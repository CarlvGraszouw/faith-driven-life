"""
Grocery best-deals API – host on Oracle Linux, extend with auth + payments to sell.
"""
import json
from pathlib import Path
from datetime import datetime

from flask import Flask, jsonify, request

app = Flask(__name__)
APP_DIR = Path(__file__).resolve().parent


def get_latest_deals():
    """Load the most recent best_deals_YYYY-MM-DD.json."""
    pattern = "best_deals_*.json"
    files = list(APP_DIR.glob(pattern))
    if not files:
        return None
    latest = max(files, key=lambda p: p.stat().st_mtime)
    with open(latest, encoding="utf-8") as f:
        return json.load(f)


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "time": datetime.utcnow().isoformat() + "Z"})


@app.route("/api/deals")
def deals():
    """
    Public (for now) best-deals data.
    TODO: Add auth – require JWT or session and check subscription before returning data.
    """
    data = get_latest_deals()
    if data is None:
        return jsonify({"error": "No deals file yet. Run compare_prices.py (e.g. via cron)."}), 503
    return jsonify({
        "disclaimer": "Prices approximate; from third-party APIs. Confirm at store.",
        "deals": data,
    })


# ---------- Placeholders for selling the app ----------

@app.route("/api/register", methods=["POST"])
def register():
    """
    TODO: User signup. Accept email + password, create user in DB, return JWT or session.
    Requires: User model (SQLite/Postgres), password hashing (e.g. bcrypt), JWT or Flask-Login.
    """
    return jsonify({"message": "Not implemented. Add user DB and auth."}), 501


@app.route("/api/login", methods=["POST"])
def login():
    """
    TODO: Login. Validate credentials, return JWT or set session.
    """
    return jsonify({"message": "Not implemented. Add auth."}), 501


@app.route("/api/create-checkout-session", methods=["POST"])
def create_checkout_session():
    """
    TODO: Stripe Checkout. Accept plan_id (e.g. monthly/yearly), create Stripe session,
    return { "url": stripe_checkout_url }. Frontend redirects user to pay.
    Requires: pip install stripe, STRIPE_SECRET_KEY in env, Stripe Product/Price IDs.
    """
    return jsonify({"message": "Not implemented. Add Stripe."}), 501


@app.route("/api/webhook", methods=["POST"])
def stripe_webhook():
    """
    TODO: Stripe webhook. On checkout.session.completed or customer.subscription.updated,
    update user's subscription in your DB. Use Stripe CLI to test locally.
    """
    return jsonify({"message": "Not implemented. Add Stripe webhook."}), 501


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
