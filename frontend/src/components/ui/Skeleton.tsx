import React from 'react'

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  width?: string | number
  height?: string | number
  rounded?: 'sm' | 'md' | 'lg' | 'full'
}

const Skeleton: React.FC<SkeletonProps> = ({ width = '100%', height = 16, rounded = 'md', className = '', style, ...rest }) => (
  <div
    className={`animate-pulse bg-contrast-200 rounded-${rounded} ${className}`}
    style={{ width, height, ...style }}
    {...rest}
  />
)

export default Skeleton
