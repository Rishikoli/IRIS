import React from 'react'

interface ToolbarProps extends React.HTMLAttributes<HTMLDivElement> {
  dense?: boolean
}

const Toolbar: React.FC<ToolbarProps> = ({ dense = false, className = '', children, ...rest }) => (
  <div
    className={`flex items-center justify-between gap-2 ${dense ? 'p-2' : 'p-3'} rounded-lg bg-contrast-50 border border-contrast-200 ${className}`}
    {...rest}
  >
    {children}
  </div>
)

export default Toolbar
