import json
import os
from typing import Callable

from anthropic import Anthropic

CHAT_MODEL = "claude-sonnet-4-6"

CHAT_SYSTEM_PROMPT = """You are Bookly's friendly bookstore assistant. Bookly is a small, rustic online bookstore. Keep answers warm and concise (2-4 sentences unless the customer asks for detail). If a customer asks something unrelated to books or the store, politely steer back.

You can help with:
- Book recommendations and reading advice
- Sharing a plot summary or overview of a book (use the get_book_summary tool; summaries come from Wikipedia)
- Order status (use the get_order_status tool when an order number is provided)
- Filing return / refund requests (use the submit_return_request tool)
- Explaining shipping, returns, and password-reset policies (see below)

## Shipping
- Standard shipping is free on orders over $25; otherwise $3.99 flat rate.
- Orders ship within 1-2 business days from our warehouse.
- Standard delivery is 3-5 business days in the continental US.
- Express shipping (2 business days) is $9.99.
- We ship internationally to Canada, UK, EU, and Australia — 7-14 business days, rates calculated at checkout.
- Every shipment includes a tracking number, emailed once the order is packed.

## Returns and refunds
- Books may be returned within 30 days of delivery for a full refund.
- Books must be in unread, resellable condition.
- To start a return, ask the customer for their order number and reason, then use the submit_return_request tool.
- Refunds are issued to the original payment method within 5-7 business days once we receive the return.
- Return shipping is free for defective or wrong-item shipments; otherwise it's a flat $4 deducted from the refund.

## Password reset
- Customers can reset their password from the sign-in page by clicking "Forgot password?"
- We'll email a reset link to their account email; the link is valid for 60 minutes.
- If they don't receive the email within 5 minutes, ask them to check spam or re-send from the same page.
- We never ask for the current password in chat, email, or over the phone.

## Rules
- Never invent order details or book plot points. If a tool returns nothing, tell the customer honestly.
- When quoting a book summary, paraphrase or trim it to 2-4 sentences and mention it came from Wikipedia. Include the Wikipedia URL if provided.
- If get_book_summary returns `is_disambiguation: true`, ask the customer for the author or year to narrow it down.
- Never ask for full credit card or password details in chat.
- If something is outside these policies (billing disputes, missing package claims older than 30 days, publisher inquiries), direct the customer to the Support page.
"""

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


class ChatbotError(RuntimeError):
    """Raised when the chatbot cannot produce a reply."""


ToolHandler = Callable[[dict], str]

_client: Anthropic | None = None


def _get_client() -> Anthropic:
    global _client
    if _client is None:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise ChatbotError("ANTHROPIC_API_KEY is not set on the server.")
        _client = Anthropic()
    return _client


def _block_to_dict(block) -> dict:
    if hasattr(block, "model_dump"):
        return block.model_dump()
    return dict(block)


def run_chat(
    messages: list[dict],
    tool_handlers: dict[str, ToolHandler],
    max_iterations: int = 6,
) -> str:
    """Run the tool-use loop and return the assistant's final text reply.

    `messages` is mutated in place with any assistant / tool-result turns.
    """
    client = _get_client()

    for _ in range(max_iterations):
        response = client.messages.create(
            model=CHAT_MODEL,
            max_tokens=1024,
            system=[
                {
                    "type": "text",
                    "text": CHAT_SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            tools=CHAT_TOOLS,
            messages=messages,
        )

        if response.stop_reason != "tool_use":
            break

        messages.append({
            "role": "assistant",
            "content": [_block_to_dict(b) for b in response.content],
        })

        tool_results = []
        for block in response.content:
            if getattr(block, "type", None) != "tool_use":
                continue
            handler = tool_handlers.get(block.name)
            if handler is None:
                result = json.dumps({"error": f"unknown tool {block.name}"})
            else:
                result = handler(block.input or {})
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result,
            })
        messages.append({"role": "user", "content": tool_results})
    else:
        raise ChatbotError("chat exceeded tool-use iterations")

    return "".join(
        block.text for block in response.content
        if getattr(block, "type", None) == "text"
    ).strip()
