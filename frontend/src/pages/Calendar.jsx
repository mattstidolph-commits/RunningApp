import { useEffect, useState } from 'react'
import FullCalendar from '@fullcalendar/react'
import dayGridPlugin from '@fullcalendar/daygrid'
import interactionPlugin from '@fullcalendar/interaction'
import { getWorkouts, updateWorkout } from '../api'

const TYPE_COLORS = {
  easy_run: '#3b82f6', long_run: '#8b5cf6', tempo: '#f97316',
  intervals: '#ef4444', cross_train: '#10b981', rest: '#d1d5db',
}

const TYPE_LABELS = {
  easy_run: 'Easy', long_run: 'Long Run', tempo: 'Tempo',
  intervals: 'Intervals', cross_train: 'Cross', rest: 'Rest',
}

export default function Calendar() {
  const [workouts, setWorkouts] = useState([])
  const [selected, setSelected] = useState(null)

  useEffect(() => {
    getWorkouts().then(setWorkouts).catch(() => {})
  }, [])

  const events = workouts.map(w => ({
    id: String(w.id),
    title: `${TYPE_LABELS[w.workout_type] || w.workout_type}${w.target_distance_km ? ` ${w.target_distance_km}km` : ''}`,
    date: w.date_adjusted || w.date_scheduled,
    backgroundColor: TYPE_COLORS[w.workout_type] || '#9ca3af',
    borderColor: w.completed_activity_id ? '#15803d' : 'transparent',
    textColor: w.workout_type === 'rest' ? '#6b7280' : '#fff',
    extendedProps: { workout: w },
  }))

  const handleEventDrop = async (info) => {
    const w = info.event.extendedProps.workout
    const newDate = info.event.startStr
    await updateWorkout(w.id, { date_adjusted: newDate })
    setWorkouts(prev => prev.map(pw => pw.id === w.id ? { ...pw, date_adjusted: newDate } : pw))
  }

  const handleEventClick = (info) => {
    setSelected(info.event.extendedProps.workout)
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <FullCalendar
        plugins={[dayGridPlugin, interactionPlugin]}
        initialView="dayGridMonth"
        events={events}
        editable={true}
        eventDrop={handleEventDrop}
        eventClick={handleEventClick}
        height="auto"
      />
      {selected && (
        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
          <div className="flex justify-between items-start">
            <div>
              <p className="font-semibold">{TYPE_LABELS[selected.workout_type]}</p>
              {selected.target_distance_km && <p className="text-sm text-gray-600">{selected.target_distance_km} km</p>}
              {selected.notes && <p className="text-sm text-gray-500 mt-1">{selected.notes}</p>}
              {selected.completed_activity_id && <p className="text-sm text-green-600 mt-1">Completed ✓</p>}
            </div>
            <button onClick={() => setSelected(null)} className="text-gray-400 hover:text-gray-600">✕</button>
          </div>
        </div>
      )}
    </div>
  )
}
