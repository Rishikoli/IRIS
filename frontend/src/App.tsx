import { Routes, Route } from 'react-router-dom'
import { ThemeProvider } from './contexts/ThemeContext'
import { ToastProvider } from './contexts/ToastContext'
import ToastContainer from './components/ui/ToastContainer'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import DashboardPage from './pages/DashboardPage'
import InvestigationPage from './pages/InvestigationPage'
import FraudChainsPage from './pages/FraudChainsPage'
import WebSocketTestPage from './pages/WebSocketTestPage'
import AnalyticsDashboard from './components/AnalyticsDashboard'

function App() {
  return (
    <ThemeProvider>
      <ToastProvider>
        <Layout>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/analytics" element={<AnalyticsDashboard />} />
            <Route path="/investigation" element={<InvestigationPage />} />
            <Route path="/fraud-chains" element={<FraudChainsPage />} />
            <Route path="/search" element={<InvestigationPage />} />
            {/* All functionality is now integrated into the dashboard */}
            <Route path="/check-tip" element={<DashboardPage />} />
            <Route path="/verify-advisor" element={<DashboardPage />} />
            <Route path="/upload-pdf" element={<DashboardPage />} />
            <Route path="/forecast" element={<DashboardPage />} />
            <Route path="/websocket-test" element={<WebSocketTestPage />} />
          </Routes>
          <ToastContainer />
        </Layout>
      </ToastProvider>
    </ThemeProvider>
  )
}

export default App