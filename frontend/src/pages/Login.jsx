import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

export default function Login() {
  const { login, register, isAuthenticated } = useAuth()
  const [mode, setMode] = useState('signin')
  const [form, setForm] = useState({ name: '', email: '', password: '' })
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)
  const navigate = useNavigate()

  if (isAuthenticated) return <Navigate to="/account" replace />

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  const submit = async (e) => {
    e.preventDefault()
    setBusy(true)
    setError(null)
    try {
      if (mode === 'signin') {
        await login(form.email, form.password)
      } else {
        await register(form.name, form.email, form.password)
      }
      navigate('/account')
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="panel auth-panel">
      <div className="auth-tabs">
        <button
          type="button"
          className={'auth-tab' + (mode === 'signin' ? ' auth-tab--active' : '')}
          onClick={() => setMode('signin')}
        >
          Sign in
        </button>
        <button
          type="button"
          className={'auth-tab' + (mode === 'signup' ? ' auth-tab--active' : '')}
          onClick={() => setMode('signup')}
        >
          Create account
        </button>
      </div>
      <form className="support-form" onSubmit={submit}>
        {mode === 'signup' && (
          <label>
            Name
            <input value={form.name} onChange={update('name')} required />
          </label>
        )}
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
          Password
          <input
            type="password"
            value={form.password}
            onChange={update('password')}
            required
            minLength={6}
          />
        </label>
        <button type="submit" className="cta" disabled={busy}>
          {busy ? 'Working…' : mode === 'signin' ? 'Sign in' : 'Create account'}
        </button>
        {error && <p className="error">{error}</p>}
      </form>
      <p className="hint">
        Forgot your password? <Link to="/change-password">Change it here</Link>.
      </p>
    </section>
  )
}
