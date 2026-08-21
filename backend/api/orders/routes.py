from pydantic import ValidationError
from flask import Blueprint, jsonify, request

from api.books import BOOKS

from .models import CheckoutRequest, OrderItem
from .store import create_order, get_order, record_return_request

bp = Blueprint("orders", __name__)


@bp.post("/api/cart/checkout")
def checkout():
    try:
        payload = CheckoutRequest.model_validate(request.get_json(silent=True) or {})
    except ValidationError as e:
        return jsonify({"error": str(e.errors()[0].get("msg") or e)}), 400

    books_by_id = {b.id: b for b in BOOKS}
    order_items: list[OrderItem] = []
    total = 0.0
    for entry in payload.items:
        book = books_by_id.get(entry.id)
        if not book:
            return jsonify({"error": f"unknown book id: {entry.id}"}), 400
        order_items.append(OrderItem(
            id=book.id, title=book.title, price=book.price, quantity=entry.quantity,
        ))
        total += book.price * entry.quantity

    order = create_order(payload.customer, order_items, total)
    return jsonify(order.model_dump()), 201


@bp.get("/api/orders/<order_number>")
def fetch_order(order_number: str):
    order = get_order(order_number)
    if not order:
        return jsonify({"error": "order not found"}), 404
    return jsonify(order.model_dump())


@bp.post("/api/orders/<order_number>/return")
def request_return(order_number: str):
    data = request.get_json(silent=True) or {}
    reason = (data.get("reason") or "").strip()
    if not reason:
        return jsonify({"error": "reason is required"}), 400
    order = record_return_request(order_number, reason)
    if not order:
        return jsonify({"error": "order not found"}), 404
    return jsonify(order.model_dump())
