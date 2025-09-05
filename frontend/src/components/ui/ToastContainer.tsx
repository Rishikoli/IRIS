import React from 'react'
import { useToast } from '../../contexts/ToastContext'

const variantStyles: Record<string, string> = {
  success: 'border-green-300 bg-green-50 text-green-900',
  error: 'border-red-300 bg-red-50 text-red-900',
  info: 'border-blue-300 bg-blue-50 text-blue-900',
  warning: 'border-yellow-300 bg-yellow-50 text-yellow-900',
}

const ToastContainer: React.FC = () => {
  const { toasts, removeToast } = useToast()

  return (
    <div className="fixed top-4 right-4 z-[1000] space-y-2">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={`min-w-[260px] max-w-[380px] rounded-lg border shadow-sm px-4 py-3 flex items-start gap-3 ${variantStyles[t.variant ?? 'info']}`}
          role="status"
        >
          <div className="flex-1">
            {t.title && <div className="font-semibold text-sm">{t.title}</div>}
            <div className="text-sm">{t.description}</div>
          </div>
          <button
            aria-label="Close"
            className="text-xs opacity-70 hover:opacity-100"
            onClick={() => removeToast(t.id)}
          >
            ✕
          </button>
        </div>
      ))}
    </div>
  )
}

export default ToastContainer
