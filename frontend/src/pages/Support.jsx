import { useState } from 'react'

export default function Support() {
  const [form, setForm] = useState({ name: '', email: '', message: '' })
  const [status, setStatus] = useState(null)

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  const submit = async (e) => {
    e.preventDefault()
    setStatus({ kind: 'pending' })
    try {
      const res = await fetch('/api/support', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`)
      setStatus({ kind: 'ok' })
      setForm({ name: '', email: '', message: '' })
    } catch (err) {
      setStatus({ kind: 'error', message: err.message })
    }
  }

  return (
    <section className="panel">
      <h1>Support</h1>
      <p>
        Need a hand tracking down an order, or have a question about a book?
        Send us a note and we'll get back to you.
      </p>
      <form className="support-form" onSubmit={submit}>
        <label>
          Name
          <input value={form.name} onChange={update('name')} required />
        </label>
        <label>
          Email
          <input
            type="email"
            value={form.email}
            onChange={update('email')}
            required
          />
        </label>
        <label>
          Message
          <textarea
            rows={5}
            value={form.message}
            onChange={update('message')}
            required
          />
        </label>
        <button type="submit" className="cta" disabled={status?.kind === 'pending'}>
          {status?.kind === 'pending' ? 'Sending…' : 'Send Message'}
        </button>
      </form>
      {status?.kind === 'ok' && (
        <p className="success">Thanks! We received your message.</p>
      )}
      {status?.kind === 'error' && (
        <p className="error">Something went wrong: {status.message}</p>
      )}
    </section>
  )
}
