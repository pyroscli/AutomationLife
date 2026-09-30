import { useEffect, useState, type FormEvent } from 'react'
import { getDay, saveDay, todayISO, type User } from './api'

interface Fields {
  calories: string
  steps: string
  pages: string
  book: string
  med_morning: boolean
  med_night: boolean
  notes: string
}

const EMPTY: Fields = {
  calories: '',
  steps: '',
  pages: '',
  book: '',
  med_morning: false,
  med_night: false,
  notes: '',
}

type Status = 'loading' | 'idle' | 'saving' | 'saved' | 'error'

function numOrNull(s: string): number | null {
  const t = s.trim()
  if (t === '') return null
  const n = Number(t)
  return Number.isFinite(n) ? n : null
}

export default function DayForm({ user, onLogout }: { user: User; onLogout: () => void }) {
  const [date, setDate] = useState(todayISO())
  const [fields, setFields] = useState<Fields>(EMPTY)
  const [status, setStatus] = useState<Status>('loading')

  useEffect(() => {
    let active = true
    setStatus('loading')
    getDay(date)
      .then((d) => {
        if (!active) return
        setFields({
          calories: d.calories?.toString() ?? '',
          steps: d.steps?.toString() ?? '',
          pages: d.pages?.toString() ?? '',
          book: d.book ?? '',
          med_morning: d.med_morning,
          med_night: d.med_night,
          notes: d.notes ?? '',
        })
        setStatus('idle')
      })
      .catch(() => active && setStatus('error'))
    return () => {
      active = false
    }
  }, [date])

  function set<K extends keyof Fields>(key: K, value: Fields[K]) {
    setFields((f) => ({ ...f, [key]: value }))
    setStatus('idle')
  }

  async function handleSave(e: FormEvent) {
    e.preventDefault()
    setStatus('saving')
    try {
      await saveDay(date, {
        calories: numOrNull(fields.calories),
        steps: numOrNull(fields.steps),
        pages: numOrNull(fields.pages),
        book: fields.book.trim(),
        med_morning: fields.med_morning,
        med_night: fields.med_night,
        notes: fields.notes.trim(),
      })
      setStatus('saved')
    } catch {
      setStatus('error')
    }
  }

  const isToday = date === todayISO()

  return (
    <main className="card">
      <div className="userbar">
        {user.picture && <img className="avatar" src={user.picture} alt="" />}
        <div style={{ flex: 1 }}>
          <strong>{user.name || user.email}</strong>
          <div className="muted small">{user.email}</div>
        </div>
        <button className="link" onClick={onLogout}>
          Sign out
        </button>
      </div>

      <div className="daterow">
        <h1>{isToday ? 'Today' : 'Edit day'}</h1>
        <input
          type="date"
          value={date}
          max={todayISO()}
          onChange={(e) => setDate(e.target.value)}
        />
      </div>

      {status === 'loading' ? (
        <p className="muted">Loading…</p>
      ) : (
        <form onSubmit={handleSave}>
          <label className="field">
            <span>🔥 Calories</span>
            <input
              type="number"
              inputMode="numeric"
              value={fields.calories}
              onChange={(e) => set('calories', e.target.value)}
              placeholder="2100"
            />
          </label>
          <label className="field">
            <span>👟 Steps</span>
            <input
              type="number"
              inputMode="numeric"
              value={fields.steps}
              onChange={(e) => set('steps', e.target.value)}
              placeholder="8200"
            />
          </label>
          <label className="field">
            <span>📖 Pages</span>
            <input
              type="number"
              inputMode="decimal"
              value={fields.pages}
              onChange={(e) => set('pages', e.target.value)}
              placeholder="14"
            />
          </label>
          <label className="field">
            <span>📚 Book</span>
            <input
              type="text"
              value={fields.book}
              onChange={(e) => set('book', e.target.value)}
              placeholder="Bird by Bird"
            />
          </label>

          <div className="meds">
            <button
              type="button"
              className={'toggle' + (fields.med_morning ? ' on' : '')}
              onClick={() => set('med_morning', !fields.med_morning)}
            >
              💊 Morning med
            </button>
            <button
              type="button"
              className={'toggle' + (fields.med_night ? ' on' : '')}
              onClick={() => set('med_night', !fields.med_night)}
            >
              💊 Night med
            </button>
          </div>

          <label className="field">
            <span>📝 Note</span>
            <textarea
              value={fields.notes}
              onChange={(e) => set('notes', e.target.value)}
              rows={2}
              placeholder="optional"
            />
          </label>

          <button className="btn google" type="submit" disabled={status === 'saving'}>
            {status === 'saving' ? 'Saving…' : status === 'saved' ? 'Saved ✓' : 'Save'}
          </button>
          {status === 'error' && (
            <p className="notice">Couldn’t save. Is the backend running? Try again.</p>
          )}
        </form>
      )}
    </main>
  )
}
