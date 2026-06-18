import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

function paceLabel(secs) {
  const m = Math.floor(secs / 60), s = secs % 60
  return `${m}:${String(s).padStart(2,'0')}/km`
}

export default function PaceChart({ data }) {
  if (!data?.length) return <p className="text-sm text-gray-400">No pace data yet. Import some runs.</p>
  return (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="date" tick={{ fontSize: 11 }} tickFormatter={d => d.slice(5)} />
        <YAxis reversed domain={['auto','auto']} tick={{ fontSize: 11 }}
          tickFormatter={paceLabel} />
        <Tooltip formatter={(v) => paceLabel(v)} labelFormatter={l => `Date: ${l}`} />
        <Line type="monotone" dataKey="pace_secs" stroke="#3b82f6" strokeWidth={2} dot={{ r: 3 }} />
      </LineChart>
    </ResponsiveContainer>
  )
}
