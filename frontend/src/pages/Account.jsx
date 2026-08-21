import { Link, Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

export default function Account() {
  const { user, logout, isAuthenticated } = useAuth()

  if (!isAuthenticated) return <Navigate to="/login" replace />

  return (
    <section className="panel">
      <h1>Your Account</h1>
      <div className="order-summary">
        <div>
          <span className="label">Name</span>
          <span>{user.name}</span>
        </div>
        <div>
          <span className="label">Email</span>
          <span>{user.email}</span>
        </div>
      </div>
      <div className="hero-actions">
        <Link className="cta" to="/change-password">Change password</Link>
        <button type="button" className="cta cta--ghost" onClick={logout}>
          Sign out
        </button>
      </div>
    </section>
  )
}
