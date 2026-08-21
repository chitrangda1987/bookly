from flask import Blueprint, jsonify, request

from . import store

bp = Blueprint("auth", __name__)


def _bearer_token() -> str | None:
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        return header[len("Bearer "):].strip() or None
    return None


def _require_user():
    user = store.user_from_token(_bearer_token())
    if not user:
        return None, (jsonify({"error": "authentication required"}), 401)
    return user, None


@bp.post("/api/auth/register")
def register():
    data = request.get_json(silent=True) or {}
    user, err = store.register_user(
        data.get("name") or "",
        data.get("email") or "",
        data.get("password") or "",
    )
    if err:
        return jsonify({"error": err}), 400
    token = store.issue_token(user["email"])
    return jsonify({"token": token, "user": user}), 201


@bp.post("/api/auth/login")
def login():
    data = request.get_json(silent=True) or {}
    user, err = store.login_user(
        data.get("email") or "", data.get("password") or ""
    )
    if err:
        return jsonify({"error": err}), 401
    token = store.issue_token(user["email"])
    return jsonify({"token": token, "user": user})


@bp.post("/api/auth/logout")
def logout():
    token = _bearer_token()
    if token:
        store.revoke_token(token)
    return jsonify({"ok": True})


@bp.get("/api/auth/me")
def me():
    user, err = _require_user()
    if err:
        return err
    return jsonify({"user": {"name": user["name"], "email": user["email"]}})


@bp.post("/api/auth/change-password")
def change_password():
    data = request.get_json(silent=True) or {}
    ok, msg = store.update_password(
        data.get("email") or "",
        data.get("new_password") or "",
    )
    if not ok:
        return jsonify({"error": msg}), 400
    return jsonify({"ok": True, "message": "password updated"})
