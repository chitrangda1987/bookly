from pydantic import BaseModel, Field


class Book(BaseModel):
    id: int
    title: str
    author: str
    genre: str
    price: float = Field(ge=0)
    cover: str | None = None
