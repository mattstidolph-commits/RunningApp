export default function ActivitySummary({ activity }) {
  if (!activity) return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Last Activity</p>
      <p className="text-sm text-gray-400">No activities synced yet. Upload a FIT file on the Progress page.</p>
    </div>
  )
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Last Activity</p>
      <p className="font-semibold text-gray-800 capitalize mb-2">{activity.type} — {activity.date}</p>
      <div className="flex gap-4 text-sm text-gray-600">
        {activity.distance_km && <span>{activity.distance_km} km</span>}
        {activity.avg_pace && <span>{activity.avg_pace}</span>}
        {activity.avg_hr && <span>{activity.avg_hr} bpm</span>}
        {activity.duration_mins && <span>{Math.round(activity.duration_mins)} min</span>}
      </div>
    </div>
  )
}
