import { useEffect, useState } from 'react'
import { getPlans, activatePlan, getWorkouts } from '../api'
import WorkoutEditor from '../components/WorkoutEditor'

const DAY_NAMES = ['', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
const TYPE_COLORS = {
  easy_run: 'bg-blue-100 text-blue-700', long_run: 'bg-purple-100 text-purple-700',
  tempo: 'bg-orange-100 text-orange-700', intervals: 'bg-red-100 text-red-700',
  cross_train: 'bg-green-100 text-green-700', rest: 'bg-gray-100 text-gray-500',
}

export default function TrainingPlan() {
  const [plans, setPlans] = useState([])
  const [workouts, setWorkouts] = useState([])
  const [selectedPlanId, setSelectedPlanId] = useState('')
  const [startDate, setStartDate] = useState(new Date().toISOString().split('T')[0])
  const [activating, setActivating] = useState(false)

  useEffect(() => {
    getPlans().then(setPlans)
    getWorkouts().then(setWorkouts)
  }, [])

  const activate = async () => {
    if (!selectedPlanId) return
    if (!window.confirm('Activating a new plan will reset your current schedule. Continue?')) return
    setActivating(true)
    try {
      await activatePlan(Number(selectedPlanId), startDate)
      const updated = await getWorkouts()
      setWorkouts(updated)
    } finally {
      setActivating(false)
    }
  }

  const grouped = workouts.reduce((acc, w) => {
    if (!acc[w.week]) acc[w.week] = []
    acc[w.week].push(w)
    return acc
  }, {})

  const weeks = Object.keys(grouped).sort((a, b) => Number(a) - Number(b))
  const currentWeek = weeks.find(wk =>
    grouped[wk].some(w => w.date_scheduled && new Date(w.date_scheduled) >= new Date(new Date().toDateString()))
  ) || weeks[0]

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl border border-gray-200 p-5 flex flex-wrap gap-4 items-end">
        <div>
          <label className="block text-xs text-gray-500 mb-1">Plan</label>
          <select value={selectedPlanId} onChange={e => setSelectedPlanId(e.target.value)}
            className="border rounded px-3 py-1.5 text-sm">
            <option value="">Select a plan...</option>
            {plans.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-xs text-gray-500 mb-1">Start Date (Monday)</label>
          <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)}
            className="border rounded px-3 py-1.5 text-sm" />
        </div>
        <button onClick={activate} disabled={!selectedPlanId || activating}
          className="px-4 py-1.5 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50">
          {activating ? 'Activating...' : 'Activate Plan'}
        </button>
      </div>

      {weeks.map(wk => (
        <div key={wk} className={`bg-white rounded-xl border p-5 ${wk === currentWeek ? 'border-blue-400' : 'border-gray-200'}`}>
          <p className="font-semibold text-gray-700 mb-3">
            Week {wk} {wk === currentWeek && <span className="ml-2 text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">Current</span>}
          </p>
          <div className="grid grid-cols-7 gap-2">
            {grouped[wk].sort((a,b) => a.day - b.day).map(w => (
              <div key={w.id} className={`rounded-lg p-2 text-xs ${TYPE_COLORS[w.workout_type] || 'bg-gray-100 text-gray-600'}`}>
                <p className="font-semibold">{DAY_NAMES[w.day]}</p>
                <p>{w.workout_type.replace('_', ' ')}</p>
                {w.target_distance_km && <p>{w.target_distance_km}km</p>}
                <WorkoutEditor
                  workout={w}
                  onSaved={updated => setWorkouts(prev => prev.map(pw => pw.id === updated.id ? updated : pw))}
                />
              </div>
            ))}
          </div>
        </div>
      ))}
      {weeks.length === 0 && <p className="text-gray-400 text-sm">No plan activated yet. Select a plan above and click Activate.</p>}
    </div>
  )
}
