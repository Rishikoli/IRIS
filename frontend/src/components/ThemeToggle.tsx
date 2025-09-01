import React from 'react'
import { useTheme } from '../contexts/ThemeContext'

const ThemeToggle: React.FC = () => {
  const { theme, toggleTheme } = useTheme()

  return (
    <button
      onClick={toggleTheme}
      className="relative inline-flex h-8 w-14 items-center justify-center rounded-full bg-gray-200 transition-colors focus:outline-none focus:ring-2 focus:ring-dark-accent focus:ring-offset-2 dark:bg-dark-secondary dark:focus:ring-offset-dark-primary"
      aria-label="Toggle theme"
    >
      <span className="sr-only">Toggle theme</span>
      
      {/* Toggle background */}
      <span
        className={`absolute inset-0 rounded-full transition-colors ${
          theme === 'dark' 
            ? 'bg-dark-secondary border border-dark-border' 
            : 'bg-gray-200'
        }`}
      />
      
      {/* Toggle slider */}
      <span
        className={`relative inline-block h-6 w-6 transform rounded-full transition-transform ${
          theme === 'dark'
            ? 'translate-x-3 bg-dark-accent'
            : '-translate-x-3 bg-white shadow-sm'
        }`}
      >
        {/* Icon */}
        <span className="absolute inset-0 flex items-center justify-center">
          {theme === 'dark' ? (
            <svg className="h-3 w-3 text-dark-primary" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
            </svg>
          ) : (
            <svg className="h-3 w-3 text-gray-600" fill="currentColor" viewBox="0 0 20 20">
              <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
            </svg>
          )}
        </span>
      </span>
    </button>
  )
}

export default ThemeToggle