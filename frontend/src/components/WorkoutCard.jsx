const TYPE_COLORS = {
  easy_run: 'bg-blue-100 text-blue-800',
  long_run: 'bg-purple-100 text-purple-800',
  tempo: 'bg-orange-100 text-orange-800',
  intervals: 'bg-red-100 text-red-800',
  cross_train: 'bg-green-100 text-green-800',
  rest: 'bg-gray-100 text-gray-600',
}

const TYPE_LABELS = {
  easy_run: 'Easy Run', long_run: 'Long Run', tempo: 'Tempo Run',
  intervals: 'Intervals', cross_train: 'Cross Train', rest: 'Rest Day',
}

export default function WorkoutCard({ workout }) {
  if (!workout) return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <p className="text-sm text-gray-400">No workout scheduled for today.</p>
    </div>
  )
  const color = TYPE_COLORS[workout.workout_type] || 'bg-gray-100 text-gray-600'
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Today's Workout</p>
      <div className="flex items-center gap-3 mb-3">
        <span className={`px-3 py-1 rounded-full text-sm font-medium ${color}`}>
          {TYPE_LABELS[workout.workout_type] || workout.workout_type}
        </span>
        {workout.target_distance_km && (
          <span className="text-gray-700 font-semibold">{workout.target_distance_km} km</span>
        )}
      </div>
      {workout.notes && <p className="text-sm text-gray-600">{workout.notes}</p>}
    </div>
  )
}
