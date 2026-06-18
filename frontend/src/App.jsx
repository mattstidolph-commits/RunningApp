import { BrowserRouter, NavLink, Routes, Route, Navigate } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Calendar from './pages/Calendar'
import TrainingPlan from './pages/TrainingPlan'
import Mobility from './pages/Mobility'
import Progress from './pages/Progress'

const NAV = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/calendar', label: 'Calendar' },
  { to: '/plan', label: 'Training Plan' },
  { to: '/mobility', label: 'Mobility' },
  { to: '/progress', label: 'Progress' },
]

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50 flex flex-col">
        <nav className="bg-white border-b border-gray-200 px-6 py-3 flex gap-6 items-center">
          <span className="font-bold text-blue-600 text-lg mr-4">Running App</span>
          {NAV.map(n => (
            <NavLink
              key={n.to}
              to={n.to}
              className={({ isActive }) =>
                `text-sm font-medium ${isActive ? 'text-blue-600' : 'text-gray-500 hover:text-gray-800'}`
              }
            >
              {n.label}
            </NavLink>
          ))}
        </nav>
        <main className="flex-1 p-6 max-w-6xl mx-auto w-full">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/calendar" element={<Calendar />} />
            <Route path="/plan" element={<TrainingPlan />} />
            <Route path="/mobility" element={<Mobility />} />
            <Route path="/progress" element={<Progress />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
