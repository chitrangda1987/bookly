from flask import Blueprint, jsonify, request

from api.books import BOOKS

from .store import create_order, get_order, record_return_request

bp = Blueprint("orders", __name__)


@bp.post("/api/cart/checkout")
def checkout():
    data = request.get_json(silent=True) or {}
    customer = data.get("customer") or {}
    items_in = data.get("items") or []
    name = (customer.get("name") or "").strip()
    email = (customer.get("email") or "").strip()

    if not name or not email:
        return jsonify({"error": "customer name and email are required"}), 400
    if not isinstance(items_in, list) or not items_in:
        return jsonify({"error": "cart is empty"}), 400

    books_by_id = {b["id"]: b for b in BOOKS}
    order_items = []
    total = 0.0
    for entry in items_in:
        book_id = entry.get("id")
        qty = int(entry.get("quantity") or 1)
        if book_id not in books_by_id or qty <= 0:
            return jsonify({"error": f"invalid cart entry: {entry}"}), 400
        book = books_by_id[book_id]
        order_items.append({
            "id": book_id,
            "title": book["title"],
            "price": book["price"],
            "quantity": qty,
        })
        total += book["price"] * qty

    order = create_order({"name": name, "email": email}, order_items, total)
    return jsonify(order), 201


@bp.get("/api/orders/<order_number>")
def fetch_order(order_number: str):
    order = get_order(order_number)
    if not order:
        return jsonify({"error": "order not found"}), 404
    return jsonify(order)


@bp.post("/api/orders/<order_number>/return")
def request_return(order_number: str):
    data = request.get_json(silent=True) or {}
    reason = (data.get("reason") or "").strip()
    if not reason:
        return jsonify({"error": "reason is required"}), 400
    order = record_return_request(order_number, reason)
    if not order:
        return jsonify({"error": "order not found"}), 404
    return jsonify(order)
