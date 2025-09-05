import React, { createContext, useCallback, useContext, useMemo, useState } from 'react'

export type ToastVariant = 'success' | 'error' | 'info' | 'warning'

export interface ToastMessage {
  id: string
  title?: string
  description: string
  variant?: ToastVariant
  durationMs?: number
}

interface ToastContextValue {
  toasts: ToastMessage[]
  addToast: (msg: Omit<ToastMessage, 'id'>) => string
  removeToast: (id: string) => void
  clearToasts: () => void
}

const ToastContext = createContext<ToastContextValue | undefined>(undefined)

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<ToastMessage[]>([])

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  const addToast = useCallback((msg: Omit<ToastMessage, 'id'>) => {
    const id = Math.random().toString(36).slice(2)
    const duration = msg.durationMs ?? 4000
    const toast: ToastMessage = { id, ...msg }
    setToasts((prev) => [...prev, toast])
    if (duration > 0) {
      setTimeout(() => removeToast(id), duration)
    }
    return id
  }, [removeToast])

  const clearToasts = useCallback(() => setToasts([]), [])

  const value = useMemo(() => ({ toasts, addToast, removeToast, clearToasts }), [toasts, addToast, removeToast])

  return (
    <ToastContext.Provider value={value}>
      {children}
    </ToastContext.Provider>
  )
}

export const useToast = () => {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used within ToastProvider')
  return ctx
}
