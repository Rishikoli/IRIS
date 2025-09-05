import { Routes, Route } from 'react-router-dom'
import { ThemeProvider } from './contexts/ThemeContext'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import DashboardPage from './pages/DashboardPage'
import FraudChainPage from './pages/FraudChainPage'
import ReviewPage from './pages/ReviewPage'
import WebSocketTestPage from './pages/WebSocketTestPage'
import AnalyticsDashboard from './components/AnalyticsDashboard'

function App() {
  return (
    <ThemeProvider>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/analytics" element={<AnalyticsDashboard />} />
          <Route path="/fraud-chains" element={<FraudChainPage />} />
          {/* All functionality is now integrated into the dashboard */}
          <Route path="/check-tip" element={<DashboardPage />} />
          <Route path="/verify-advisor" element={<DashboardPage />} />
          <Route path="/upload-pdf" element={<DashboardPage />} />
          <Route path="/forecast" element={<DashboardPage />} />
          <Route path="/review" element={<ReviewPage />} />
          <Route path="/websocket-test" element={<WebSocketTestPage />} />
        </Routes>
      </Layout>
    </ThemeProvider>
  )
}

export default App