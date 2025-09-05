import { useState, useEffect, useRef } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Menu, X, Shield, BarChart3, TrendingUp, FileSearch } from 'lucide-react'
import ThemeToggle from './ThemeToggle'
import NotificationPanel from './NotificationPanel'
import { useWebSocket } from '../hooks/useWebSocket'
import { whaleLogo } from '../assets'
import '../assets/fonts/merchant-black.css'

const NavBar = () => {
  const [isOpen, setIsOpen] = useState(false)
  const location = useLocation()
  const navRef = useRef<HTMLElement>(null)

  // WebSocket for real-time notifications
  const {
    alerts,
    isConnected,
    connectionState,
    connect,
    clearAlerts,
    markAsRead,
    unreadCount
  } = useWebSocket()

  // Auto-connect to WebSocket when component mounts
  useEffect(() => {
    connect().catch(console.error)
  }, [])

  // Close mobile menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (navRef.current && !navRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  // Close mobile menu when route changes
  useEffect(() => {
    setIsOpen(false)
  }, [location.pathname])

  const navItems = [
    { label: 'Home', path: '/', icon: Shield },
    { label: 'Dashboard', path: '/dashboard', icon: BarChart3 },
    { label: 'Analytics', path: '/analytics', icon: TrendingUp },
    { label: 'Investigation', path: '/investigation', icon: FileSearch },
  ]

  // Development/demo navigation items (available via direct URL)
  // const devNavItems = [
  //   { label: 'WebSocket Test', path: '/websocket-test', icon: Shield },
  // ]

  const isActive = (path: string) => location.pathname === path

  return (
    <nav ref={navRef} className="bg-white dark:bg-dark-secondary shadow-lg border-b border-gray-200 dark:border-dark-border transition-colors">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center py-1/4">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3">
            <img
              src={whaleLogo}
              alt="IRIS Logo"
              className="h-20 w-20 object-contain"
            />
            <span className="text-xl merchant-black text-gray-900 dark:text-dark-text">IRIS</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-6">
            <div className="flex space-x-6">
              {navItems.map((item) => {
                const Icon = item.icon
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${isActive(item.path)
                        ? 'bg-blue-100 dark:bg-dark-hover text-blue-700 dark:text-dark-accent border border-blue-200 dark:border-dark-accent/30'
                        : 'text-gray-600 dark:text-dark-muted hover:text-gray-900 dark:hover:text-dark-text hover:bg-gray-100 dark:hover:bg-dark-hover'
                      }`}
                  >
                    <Icon className="h-4 w-4" />
                    <span>{item.label}</span>
                  </Link>
                )
              })}
            </div>

            {/* Notifications and Theme Toggle */}
            <div className="flex items-center space-x-2">
              <NotificationPanel
                alerts={alerts}
                isConnected={isConnected}
                connectionState={connectionState}
                onMarkAsRead={markAsRead}
                onClearAll={clearAlerts}
                unreadCount={unreadCount}
              />
              <ThemeToggle />
            </div>
          </div>

          {/* Mobile menu button, notifications and theme toggle */}
          <div className="md:hidden flex items-center space-x-2">
            <NotificationPanel
              alerts={alerts}
              isConnected={isConnected}
              connectionState={connectionState}
              onMarkAsRead={markAsRead}
              onClearAll={clearAlerts}
              unreadCount={unreadCount}
            />
            <ThemeToggle />
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="text-gray-600 dark:text-dark-muted hover:text-gray-900 dark:hover:text-dark-text focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-dark-accent focus:ring-offset-2 focus:ring-offset-white dark:focus:ring-offset-dark-secondary rounded-md p-2"
              aria-expanded={isOpen}
              aria-label="Toggle navigation menu"
            >
              {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        <div className={`md:hidden transition-all duration-300 ease-in-out ${isOpen ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0 overflow-hidden'
          }`}>
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 border-t border-gray-200 dark:border-dark-border">
            {navItems.map((item) => {
              const Icon = item.icon
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-md text-base font-medium transition-colors ${isActive(item.path)
                      ? 'bg-blue-100 dark:bg-dark-hover text-blue-700 dark:text-dark-accent border border-blue-200 dark:border-dark-accent/30'
                      : 'text-gray-600 dark:text-dark-muted hover:text-gray-900 dark:hover:text-dark-text hover:bg-gray-100 dark:hover:bg-dark-hover'
                    }`}
                  onClick={() => setIsOpen(false)}
                >
                  <Icon className="h-5 w-5" />
                  <span>{item.label}</span>
                </Link>
              )
            })}
          </div>
        </div>
      </div>
    </nav>
  )
}

export default NavBar