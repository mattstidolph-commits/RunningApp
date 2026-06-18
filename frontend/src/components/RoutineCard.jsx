import { useState } from 'react'
import { logMobilitySession } from '../api'

export default function RoutineCard({ routine, onLogged }) {
  const [expanded, setExpanded] = useState(false)
  const [logging, setLogging] = useState(false)

  const log = async () => {
    setLogging(true)
    try {
      await logMobilitySession({ routine_name: routine.name, duration_mins: routine.duration_mins })
      onLogged?.()
    } finally {
      setLogging(false)
    }
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4">
      <div className="flex justify-between items-start mb-2">
        <div>
          <p className="font-semibold text-gray-800 text-sm">{routine.name}</p>
          <p className="text-xs text-gray-500">{routine.duration_mins} min · {routine.areas.join(', ')}</p>
        </div>
        <button onClick={log} disabled={logging}
          className="text-xs px-3 py-1 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
          {logging ? '...' : 'Log'}
        </button>
      </div>
      <button onClick={() => setExpanded(!expanded)} className="text-xs text-blue-500 hover:underline">
        {expanded ? 'Hide' : 'Show exercises'}
      </button>
      {expanded && (
        <ul className="mt-2 space-y-1">
          {routine.exercises.map((ex, i) => (
            <li key={i} className="text-xs text-gray-600 flex gap-2">
              <span className="text-gray-400 shrink-0">
                {Math.floor(ex.duration_secs/60)}:{String(ex.duration_secs%60).padStart(2,'0')}
              </span>
              <span>{ex.name}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
