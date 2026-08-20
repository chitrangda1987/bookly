import json
import random
import string
from datetime import datetime, timedelta, timezone
from pathlib import Path

DEMO_ORDERS_FILE = Path(__file__).parent / "demo_orders.json"

ORDERS: dict[str, dict] = {}


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def new_order_number() -> str:
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"BK-{now_utc().year}-{suffix}"


def get_order(number: str) -> dict | None:
    return ORDERS.get(number.strip().upper())


def record_return_request(number: str, reason: str) -> dict | None:
    order = get_order(number)
    if not order:
        return None
    order["return_request"] = {
        "reason": reason,
        "status": "pending",
        "requested_at": now_utc().isoformat(),
    }
    return order


def create_order(customer: dict, order_items: list[dict], total: float) -> dict:
    now = now_utc()
    order_number = new_order_number()
    order = {
        "order_number": order_number,
        "customer": customer,
        "items": order_items,
        "total": round(total, 2),
        "status": "processing",
        "placed_at": now.isoformat(),
        "shipped_at": None,
        "tracking_number": None,
        "estimated_delivery": (now + timedelta(days=5)).date().isoformat(),
        "return_request": None,
    }
    ORDERS[order_number] = order
    return order


def _hydrate_demo_order(template: dict, books_by_id: dict[int, dict], now: datetime) -> dict | None:
    items = []
    total = 0.0
    for entry in template.get("items", []):
        book = books_by_id.get(entry["id"])
        if not book:
            return None
        qty = entry["quantity"]
        items.append({
            "id": book["id"],
            "title": book["title"],
            "price": book["price"],
            "quantity": qty,
        })
        total += book["price"] * qty

    shipped_hours = template.get("shipped_hours_ago")
    return {
        "order_number": template["order_number"],
        "customer": template["customer"],
        "items": items,
        "total": round(total, 2),
        "status": template["status"],
        "placed_at": (now - timedelta(hours=template["placed_hours_ago"])).isoformat(),
        "shipped_at": (
            (now - timedelta(hours=shipped_hours)).isoformat()
            if shipped_hours is not None else None
        ),
        "tracking_number": template.get("tracking_number"),
        "estimated_delivery": (
            now + timedelta(days=template["estimated_delivery_days_from_now"])
        ).date().isoformat(),
        "return_request": None,
    }


def seed_demo_orders(books: list[dict]) -> None:
    """Populate demo orders (from demo_orders.json) so the chatbot has data to look up."""
    if not books:
        return
    with DEMO_ORDERS_FILE.open() as f:
        templates = json.load(f)

    now = now_utc()
    books_by_id = {b["id"]: b for b in books}
    for template in templates:
        order = _hydrate_demo_order(template, books_by_id, now)
        if order:
            ORDERS[order["order_number"]] = order
