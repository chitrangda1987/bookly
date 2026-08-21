import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

export default function ChangePassword() {
  const { user, changePassword } = useAuth()
  const [form, setForm] = useState({
    email: user?.email || '',
    newPassword: '',
  })
  const [status, setStatus] = useState(null)

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  const submit = async (e) => {
    e.preventDefault()
    setStatus({ kind: 'pending' })
    try {
      await changePassword(form.email, form.newPassword)
      setStatus({ kind: 'ok' })
      setForm({ email: form.email, newPassword: '' })
    } catch (err) {
      setStatus({ kind: 'error', message: err.message })
    }
  }

  return (
    <section className="panel">
      <h1>Change Password</h1>
      <p>Enter your account email and a new password (at least 6 characters).</p>
      <form className="support-form" onSubmit={submit}>
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
          New password
          <input
            type="password"
            value={form.newPassword}
            onChange={update('newPassword')}
            required
            minLength={6}
          />
        </label>
        <button
          type="submit"
          className="cta"
          disabled={status?.kind === 'pending'}
        >
          {status?.kind === 'pending' ? 'Updating…' : 'Update password'}
        </button>
        {status?.kind === 'ok' && (
          <p className="success">
            Password updated. <Link to="/login">Sign in</Link> with the new one.
          </p>
        )}
        {status?.kind === 'error' && (
          <p className="error">{status.message}</p>
        )}
      </form>
    </section>
  )
}
