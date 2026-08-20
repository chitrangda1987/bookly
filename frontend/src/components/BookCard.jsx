import { useState } from 'react'
import { useCart } from '../context/CartContext.jsx'

export default function BookCard({ book }) {
  const { addItem } = useCart()
  const [added, setAdded] = useState(false)

  const handleAdd = () => {
    addItem(book)
    setAdded(true)
    setTimeout(() => setAdded(false), 1200)
  }

  return (
    <article className="book-card">
      {book.cover && (
        <img
          className="book-cover"
          src={book.cover}
          alt={`Cover of ${book.title}`}
          loading="lazy"
        />
      )}
      <h3 className="book-title">{book.title}</h3>
      <p className="book-author">by {book.author}</p>
      <div className="book-meta">
        <span className="book-genre">{book.genre}</span>
        <span className="book-price">${book.price.toFixed(2)}</span>
      </div>
      <button
        type="button"
        className={'add-to-cart' + (added ? ' add-to-cart--added' : '')}
        onClick={handleAdd}
      >
        {added ? 'Added ✓' : 'Add to Cart'}
      </button>
    </article>
  )
}
