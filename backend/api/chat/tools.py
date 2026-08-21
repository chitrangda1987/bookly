CHAT_TOOLS = [
    {
        "name": "get_order_status",
        "description": (
            "Look up an order by its order number. Returns order status, items, "
            "tracking, and estimated delivery. Use this whenever a customer "
            "asks about the state of a specific order."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_number": {
                    "type": "string",
                    "description": "The order number, e.g. BK-2026-DEMO01",
                }
            },
            "required": ["order_number"],
        },
    },
    {
        "name": "get_book_summary",
        "description": (
            "Fetch a short plot summary / overview of a book from Wikipedia. "
            "Use this whenever a customer asks what a book is about, wants a "
            "synopsis, or asks for an overview. Returns the Wikipedia intro "
            "extract, page URL, and a flag if the page is a disambiguation."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "The book title to look up.",
                },
                "author": {
                    "type": "string",
                    "description": "Optional author name to disambiguate.",
                },
            },
            "required": ["title"],
        },
    },
    {
        "name": "submit_return_request",
        "description": (
            "File a return / refund request for an existing order. Only call "
            "after the customer has provided both the order number and a reason."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_number": {"type": "string"},
                "reason": {
                    "type": "string",
                    "description": "The customer's stated reason for the return.",
                },
            },
            "required": ["order_number", "reason"],
        },
    },
]
