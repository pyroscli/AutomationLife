// Thin typed wrapper around the FastAPI backend. All calls go through the Vite
// proxy (same-origin), so the session cookie is sent automatically.

export interface User {
  id: number
  email: string
  name: string
  picture: string
}

export type MeResponse =
  | { authenticated: true; user: User }
  | { authenticated: false; google_configured: boolean }

export async function fetchMe(): Promise<MeResponse> {
  const res = await fetch('/api/me', { credentials: 'include' })
  if (!res.ok) throw new Error(`GET /api/me failed: ${res.status}`)
  return res.json()
}

export async function logout(): Promise<void> {
  await fetch('/api/logout', { method: 'POST', credentials: 'include' })
}

// Full-page navigation (not fetch) so the browser follows the Google redirect.
export function goToLogin(): void {
  window.location.href = '/login'
}

// ---- Daily log ---------------------------------------------------------------

export interface DayLog {
  date: string
  saved: boolean
  calories: number | null
  steps: number | null
  pages: number | null
  book: string
  med_morning: boolean
  med_night: boolean
  notes: string
  updated_at: string | null
}

export interface DayLogInput {
  calories: number | null
  steps: number | null
  pages: number | null
  book: string
  med_morning: boolean
  med_night: boolean
  notes: string
}

export async function getDay(date: string): Promise<DayLog> {
  const res = await fetch(`/api/day/${date}`, { credentials: 'include' })
  if (!res.ok) throw new Error(`GET /api/day failed: ${res.status}`)
  return res.json()
}

export async function saveDay(date: string, data: DayLogInput): Promise<DayLog> {
  const res = await fetch(`/api/day/${date}`, {
    method: 'PUT',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error(`PUT /api/day failed: ${res.status}`)
  return res.json()
}

// Local calendar date (YYYY-MM-DD) so "today" tracks the user's wall clock,
// not UTC.
export function todayISO(): string {
  const d = new Date()
  return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10)
}
