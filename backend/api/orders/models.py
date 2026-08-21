from typing import Literal

from pydantic import BaseModel, EmailStr, Field


OrderStatus = Literal["processing", "shipped", "delivered", "cancelled"]
ReturnStatus = Literal["pending", "approved", "rejected", "refunded"]


class Customer(BaseModel):
    name: str
    email: str  # keeping loose validation; EmailStr requires email-validator


class OrderItem(BaseModel):
    id: int
    title: str
    price: float = Field(ge=0)
    quantity: int = Field(ge=1)


class ReturnRequest(BaseModel):
    reason: str
    status: ReturnStatus = "pending"
    requested_at: str


class Order(BaseModel):
    order_number: str
    customer: Customer
    items: list[OrderItem]
    total: float = Field(ge=0)
    status: OrderStatus = "processing"
    placed_at: str
    shipped_at: str | None = None
    tracking_number: str | None = None
    estimated_delivery: str
    return_request: ReturnRequest | None = None


class CartItemInput(BaseModel):
    id: int
    quantity: int = Field(ge=1, default=1)


class CheckoutRequest(BaseModel):
    customer: Customer
    items: list[CartItemInput] = Field(min_length=1)
