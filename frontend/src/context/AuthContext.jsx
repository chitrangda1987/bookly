import { createContext, useContext, useEffect, useMemo, useState } from 'react'

const AuthContext = createContext(null)
const STORAGE_KEY = 'bookly.auth'

function readStored() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export function AuthProvider({ children }) {
  const [auth, setAuth] = useState(() => readStored())

  useEffect(() => {
    if (auth) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(auth))
    } else {
      localStorage.removeItem(STORAGE_KEY)
    }
  }, [auth])

  const value = useMemo(() => {
    const request = async (path, body) => {
      const res = await fetch(path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`)
      return data
    }

    const login = async (email, password) => {
      const data = await request('/api/auth/login', { email, password })
      setAuth({ token: data.token, user: data.user })
      return data.user
    }

    const register = async (name, email, password) => {
      const data = await request('/api/auth/register', { name, email, password })
      setAuth({ token: data.token, user: data.user })
      return data.user
    }

    const logout = async () => {
      try {
        if (auth?.token) {
          await fetch('/api/auth/logout', {
            method: 'POST',
            headers: { Authorization: `Bearer ${auth.token}` },
          })
        }
      } finally {
        setAuth(null)
      }
    }

    const changePassword = async (email, newPassword) => {
      await request('/api/auth/change-password', {
        email,
        new_password: newPassword,
      })
      // If the currently signed-in user just changed their password, sign
      // them out — the server invalidates their token.
      if (auth?.user?.email?.toLowerCase() === email.toLowerCase()) {
        setAuth(null)
      }
    }

    return {
      user: auth?.user || null,
      token: auth?.token || null,
      isAuthenticated: Boolean(auth?.token),
      login,
      register,
      logout,
      changePassword,
    }
  }, [auth])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
