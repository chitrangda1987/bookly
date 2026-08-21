from anthropic import APIError
from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from .chatbot import CHAT_MODEL, ChatbotError, run_chat
from .models import ChatMessage

bp = Blueprint("chat", __name__)


@bp.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    raw = data.get("messages")
    if not isinstance(raw, list) or not raw:
        return jsonify({"error": "messages must be a non-empty list"}), 400

    cleaned: list[ChatMessage] = []
    for entry in raw:
        try:
            msg = ChatMessage.model_validate(entry)
        except ValidationError:
            continue
        if msg.content.strip():
            cleaned.append(msg)

    if not cleaned or cleaned[-1].role != "user":
        return jsonify({"error": "last message must be from the user"}), 400

    try:
        reply = run_chat(cleaned)
    except ChatbotError as e:
        return jsonify({"error": str(e)}), 503
    except APIError as e:
        return jsonify({"error": f"Anthropic API error: {e}"}), 502

    return jsonify({"reply": reply, "model": CHAT_MODEL})
