import { useEffect, useState } from 'react'
import BookCard from '../components/BookCard.jsx'

export default function Search() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const controller = new AbortController()
    setLoading(true)
    const url = query
      ? `/api/books/search?q=${encodeURIComponent(query)}`
      : '/api/books'
    fetch(url, { signal: controller.signal })
      .then((r) => r.json())
      .then(setResults)
      .catch(() => {})
      .finally(() => setLoading(false))
    return () => controller.abort()
  }, [query])

  return (
    <section className="panel">
      <h1>Search</h1>
      <input
        className="search-input"
        type="search"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search by title, author, or genre…"
        autoFocus
      />
      {loading && <p>Searching…</p>}
      <div className="book-grid">
        {results.map((b) => (
          <BookCard key={b.id} book={b} />
        ))}
      </div>
      {!loading && results.length === 0 && (
        <p>No books matched your search.</p>
      )}
    </section>
  )
}
