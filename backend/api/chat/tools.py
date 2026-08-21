import json

from langchain_core.tools import StructuredTool

from api.orders.store import ORDERS, record_return_request

from .models import GetBookSummaryInput, GetOrderStatusInput, SubmitReturnRequestInput
from .wikipedia import fetch_summary


def _get_order_status(order_number: str) -> str:
    num = order_number.strip().upper()
    order = ORDERS.get(num)
    if not order:
        return json.dumps({"found": False, "order_number": num})
    return json.dumps({"found": True, **order.model_dump()})


def _get_book_summary(title: str, author: str | None = None) -> str:
    return json.dumps(fetch_summary((title or "").strip(), (author or None) and author.strip()))


def _submit_return_request(order_number: str, reason: str) -> str:
    num = order_number.strip().upper()
    reason = reason.strip()
    if not reason:
        return json.dumps({"ok": False, "error": "reason is required"})
    order = record_return_request(num, reason)
    if not order:
        return json.dumps({"ok": False, "error": "order not found"})
    return json.dumps({
        "ok": True,
        "order_number": num,
        "return_request": order.return_request.model_dump() if order.return_request else None,
    })


CHAT_TOOLS = [
    StructuredTool.from_function(
        func=_get_order_status,
        name="get_order_status",
        description=(
            "Look up an order by its order number. Returns order status, items, "
            "tracking, and estimated delivery. Use this whenever a customer "
            "asks about the state of a specific order."
        ),
        args_schema=GetOrderStatusInput,
    ),
    StructuredTool.from_function(
        func=_get_book_summary,
        name="get_book_summary",
        description=(
            "Fetch a short plot summary / overview of a book from Wikipedia. "
            "Use this whenever a customer asks what a book is about, wants a "
            "synopsis, or asks for an overview. Returns the Wikipedia intro "
            "extract, page URL, and a flag if the page is a disambiguation."
        ),
        args_schema=GetBookSummaryInput,
    ),
    StructuredTool.from_function(
        func=_submit_return_request,
        name="submit_return_request",
        description=(
            "File a return / refund request for an existing order. Only call "
            "after the customer has provided both the order number and a reason."
        ),
        args_schema=SubmitReturnRequestInput,
    ),
]
