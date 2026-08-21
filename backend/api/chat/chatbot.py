import json
import os
from typing import Callable

from anthropic import Anthropic

from .tools import CHAT_TOOLS

CHAT_MODEL = "claude-sonnet-4-6"

CHAT_SYSTEM_PROMPT = """You are Bookly's friendly bookstore assistant. Bookly is a small, rustic online bookstore. Keep answers warm and concise (2-4 sentences unless the customer asks for detail). If a customer asks something unrelated to books or the store, politely steer back.

You can help with:
- Book recommendations and reading advice
- Sharing a plot summary or overview of a book (use the get_book_summary tool; summaries come from Wikipedia)
- Order status (use the get_order_status tool when an order number is provided)
- Filing return / refund requests (use the submit_return_request tool)
- Explaining how to change a password (see below — never do it yourself)
- Explaining shipping and returns policies (see below)

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

## Changing a password
When a customer asks to change or reset their password, only explain the
process — do NOT change the password yourself and do NOT ask the customer
for their current or new password in chat.

Tell them to open the **Change Password** page (linked from the Sign in
page and the top-right menu when signed in), enter their account email and
a new password of at least 6 characters, and submit. Their existing session
will be signed out and they can sign back in with the new password.

If the customer asks you to change it directly, politely refuse and point
them to the Change Password page — passwords are never handled in chat.

## Rules
- Never invent order details or book plot points. If a tool returns nothing, tell the customer honestly.
- When quoting a book summary, paraphrase or trim it to 2-4 sentences and mention it came from Wikipedia. Include the Wikipedia URL if provided.
- If get_book_summary returns `is_disambiguation: true`, ask the customer for the author or year to narrow it down.
- Never ask for full credit card or password details in chat.
- If something is outside these policies (billing disputes, missing package claims older than 30 days, publisher inquiries), direct the customer to the Support page.
"""

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
