import { useEffect, useState } from 'react'
import { fetchMe, goToLogin, logout, type MeResponse } from './api'
import DayForm from './DayForm'
import './App.css'

export default function App() {
  const [me, setMe] = useState<MeResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function refresh() {
    try {
      setMe(await fetchMe())
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to reach the server')
    }
  }

  useEffect(() => {
    refresh()
  }, [])

  async function handleLogout() {
    await logout()
    refresh()
  }

  if (error) {
    return (
      <main className="card">
        <h1>Daily</h1>
        <p className="notice">
          Can’t reach the API. Is the backend running on <code>:8000</code>?
          <br />
          <span className="muted small">{error}</span>
        </p>
      </main>
    )
  }

  if (!me) {
    return (
      <main className="card">
        <p className="muted">Loading…</p>
      </main>
    )
  }

  if (me.authenticated) {
    return <DayForm user={me.user} onLogout={handleLogout} />
  }

  return (
    <main className="card">
      <h1>Daily</h1>
      <p className="muted">Log calories, steps, pages and meds in one tap.</p>
      {me.google_configured ? (
        <button className="btn google" onClick={goToLogin}>
          Continue with Google
        </button>
      ) : (
        <p className="notice">
          Google login isn’t configured yet. Add <code>GOOGLE_CLIENT_ID</code> and{' '}
          <code>GOOGLE_CLIENT_SECRET</code> to <code>webapp/.env</code>, then restart the backend.
        </p>
      )}
    </main>
  )
}
