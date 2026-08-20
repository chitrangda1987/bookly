# Bookly

A rustic little bookstore — Python (Flask) API + React (Vite) frontend.

## Run

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python app.py            # serves http://localhost:5000
```

### Frontend

```bash
cd frontend
npm install
npm run dev              # serves http://localhost:5173
```

Vite proxies `/api/*` to the Flask server, so both must be running.

## Layout

```
backend/            Flask API (books, search, support)
frontend/           React SPA (Vite)
  public/images/    rustic_bookstore_background.svg (page background)
  src/components/   Navbar, BookCard
  src/pages/        Home, Search, Books, Support
images/             Original source images
```
