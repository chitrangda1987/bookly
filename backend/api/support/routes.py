from flask import Blueprint, jsonify, request

bp = Blueprint("support", __name__)


@bp.post("/api/support")
def submit_support():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    message = (data.get("message") or "").strip()
    if not (name and email and message):
        return jsonify({"error": "name, email, and message are required"}), 400
    return jsonify({"ok": True, "received": {"name": name, "email": email}})
