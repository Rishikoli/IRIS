import { useState, useEffect, useCallback, useRef } from 'react'
import { webSocketService, WebSocketAlert } from '../services/websocket'

export interface UseWebSocketReturn {
  alerts: WebSocketAlert[]
  isConnected: boolean
  connectionState: string
  connect: () => Promise<void>
  disconnect: () => void
  clearAlerts: () => void
  markAsRead: (alertId: string) => void
  unreadCount: number
}

export const useWebSocket = (): UseWebSocketReturn => {
  const [alerts, setAlerts] = useState<WebSocketAlert[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const [connectionState, setConnectionState] = useState('disconnected')
  const unsubscribeRef = useRef<(() => void) | null>(null)

  const updateConnectionState = useCallback(() => {
    const connected = webSocketService.isConnected()
    const state = webSocketService.getConnectionState()
    setIsConnected(connected)
    setConnectionState(state)
  }, [])

  const handleAlert = useCallback((alert: WebSocketAlert) => {
    setAlerts(prev => {
      // Avoid duplicates
      if (prev.some(a => a.id === alert.id)) {
        return prev
      }
      
      // Add new alert to the beginning of the array
      const newAlerts = [alert, ...prev]
      
      // Keep only the last 50 alerts to prevent memory issues
      return newAlerts.slice(0, 50)
    })
  }, [])

  const connect = useCallback(async () => {
    try {
      await webSocketService.connect()
      updateConnectionState()
    } catch (error) {
      console.error('Failed to connect to WebSocket:', error)
      updateConnectionState()
    }
  }, [updateConnectionState])

  const disconnect = useCallback(() => {
    webSocketService.disconnect()
    updateConnectionState()
  }, [updateConnectionState])

  const clearAlerts = useCallback(() => {
    setAlerts([])
  }, [])

  const markAsRead = useCallback((alertId: string) => {
    setAlerts(prev => 
      prev.map(alert => 
        alert.id === alertId 
          ? { ...alert, read: true }
          : alert
      )
    )
  }, [])

  const unreadCount = alerts.filter(alert => !alert.read).length

  useEffect(() => {
    // Subscribe to alerts
    unsubscribeRef.current = webSocketService.onAlert(handleAlert)
    
    // Update connection state periodically
    const interval = setInterval(updateConnectionState, 1000)
    
    // Initial connection state check
    updateConnectionState()

    return () => {
      // Cleanup
      if (unsubscribeRef.current) {
        unsubscribeRef.current()
      }
      clearInterval(interval)
    }
  }, [handleAlert, updateConnectionState])

  return {
    alerts,
    isConnected,
    connectionState,
    connect,
    disconnect,
    clearAlerts,
    markAsRead,
    unreadCount
  }
}