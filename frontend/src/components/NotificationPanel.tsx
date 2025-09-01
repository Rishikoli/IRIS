import React, { useState } from 'react'
import { WebSocketAlert } from '../services/websocket'

interface NotificationPanelProps {
  alerts: WebSocketAlert[]
  isConnected: boolean
  connectionState: string
  onMarkAsRead: (alertId: string) => void
  onClearAll: () => void
  unreadCount: number
}

const NotificationPanel: React.FC<NotificationPanelProps> = ({
  alerts,
  isConnected,
  connectionState,
  onMarkAsRead,
  onClearAll,
  unreadCount
}) => {
  const [isOpen, setIsOpen] = useState(false)

  const getPriorityColor = (priority?: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 border-red-300 text-red-800'
      case 'medium':
        return 'bg-yellow-100 border-yellow-300 text-yellow-800'
      case 'low':
        return 'bg-blue-100 border-blue-300 text-blue-800'
      default:
        return 'bg-gray-100 border-gray-300 text-gray-800'
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'high_risk_tip':
        return '⚠️'
      case 'fraud_chain_update':
        return '🔗'
      case 'document_anomaly':
        return '📄'
      case 'advisor_verification':
        return '👤'
      case 'regional_spike':
        return '📈'
      case 'connection':
        return '🔌'
      default:
        return '🔔'
    }
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    
    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`
    return date.toLocaleDateString()
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
    <div className="relative">
      {/* Notification Bell */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-600 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-lg"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
        
        {/* Unread Badge */}
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
        
        {/* Connection Status Indicator */}
        <span className={`absolute -bottom-1 -right-1 w-3 h-3 rounded-full ${
          isConnected ? 'bg-green-400' : 'bg-red-400'
        }`} />
      </button>

      {/* Notification Panel */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-lg border border-gray-200 z-50 max-h-96 overflow-hidden">
          {/* Header */}
          <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">
                Real-time Alerts
              </h3>
              <div className="flex items-center space-x-2">
                <span className={`text-sm ${getConnectionStatusColor()}`}>
                  {connectionState}
                </span>
                {alerts.length > 0 && (
                  <button
                    onClick={onClearAll}
                    className="text-sm text-blue-600 hover:text-blue-800"
                  >
                    Clear All
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Alerts List */}
          <div className="max-h-80 overflow-y-auto">
            {alerts.length === 0 ? (
              <div className="px-4 py-8 text-center text-gray-500">
                <svg className="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
                <p>No alerts yet</p>
                <p className="text-sm">Real-time notifications will appear here</p>
              </div>
            ) : (
              alerts.map((alert) => (
                <div
                  key={alert.id}
                  className={`px-4 py-3 border-b border-gray-100 hover:bg-gray-50 cursor-pointer ${
                    !alert.read ? 'bg-blue-50' : ''
                  }`}
                  onClick={() => onMarkAsRead(alert.id)}
                >
                  <div className="flex items-start space-x-3">
                    <span className="text-lg flex-shrink-0 mt-0.5">
                      {getTypeIcon(alert.type)}
                    </span>
                    <div className="flex-1 min-w-0">
                      {alert.title && (
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {alert.title}
                        </p>
                      )}
                      <p className="text-sm text-gray-600 mt-1">
                        {alert.message}
                      </p>
                      
                      {/* Additional Details */}
                      <div className="flex items-center justify-between mt-2">
                        <div className="flex items-center space-x-2">
                          {alert.priority && (
                            <span className={`px-2 py-1 text-xs rounded-full border ${getPriorityColor(alert.priority)}`}>
                              {alert.priority.toUpperCase()}
                            </span>
                          )}
                          {alert.risk_score && (
                            <span className="text-xs text-gray-500">
                              Risk: {alert.risk_score}%
                            </span>
                          )}
                          {alert.sector && (
                            <span className="text-xs text-gray-500">
                              {alert.sector}
                            </span>
                          )}
                          {alert.region && (
                            <span className="text-xs text-gray-500">
                              {alert.region}
                            </span>
                          )}
                        </div>
                        <span className="text-xs text-gray-400">
                          {formatTimestamp(alert.timestamp)}
                        </span>
                      </div>
                    </div>
                    
                    {!alert.read && (
                      <div className="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0 mt-2" />
                    )}
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Footer */}
          {!isConnected && (
            <div className="px-4 py-2 bg-red-50 border-t border-red-200">
              <p className="text-sm text-red-600 text-center">
                Connection lost. Attempting to reconnect...
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default NotificationPanel