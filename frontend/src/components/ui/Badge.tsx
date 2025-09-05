import React from 'react'

type Variant = 'neutral' | 'primary' | 'success' | 'warning' | 'danger'

const VARIANT: Record<Variant, string> = {
  neutral: 'bg-contrast-100 text-contrast-700',
  primary: 'bg-primary-100 text-primary-700',
  success: 'bg-success-100 text-success-700',
  warning: 'bg-warning-100 text-warning-700',
  danger: 'bg-danger-100 text-danger-700',
}

const ROUNDED: Record<'sm' | 'md' | 'full', string> = {
  sm: 'rounded-sm',
  md: 'rounded-md',
  full: 'rounded-full',
}

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: Variant
  rounded?: 'sm' | 'md' | 'full'
}

const Badge: React.FC<BadgeProps> = ({ variant = 'neutral', rounded = 'md', className = '', children, ...rest }) => (
  <span className={`inline-flex items-center px-2 py-0.5 text-xs font-medium ${ROUNDED[rounded]} ${VARIANT[variant]} ${className}`} {...rest}>
    {children}
  </span>
)

export default Badge
