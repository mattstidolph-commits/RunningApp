import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

export default function MileageChart({ data }) {
  if (!data?.length) return <p className="text-sm text-gray-400">No mileage data yet.</p>
  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="week" tick={{ fontSize: 11 }} tickFormatter={d => d.slice(5)} />
        <YAxis tick={{ fontSize: 11 }} unit="km" />
        <Tooltip formatter={(v, n) => n === 'run_km' ? [`${v.toFixed(1)} km`, 'Running'] : [v, 'CrossFit sessions']} />
        <Bar dataKey="run_km" fill="#3b82f6" radius={[3,3,0,0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
