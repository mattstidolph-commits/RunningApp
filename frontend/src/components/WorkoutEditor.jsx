import { useState } from 'react'
import { updateWorkout } from '../api'

const TYPES = ['easy_run','long_run','tempo','intervals','cross_train','rest']

export default function WorkoutEditor({ workout, onSaved }) {
  const [editing, setEditing] = useState(false)
  const [form, setForm] = useState({
    workout_type: workout.workout_type,
    target_distance_km: workout.target_distance_km || '',
    notes: workout.notes || '',
  })
  const [saving, setSaving] = useState(false)

  const save = async () => {
    setSaving(true)
    try {
      const updated = await updateWorkout(workout.id, {
        workout_type: form.workout_type,
        target_distance_km: form.target_distance_km ? Number(form.target_distance_km) : null,
        notes: form.notes || null,
      })
      onSaved(updated)
      setEditing(false)
    } finally {
      setSaving(false)
    }
  }

  if (!editing) return (
    <button onClick={() => setEditing(true)} className="text-xs text-blue-500 hover:underline">edit</button>
  )

  return (
    <div className="flex flex-col gap-2 mt-1">
      <select value={form.workout_type} onChange={e => setForm(f => ({...f, workout_type: e.target.value}))}
        className="text-xs border rounded px-1 py-0.5">
        {TYPES.map(t => <option key={t} value={t}>{t}</option>)}
      </select>
      <input type="number" placeholder="km" value={form.target_distance_km}
        onChange={e => setForm(f => ({...f, target_distance_km: e.target.value}))}
        className="text-xs border rounded px-1 py-0.5 w-20" />
      <input type="text" placeholder="notes" value={form.notes}
        onChange={e => setForm(f => ({...f, notes: e.target.value}))}
        className="text-xs border rounded px-1 py-0.5" />
      <div className="flex gap-2">
        <button onClick={save} disabled={saving}
          className="text-xs bg-blue-600 text-white px-2 py-0.5 rounded disabled:opacity-50">
          {saving ? '...' : 'Save'}
        </button>
        <button onClick={() => setEditing(false)} className="text-xs text-gray-400 hover:text-gray-600">Cancel</button>
      </div>
    </div>
  )
}
