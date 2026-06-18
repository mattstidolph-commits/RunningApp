export default function WeeklySnapshot({ stats }) {
  if (!stats) return null
  const pct = stats.workouts_planned > 0
    ? Math.round((stats.workouts_completed / stats.workouts_planned) * 100)
    : 0
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">This Week</p>
      <div className="flex gap-6">
        <div className="text-center">
          <p className="text-2xl font-bold text-gray-800">{stats.km_this_week}</p>
          <p className="text-xs text-gray-500">km run</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-gray-800">{stats.crossfit_sessions}</p>
          <p className="text-xs text-gray-500">CrossFit</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-gray-800">{stats.workouts_completed}/{stats.workouts_planned}</p>
          <p className="text-xs text-gray-500">workouts done</p>
        </div>
      </div>
      <div className="mt-3 h-2 bg-gray-100 rounded-full overflow-hidden">
        <div className="h-full bg-blue-500 rounded-full" style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}
