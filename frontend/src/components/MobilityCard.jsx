import { useState } from 'react'
import { logMobilitySession } from '../api'

export default function MobilityCard({ routineName, routine, onLogged }) {
  const [expanded, setExpanded] = useState(false)
  const [logging, setLogging] = useState(false)
  const [done, setDone] = useState(false)

  const markDone = async () => {
    setLogging(true)
    try {
      await logMobilitySession({ routine_name: routineName, duration_mins: routine?.duration_mins || 10, recommended: true })
      setDone(true)
      onLogged?.()
    } finally {
      setLogging(false)
    }
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Mobility Today</p>
      <div className="flex items-center justify-between mb-3">
        <div>
          <p className="font-semibold text-gray-800">{routineName}</p>
          {routine && <p className="text-sm text-gray-500">{routine.duration_mins} min · {routine.areas.join(', ')}</p>}
        </div>
        {done ? (
          <span className="text-green-600 font-medium text-sm">Done ✓</span>
        ) : (
          <button onClick={markDone} disabled={logging}
            className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50">
            {logging ? '...' : 'Mark Done'}
          </button>
        )}
      </div>
      {routine?.exercises && (
        <button onClick={() => setExpanded(!expanded)}
          className="text-sm text-blue-600 hover:underline">
          {expanded ? 'Hide exercises' : 'Show exercises'}
        </button>
      )}
      {expanded && routine?.exercises && (
        <ul className="mt-3 space-y-1">
          {routine.exercises.map((ex, i) => (
            <li key={i} className="text-sm text-gray-600 flex gap-2">
              <span className="text-gray-400">{Math.floor(ex.duration_secs / 60)}:{String(ex.duration_secs % 60).padStart(2,'0')}</span>
              <span>{ex.name}</span>
              {ex.cue && <span className="text-gray-400">— {ex.cue}</span>}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
