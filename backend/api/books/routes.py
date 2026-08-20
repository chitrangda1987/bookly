import json
from pathlib import Path

from flask import Blueprint, jsonify, request

BOOKS_FILE = Path(__file__).resolve().parents[2] / "books.json"
with BOOKS_FILE.open() as f:
    BOOKS = json.load(f)

bp = Blueprint("books", __name__)


@bp.get("/api/books")
def list_books():
    return jsonify(BOOKS)


@bp.get("/api/books/search")
def search_books():
    query = (request.args.get("q") or "").strip().lower()
    if not query:
        return jsonify(BOOKS)
    matches = [
        b for b in BOOKS
        if query in b["title"].lower()
        or query in b["author"].lower()
        or query in b["genre"].lower()
    ]
    return jsonify(matches)
