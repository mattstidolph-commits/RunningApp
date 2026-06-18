import { useEffect, useState } from 'react'
import { getMobilityRoutines, getMobilityRecommendation, getMobilitySessions } from '../api'
import MobilityCard from '../components/MobilityCard'
import RoutineCard from '../components/RoutineCard'

const AREAS = ['all', 'hips', 'calves', 'ankles', 'full_body', 'thoracic', 'glutes', 'shoulders']

export default function Mobility() {
  const [recommendation, setRecommendation] = useState(null)
  const [routines, setRoutines] = useState([])
  const [sessions, setSessions] = useState([])
  const [areaFilter, setAreaFilter] = useState('all')

  const loadAll = async () => {
    const [rec, rts, sess] = await Promise.all([
      getMobilityRecommendation(),
      getMobilityRoutines(),
      getMobilitySessions(30),
    ])
    setRecommendation(rec)
    setRoutines(rts)
    setSessions(sess)
  }

  useEffect(() => { loadAll() }, [])

  const filteredRoutines = areaFilter === 'all'
    ? routines
    : routines.filter(r => r.areas.includes(areaFilter))

  return (
    <div className="space-y-6">
      {recommendation && (
        <div>
          <h2 className="text-lg font-bold text-gray-800 mb-3">Recommended Today</h2>
          <MobilityCard
            routineName={recommendation.routine_name}
            routine={recommendation.routine}
            onLogged={loadAll}
          />
        </div>
      )}

      <div>
        <div className="flex justify-between items-center mb-3">
          <h2 className="text-lg font-bold text-gray-800">Routine Library</h2>
          <select value={areaFilter} onChange={e => setAreaFilter(e.target.value)}
            className="text-sm border rounded px-2 py-1">
            {AREAS.map(a => <option key={a} value={a}>{a === 'all' ? 'All areas' : a}</option>)}
          </select>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredRoutines.map(r => (
            <RoutineCard key={r.name} routine={r} onLogged={loadAll} />
          ))}
        </div>
      </div>

      <div>
        <h2 className="text-lg font-bold text-gray-800 mb-3">History (last 30 days)</h2>
        {sessions.length === 0
          ? <p className="text-sm text-gray-400">No sessions logged yet.</p>
          : (
            <div className="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100">
              {sessions.map(s => (
                <div key={s.id} className="flex justify-between items-center px-4 py-3 text-sm">
                  <div>
                    <p className="font-medium text-gray-800">{s.routine_name}</p>
                    <p className="text-gray-500 text-xs">{s.date}</p>
                  </div>
                  <p className="text-gray-600">{s.duration_mins} min</p>
                </div>
              ))}
            </div>
          )
        }
      </div>
    </div>
  )
}
