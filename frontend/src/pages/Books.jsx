import { useEffect, useState } from 'react'
import BookCard from '../components/BookCard.jsx'

export default function Books() {
  const [books, setBooks] = useState([])
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/books')
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.json()
      })
      .then(setBooks)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <section className="panel">
      <h1>Our Shelves</h1>
      {loading && <p>Loading books…</p>}
      {error && (
        <p className="error">
          Couldn't reach the shop ({error}). Is the Python backend running on
          port 5000?
        </p>
      )}
      <div className="book-grid">
        {books.map((b) => (
          <BookCard key={b.id} book={b} />
        ))}
      </div>
    </section>
  )
}
