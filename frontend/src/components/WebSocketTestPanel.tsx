import React, { useState } from 'react'
import { useWebSocket } from '../hooks/useWebSocket'

const WebSocketTestPanel: React.FC = () => {
  const {
    alerts,
    isConnected,
    connectionState,
    connect,
    disconnect,
    clearAlerts,
    markAsRead,
    unreadCount
  } = useWebSocket()

  const [testResults, setTestResults] = useState<string[]>([])
  const [isRunningTests, setIsRunningTests] = useState(false)

  const addTestResult = (message: string) => {
    setTestResults(prev => [...prev, `${new Date().toLocaleTimeString()}: ${message}`])
  }

  const runConnectionTest = async () => {
    setIsRunningTests(true)
    setTestResults([])
    
    addTestResult('🔌 Starting WebSocket connection test...')
    
    try {
      await connect()
      addTestResult('✅ WebSocket connected successfully')
      
      // Wait for initial connection message or mock alert
      setTimeout(() => {
        if (alerts.length > 0) {
          addTestResult(`📨 Received ${alerts.length} alert(s)`)
          addTestResult(`   Latest: ${alerts[0].type} - ${alerts[0].message}`)
        } else {
          addTestResult('⏳ No alerts received yet (this is normal)')
        }
      }, 2000)
      
    } catch (error) {
      addTestResult(`❌ Connection failed: ${error}`)
    }
    
    setIsRunningTests(false)
  }

  const testHighRiskTip = async () => {
    addTestResult('🧪 Testing high-risk tip submission...')
    
    const testTip = {
      message: "🚨 URGENT! Buy TESTSTOCK now! Guaranteed 500% returns in 24 hours! Limited time offer!",
      source: "websocket_test"
    }
    
    try {
      const response = await fetch('/api/check-tip', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(testTip)
      })
      
      if (response.ok) {
        const result = await response.json()
        addTestResult(`✅ Tip analyzed - Risk Score: ${result.assessment.score}%`)
        addTestResult('⏳ Waiting for real-time alert...')
        
        // Check for new alerts after a short delay
        setTimeout(() => {
          const newAlerts = alerts.filter(alert => 
            alert.type === 'high_risk_tip' && 
            alert.message.includes('fraud probability')
          )
          
          if (newAlerts.length > 0) {
            addTestResult('🚨 Real-time alert received successfully!')
          } else {
            addTestResult('⚠️ No real-time alert received (check server logs)')
          }
        }, 3000)
        
      } else {
        addTestResult(`❌ API request failed: ${response.status}`)
      }
    } catch (error) {
      addTestResult(`❌ Test failed: ${error}`)
    }
  }

  const getConnectionStatusColor = () => {
    switch (connectionState) {
      case 'connected':
        return 'text-green-600'
      case 'connecting':
        return 'text-yellow-600'
      case 'disconnected':
        return 'text-red-600'
      default:
        return 'text-gray-600'
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">WebSocket Test Panel</h2>
      
      {/* Connection Status */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <h3 className="text-lg font-semibold mb-2">Connection Status</h3>
        <div className="flex items-center space-x-4">
          <span className={`font-medium ${getConnectionStatusColor()}`}>
            Status: {connectionState}
          </span>
          <span className="text-gray-600">
            Connected: {isConnected ? '✅' : '❌'}
          </span>
          <span className="text-gray-600">
            Unread Alerts: {unreadCount}
          </span>
          <span className="text-gray-600">
            Total Alerts: {alerts.length}
          </span>
        </div>
      </div>

      {/* Test Controls */}
      <div className="mb-6 space-y-4">
        <h3 className="text-lg font-semibold">Test Controls</h3>
        <div className="flex flex-wrap gap-3">
          <button
            onClick={runConnectionTest}
            disabled={isRunningTests}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {isRunningTests ? 'Testing...' : 'Test Connection'}
          </button>
          
          <button
            onClick={testHighRiskTip}
            disabled={!isConnected}
            className="px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 disabled:opacity-50"
          >
            Test High-Risk Tip Alert
          </button>
          
          <button
            onClick={disconnect}
            disabled={!isConnected}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50"
          >
            Disconnect
          </button>
          
          <button
            onClick={clearAlerts}
            className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
          >
            Clear Alerts
          </button>
        </div>
      </div>

      {/* Test Results */}
      {testResults.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-2">Test Results</h3>
          <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm max-h-64 overflow-y-auto">
            {testResults.map((result, index) => (
              <div key={index}>{result}</div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Alerts */}
      {alerts.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-2">Recent Alerts ({alerts.length})</h3>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {alerts.slice(0, 5).map((alert) => (
              <div
                key={alert.id}
                className={`p-3 rounded-lg border ${
                  !alert.read ? 'bg-blue-50 border-blue-200' : 'bg-gray-50 border-gray-200'
                }`}
                onClick={() => markAsRead(alert.id)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <span className="text-lg">
                        {alert.type === 'high_risk_tip' ? '⚠️' : 
                         alert.type === 'fraud_chain_update' ? '🔗' :
                         alert.type === 'document_anomaly' ? '📄' :
                         alert.type === 'connection' ? '🔌' : '🔔'}
                      </span>
                      <span className="font-medium text-gray-900">
                        {alert.title || alert.type}
                      </span>
                      {alert.priority && (
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          alert.priority === 'high' ? 'bg-red-100 text-red-800' :
                          alert.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-blue-100 text-blue-800'
                        }`}>
                          {alert.priority.toUpperCase()}
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mt-1">{alert.message}</p>
                    <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                      <span>{new Date(alert.timestamp).toLocaleTimeString()}</span>
                      {alert.risk_score && <span>Risk: {alert.risk_score}%</span>}
                      {alert.sector && <span>Sector: {alert.sector}</span>}
                      {alert.region && <span>Region: {alert.region}</span>}
                    </div>
                  </div>
                  {!alert.read && (
                    <div className="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0 mt-2" />
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default WebSocketTestPanel