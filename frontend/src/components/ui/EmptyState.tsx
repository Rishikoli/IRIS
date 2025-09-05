import React from 'react'

interface EmptyStateProps {
  icon?: React.ReactNode
  title: string
  description?: string
  action?: React.ReactNode
  className?: string
}

const EmptyState: React.FC<EmptyStateProps> = ({ icon, title, description, action, className = '' }) => (
  <div className={`rounded-xl border border-contrast-200 bg-white p-8 text-center ${className}`}>
    {icon && <div className="mx-auto mb-3 h-10 w-10 text-primary-600">{icon}</div>}
    <h3 className="text-sm font-semibold text-contrast-800">{title}</h3>
    {description && <p className="mt-1 text-sm text-contrast-500">{description}</p>}
    {action && <div className="mt-4">{action}</div>}
  </div>
)

export default EmptyState
