import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useCart } from '../context/CartContext.jsx'

export default function Cart() {
  const { items, setQuantity, removeItem, clear, total } = useCart()
  const [form, setForm] = useState({ name: '', email: '' })
  const [order, setOrder] = useState(null)
  const [status, setStatus] = useState(null)

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  const checkout = async (e) => {
    e.preventDefault()
    setStatus({ kind: 'pending' })
    try {
      const res = await fetch('/api/cart/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          customer: form,
          items: items.map(({ id, quantity }) => ({ id, quantity })),
        }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`)
      setOrder(data)
      clear()
      setStatus({ kind: 'ok' })
    } catch (err) {
      setStatus({ kind: 'error', message: err.message })
    }
  }

  if (order) {
    return (
      <section className="panel">
        <h1>Order Confirmed</h1>
        <p>
          Thanks for your order, <strong>{order.customer.name}</strong>! A
          confirmation has been sent to {order.customer.email}.
        </p>
        <div className="order-summary">
          <div>
            <span className="label">Order number</span>
            <span className="order-number">{order.order_number}</span>
          </div>
          <div>
            <span className="label">Status</span>
            <span className="pill">{order.status}</span>
          </div>
          <div>
            <span className="label">Estimated delivery</span>
            <span>{order.estimated_delivery}</span>
          </div>
          <div>
            <span className="label">Total</span>
            <span>${order.total.toFixed(2)}</span>
          </div>
        </div>
        <p className="hint">
          Need to check on this order later? Open the chatbot and share your
          order number — it can also help with returns and refunds.
        </p>
        <Link className="cta" to="/books">Keep browsing</Link>
      </section>
    )
  }

  if (items.length === 0) {
    return (
      <section className="panel">
        <h1>Your Cart</h1>
        <p>Your cart is empty. <Link to="/books">Browse the shelves</Link> to find your next read.</p>
      </section>
    )
  }

  return (
    <section className="panel">
      <h1>Your Cart</h1>
      <ul className="cart-list">
        {items.map((item) => (
          <li key={item.id} className="cart-row">
            {item.cover && (
              <img className="cart-thumb" src={item.cover} alt="" />
            )}
            <div className="cart-info">
              <div className="cart-title">{item.title}</div>
              <div className="cart-price">${item.price.toFixed(2)}</div>
            </div>
            <input
              type="number"
              min="1"
              className="cart-qty"
              value={item.quantity}
              onChange={(e) => setQuantity(item.id, Number(e.target.value))}
            />
            <button
              type="button"
              className="link-btn"
              onClick={() => removeItem(item.id)}
            >
              Remove
            </button>
          </li>
        ))}
      </ul>
      <div className="cart-total">
        Total: <strong>${total.toFixed(2)}</strong>
      </div>
      <form className="support-form" onSubmit={checkout}>
        <h2>Checkout</h2>
        <label>
          Name
          <input value={form.name} onChange={update('name')} required />
        </label>
        <label>
          Email
          <input type="email" value={form.email} onChange={update('email')} required />
        </label>
        <button
          type="submit"
          className="cta"
          disabled={status?.kind === 'pending'}
        >
          {status?.kind === 'pending' ? 'Placing order…' : `Place order — $${total.toFixed(2)}`}
        </button>
        {status?.kind === 'error' && (
          <p className="error">Something went wrong: {status.message}</p>
        )}
      </form>
    </section>
  )
}
