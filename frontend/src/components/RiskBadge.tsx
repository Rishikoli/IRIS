import React from 'react'

interface RiskBadgeProps {
  level: 'Low' | 'Medium' | 'High'
  score: number
  reasons: string[]
  className?: string
}

const RiskBadge: React.FC<RiskBadgeProps> = ({ level, score, reasons, className = '' }) => {
  const getBadgeStyles = () => {
    switch (level) {
      case 'High':
        return {
          container: 'bg-red-50 border-red-200',
          badge: 'bg-red-100 text-red-800 border-red-200',
          icon: 'text-red-500',
          title: 'text-red-900'
        }
      case 'Medium':
        return {
          container: 'bg-yellow-50 border-yellow-200',
          badge: 'bg-yellow-100 text-yellow-800 border-yellow-200',
          icon: 'text-yellow-500',
          title: 'text-yellow-900'
        }
      case 'Low':
        return {
          container: 'bg-green-50 border-green-200',
          badge: 'bg-green-100 text-green-800 border-green-200',
          icon: 'text-green-500',
          title: 'text-green-900'
        }
      default:
        return {
          container: 'bg-gray-50 border-gray-200',
          badge: 'bg-gray-100 text-gray-800 border-gray-200',
          icon: 'text-gray-500',
          title: 'text-dark-primary'
        }
    }
  }

  const getIcon = () => {
    switch (level) {
      case 'High':
        return (
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        )
      case 'Medium':
        return (
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
        )
      case 'Low':
        return (
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
        )
      default:
        return null
    }
  }

  const styles = getBadgeStyles()

  return (
    <div className={`rounded-lg border p-6 ${styles.container} ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={`${styles.icon}`}>
            {getIcon()}
          </div>
          <h3 className={`text-lg font-semibold ${styles.title}`}>
            Risk Level: {level}
          </h3>
        </div>
        <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${styles.badge}`}>
          Score: {score}/100
        </div>
      </div>

      <div className="space-y-3">
        <div>
          <h4 className={`text-sm font-medium ${styles.title} mb-2`}>
            Risk Factors Detected:
          </h4>
          <ul className="space-y-1">
            {reasons.map((reason, index) => (
              <li key={index} className="flex items-start space-x-2">
                <span className={`inline-block w-1.5 h-1.5 rounded-full mt-2 ${styles.icon.replace('text-', 'bg-')}`} />
                <span className="text-sm text-gray-700">{reason}</span>
              </li>
            ))}
          </ul>
        </div>

        {level === 'High' && (
          <div className="mt-4 p-3 bg-red-100 border border-red-200 rounded-md">
            <p className="text-sm text-red-800 font-medium">
              ⚠️ High Risk Warning: This message shows multiple fraud indicators. 
              Exercise extreme caution and verify all information independently.
            </p>
          </div>
        )}

        {level === 'Medium' && (
          <div className="mt-4 p-3 bg-yellow-100 border border-yellow-200 rounded-md">
            <p className="text-sm text-yellow-800 font-medium">
              ⚡ Caution Required: This message contains some risk indicators. 
              Please verify the source and claims before making any investment decisions.
            </p>
          </div>
        )}

        {level === 'Low' && (
          <div className="mt-4 p-3 bg-green-100 border border-green-200 rounded-md">
            <p className="text-sm text-green-800 font-medium">
              ✅ Low Risk: This message appears to be informational, but always 
              do your own research before making investment decisions.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default RiskBadge