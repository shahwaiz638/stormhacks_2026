import { Navigate, Outlet, Route, Routes } from 'react-router-dom'
import Navbar from '@/components/Navbar'
import HomePage from '@/pages/HomePage'
import FoundReportPage from '@/pages/FoundReportPage'
import LostReportPage from '@/pages/LostReportPage'

function AppLayout() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main>
        <Outlet />
      </main>
    </div>
  )
}

function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<HomePage />} />
        <Route path="report">
          <Route index element={<Navigate to="lost" replace />} />
          <Route path="lost" element={<LostReportPage />} />
          <Route path="found" element={<FoundReportPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}

export default App
