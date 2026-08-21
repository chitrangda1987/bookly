import json
from pathlib import Path

from flask import Blueprint, jsonify, request

from .models import Book

BOOKS_FILE = Path(__file__).resolve().parents[2] / "data" / "books.json"
with BOOKS_FILE.open() as f:
    _raw = json.load(f)
    BOOKS: list[Book] = [Book.model_validate(b) for b in _raw]

bp = Blueprint("books", __name__)


def _matches(book: Book, query: str) -> bool:
    return (
        query in book.title.lower()
        or query in book.author.lower()
        or query in book.genre.lower()
    )


@bp.get("/api/books")
def list_books():
    return jsonify([b.model_dump() for b in BOOKS])


@bp.get("/api/books/search")
def search_books():
    query = (request.args.get("q") or "").strip().lower()
    matches = BOOKS if not query else [b for b in BOOKS if _matches(b, query)]
    return jsonify([b.model_dump() for b in matches])
