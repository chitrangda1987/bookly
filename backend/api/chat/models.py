from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class GetOrderStatusInput(BaseModel):
    order_number: str = Field(description="The order number, e.g. BK-2026-DEMO01.")


class GetBookSummaryInput(BaseModel):
    title: str = Field(description="The book title to look up.")
    author: str | None = Field(
        default=None, description="Optional author name to disambiguate."
    )


class SubmitReturnRequestInput(BaseModel):
    order_number: str
    reason: str = Field(description="The customer's stated reason for the return.")
