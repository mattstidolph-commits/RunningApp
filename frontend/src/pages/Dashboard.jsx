import { useEffect, useState } from 'react'
import { getDashboard, getMobilityRecommendation } from '../api'
import WorkoutCard from '../components/WorkoutCard'
import MobilityCard from '../components/MobilityCard'
import ActivitySummary from '../components/ActivitySummary'
import WeeklySnapshot from '../components/WeeklySnapshot'

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [mobility, setMobility] = useState(null)
  const [error, setError] = useState(null)

  const load = async () => {
    try {
      const [dash, mob] = await Promise.all([getDashboard(), getMobilityRecommendation()])
      setData(dash)
      setMobility(mob)
    } catch (e) {
      setError('Could not load dashboard. Is the backend running?')
    }
  }

  useEffect(() => { load() }, [])

  if (error) return <p className="text-red-500">{error}</p>
  if (!data) return <p className="text-gray-400">Loading...</p>

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-gray-800">
        {new Date().toLocaleDateString('en-ZA', { weekday: 'long', day: 'numeric', month: 'long' })}
      </h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <WorkoutCard workout={data.today_workout} />
        {mobility && (
          <MobilityCard
            routineName={mobility.routine_name}
            routine={mobility.routine}
            onLogged={load}
          />
        )}
      </div>
      <ActivitySummary activity={data.last_activity} />
      <WeeklySnapshot stats={data.weekly_stats} />
    </div>
  )
}
