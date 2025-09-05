import React from 'react'

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  padding?: 'none' | 'sm' | 'md' | 'lg'
  shadow?: 'none' | 'sm' | 'md'
  bordered?: boolean
}

const pad = {
  none: '',
  sm: 'p-3',
  md: 'p-4',
  lg: 'p-6',
}

const shadowMap = {
  none: '',
  sm: 'shadow',
  md: 'shadow-md',
}

export const Card: React.FC<CardProps> = ({
  className = '',
  children,
  padding = 'md',
  shadow = 'md',
  bordered = true,
  ...rest
}) => (
  <div
    className={`rounded-xl overflow-hidden bg-white border ${bordered ? 'border-contrast-200' : 'border-transparent'} ${shadowMap[shadow]} ${pad[padding]} ${className}`}
    {...rest}
  >
    {children}
  </div>
)

export const CardHeader: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ className = '', children, ...rest }) => (
  <div className={`mb-3 flex items-center justify-between ${className}`} {...rest}>
    {children}
  </div>
)

export const CardTitle: React.FC<React.HTMLAttributes<HTMLHeadingElement>> = ({ className = '', children, ...rest }) => (
  <h3 className={`text-base font-semibold text-contrast-800 ${className}`} {...rest}>{children}</h3>
)

export const CardContent: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ className = '', children, ...rest }) => (
  <div className={className} {...rest}>{children}</div>
)

export default Card
