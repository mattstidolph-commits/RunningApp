import { useEffect, useState } from 'react'
import { getProgressCharts, syncGarmin } from '../api'
import PaceChart from '../components/PaceChart'
import MileageChart from '../components/MileageChart'
import FitUpload from '../components/FitUpload'

export default function Progress() {
  const [charts, setCharts] = useState(null)
  const [syncing, setSyncing] = useState(false)
  const [syncMsg, setSyncMsg] = useState(null)

  const loadCharts = () => getProgressCharts().then(setCharts)
  useEffect(() => { loadCharts() }, [])

  const handleSync = async () => {
    setSyncing(true)
    try {
      const res = await syncGarmin()
      setSyncMsg(res.message)
    } catch {
      setSyncMsg('Sync failed.')
    } finally {
      setSyncing(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h2 className="font-bold text-gray-800 mb-4">Sync Garmin Data</h2>
        <FitUpload onUploaded={loadCharts} />
        <div className="mt-4 flex items-center gap-3">
          <button onClick={handleSync} disabled={syncing}
            className="px-4 py-2 bg-gray-800 text-white text-sm rounded-lg hover:bg-gray-700 disabled:opacity-50">
            {syncing ? 'Syncing...' : 'Sync from Garmin Connect'}
          </button>
          {syncMsg && <p className="text-sm text-gray-500">{syncMsg}</p>}
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h2 className="font-bold text-gray-800 mb-4">Easy Run Pace Trend</h2>
        <PaceChart data={charts?.pace_trend} />
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h2 className="font-bold text-gray-800 mb-4">Weekly Mileage</h2>
        <MileageChart data={charts?.weekly_mileage} />
      </div>

      {charts?.hr_trend?.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="font-bold text-gray-800 mb-3">Heart Rate Trend</h2>
          <p className="text-sm text-gray-500">
            Latest avg HR: {charts.hr_trend[charts.hr_trend.length - 1]?.avg_hr} bpm
          </p>
        </div>
      )}
    </div>
  )
}
