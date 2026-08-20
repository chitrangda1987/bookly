import json

from anthropic import APIError
from flask import Blueprint, jsonify, request

from api.orders.store import ORDERS, record_return_request

from .chatbot import CHAT_MODEL, ChatbotError, run_chat
from .wikipedia import fetch_summary

bp = Blueprint("chat", __name__)


def _tool_get_order_status(tool_input: dict) -> str:
    num = (tool_input.get("order_number") or "").strip().upper()
    order = ORDERS.get(num)
    if not order:
        return json.dumps({"found": False, "order_number": num})
    return json.dumps({"found": True, **order})


def _tool_get_book_summary(tool_input: dict) -> str:
    title = (tool_input.get("title") or "").strip()
    author = (tool_input.get("author") or "").strip() or None
    return json.dumps(fetch_summary(title, author))


def _tool_submit_return_request(tool_input: dict) -> str:
    num = (tool_input.get("order_number") or "").strip().upper()
    reason = (tool_input.get("reason") or "").strip()
    if not reason:
        return json.dumps({"ok": False, "error": "reason is required"})
    order = record_return_request(num, reason)
    if not order:
        return json.dumps({"ok": False, "error": "order not found"})
    return json.dumps({
        "ok": True,
        "order_number": num,
        "return_request": order["return_request"],
    })


TOOL_HANDLERS = {
    "get_order_status": _tool_get_order_status,
    "get_book_summary": _tool_get_book_summary,
    "submit_return_request": _tool_submit_return_request,
}


@bp.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    messages = data.get("messages")
    if not isinstance(messages, list) or not messages:
        return jsonify({"error": "messages must be a non-empty list"}), 400

    cleaned = []
    for m in messages:
        role = m.get("role")
        content = (m.get("content") or "").strip()
        if role not in ("user", "assistant") or not content:
            continue
        cleaned.append({"role": role, "content": content})
    if not cleaned or cleaned[-1]["role"] != "user":
        return jsonify({"error": "last message must be from the user"}), 400

    try:
        reply = run_chat(cleaned, TOOL_HANDLERS)
    except ChatbotError as e:
        return jsonify({"error": str(e)}), 503
    except APIError as e:
        return jsonify({"error": f"Anthropic API error: {e}"}), 502

    return jsonify({"reply": reply, "model": CHAT_MODEL})
