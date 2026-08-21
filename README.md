# Bookly

A rustic online bookstore — Python (Flask) API + React (Vite) frontend, with
a Claude Sonnet-powered support chatbot.

## Features

- **Catalog** — browse or search a small book catalog seeded from
  `backend/data/books.json`.
- **Cart & checkout** — add books to a cart, place an order, and get an
  order number back (`BK-YYYY-XXXXXX`). Orders live in an in-memory store.
- **Accounts** — register, sign in, sign out, and change your password from
  the Change Password page. Passwords are hashed with `werkzeug.security`;
  sessions are bearer tokens kept in memory.
- **Chatbot** — a floating 💬 widget bottom-right that talks to Claude
  Sonnet 4.6 via Anthropic's tool-use API. It can:
  - Recommend books and answer store questions
  - Look up order status (`get_order_status`)
  - File return / refund requests (`submit_return_request`)
  - Fetch a book's summary from Wikipedia (`get_book_summary`)
  - Explain shipping, returns, and password-change policies (from the
    system prompt — it never handles passwords itself)

## Requirements

- **Python 3.10+** (developed on 3.13; `type X | None` syntax means 3.9
  and older will not work)
- **Node 18+** (Vite 5 requires it)
- **Anthropic API key** in `backend/.env` as `ANTHROPIC_API_KEY`

## Environment variables

The backend reads its config from `backend/.env`. A template lives at
`backend/.env.example`:

```
ANTHROPIC_API_KEY=sk-ant-...
```

Set-up:

1. `cd backend`
2. `cp .env.example .env`
3. Open `backend/.env` in an editor and replace `sk-ant-...` with a real
   Anthropic API key. Get one at
   [console.anthropic.com](https://console.anthropic.com/) → *API Keys*.
4. Save. `python-dotenv` loads the file automatically when `app.py` starts.

`backend/.env` is gitignored, so your key never leaves your machine.
`backend/.env.example` is committed and safe to check in.

Without a key the app still boots, but any call to `POST /api/chat` returns
`503 ANTHROPIC_API_KEY is not set on the server.`

## Run

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# create .env first — see the Environment variables section above
python app.py           # serves http://localhost:5000
```

### Frontend

```bash
cd frontend
npm install
npm run dev             # serves http://localhost:5173
```

Vite proxies `/api/*` to the Flask server, so both must be running.

Demo login: `ada@example.com` / `bookly123`.
Demo orders the chatbot can look up: `BK-2026-DEMO01`, `BK-2026-DEMO02`.
