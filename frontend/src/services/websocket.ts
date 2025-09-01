export interface WebSocketAlert {
  id: string
  type: 'high_risk_tip' | 'fraud_chain_update' | 'document_anomaly' | 'advisor_verification' | 'regional_spike' | 'connection'
  title?: string
  message: string
  priority?: 'low' | 'medium' | 'high'
  timestamp: string
  read: boolean
  // Type-specific properties
  sector?: string
  region?: string
  risk_score?: number
  chain_id?: string
  new_nodes?: number
  anomaly_count?: number
  advisor_name?: string
  tip_count?: number
  increase_percentage?: number
}

export type WebSocketEventHandler = (alert: WebSocketAlert) => void

export class WebSocketService {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private eventHandlers: WebSocketEventHandler[] = []
  private isConnecting = false

  constructor(private url: string = 'ws://localhost:8000/ws/alerts') {}

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        resolve()
        return
      }

      if (this.isConnecting) {
        return
      }

      this.isConnecting = true

      try {
        this.ws = new WebSocket(this.url)

        this.ws.onopen = () => {
          console.log('WebSocket connected to IRIS alerts')
          this.reconnectAttempts = 0
          this.isConnecting = false
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const alert: WebSocketAlert = JSON.parse(event.data)
            this.handleAlert(alert)
          } catch (error) {
            console.error('Error parsing WebSocket message:', error)
          }
        }

        this.ws.onclose = (event) => {
          console.log('WebSocket connection closed:', event.code, event.reason)
          this.isConnecting = false
          this.scheduleReconnect()
        }

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          this.isConnecting = false
          reject(error)
        }
      } catch (error) {
        this.isConnecting = false
        reject(error)
      }
    })
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.reconnectAttempts = this.maxReconnectAttempts // Prevent reconnection
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)
      
      console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
      
      setTimeout(() => {
        this.connect().catch(error => {
          console.error('Reconnection failed:', error)
        })
      }, delay)
    } else {
      console.error('Max reconnection attempts reached. Please refresh the page.')
    }
  }

  private handleAlert(alert: WebSocketAlert): void {
    // Log the alert for debugging
    console.log('Received WebSocket alert:', alert)
    
    // Notify all registered handlers
    this.eventHandlers.forEach(handler => {
      try {
        handler(alert)
      } catch (error) {
        console.error('Error in WebSocket event handler:', error)
      }
    })
  }

  onAlert(handler: WebSocketEventHandler): () => void {
    this.eventHandlers.push(handler)
    
    // Return unsubscribe function
    return () => {
      const index = this.eventHandlers.indexOf(handler)
      if (index > -1) {
        this.eventHandlers.splice(index, 1)
      }
    }
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }

  getConnectionState(): string {
    if (!this.ws) return 'disconnected'
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting'
      case WebSocket.OPEN:
        return 'connected'
      case WebSocket.CLOSING:
        return 'closing'
      case WebSocket.CLOSED:
        return 'disconnected'
      default:
        return 'unknown'
    }
  }
}

// Create singleton instance
export const webSocketService = new WebSocketService()

// Auto-connect when service is imported (optional)
// webSocketService.connect().catch(console.error)