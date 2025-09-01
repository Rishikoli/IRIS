import React from 'react'
import WebSocketTestPanel from '../components/WebSocketTestPanel'

const WebSocketTestPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            WebSocket Real-time Testing
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            This page allows you to test the real-time WebSocket functionality of the IRIS platform.
            You can verify connection status, test alert generation, and monitor real-time notifications.
          </p>
        </div>
        
        <WebSocketTestPanel />
        
        <div className="mt-8 bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">How to Test</h2>
          <div className="space-y-4 text-gray-700">
            <div>
              <h3 className="font-medium text-gray-900">1. Connection Test</h3>
              <p>Click "Test Connection" to verify WebSocket connectivity. You should see a connection confirmation and may receive mock alerts every 30 seconds.</p>
            </div>
            
            <div>
              <h3 className="font-medium text-gray-900">2. High-Risk Tip Alert Test</h3>
              <p>Click "Test High-Risk Tip Alert" to submit a high-risk investment tip and verify that a real-time alert is generated and received through the WebSocket connection.</p>
            </div>
            
            <div>
              <h3 className="font-medium text-gray-900">3. Monitor Alerts</h3>
              <p>The "Recent Alerts" section shows all received alerts. Click on an alert to mark it as read. Use "Clear Alerts" to reset the alert list.</p>
            </div>
            
            <div>
              <h3 className="font-medium text-gray-900">4. Integration Testing</h3>
              <p>Navigate to other pages (Dashboard, Upload PDF) and perform actions that should trigger alerts. Return to this page to verify alerts were received.</p>
            </div>
          </div>
        </div>
        
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-medium text-blue-900 mb-2">📋 Requirements Verification</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>✅ <strong>Requirement 4.5:</strong> Real-time alerts for high-risk cases</li>
            <li>✅ <strong>Requirement 8.4:</strong> WebSocket connections for live updates</li>
            <li>✅ <strong>Task 10:</strong> Basic WebSocket endpoint /ws/alerts for live demo effect</li>
            <li>✅ <strong>Task 10:</strong> Simple WebSocket connection in React frontend</li>
            <li>✅ <strong>Task 10:</strong> Mock real-time notifications for high-risk cases</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default WebSocketTestPage