import React, { useState, useEffect, useRef } from 'react'
import { HeatmapBucket, DataIndicator, multiSourceApi, DataSourceToggle } from '../services/api'
import indiaSvg from '../assets/svg/india.svg?raw'

interface IndiaHeatmapProps {
  data: HeatmapBucket[]
  dimension: 'sector' | 'region'
  onCellClick?: (key: string) => void
  className?: string
  customSvg?: string
}

interface StateData {
  name: string
  code: string
  riskScore: number
  totalCases: number
  highRiskCases: number
  mediumRiskCases: number
  lowRiskCases: number
  path: string
}

const IndiaHeatmap: React.FC<IndiaHeatmapProps> = ({
  data,
  dimension,
  onCellClick,
  className = '',
  customSvg
}) => {
  const svgContainerRef = useRef<HTMLDivElement>(null)
  const [indicators, setIndicators] = useState<DataIndicator[]>([])
  const [sourcesEnabled, setSourcesEnabled] = useState<DataSourceToggle>({
    fmp_enabled: true,
    google_trends_enabled: true,
    economic_times_enabled: true
  })
  const [showOverlays, setShowOverlays] = useState(true)
  const mapScale = 1 // slightly zoomed out

  // Indian states with SVG paths (simplified)
  const indianStates: StateData[] = [
    {
      name: 'Maharashtra',
      code: 'MH',
      riskScore: 0,
      totalCases: 0,
      highRiskCases: 0,
      mediumRiskCases: 0,
      lowRiskCases: 0,
      path: 'M300,250 L350,240 L380,260 L370,300 L320,310 L290,280 Z'
    },
    {
      name: 'Karnataka',
      code: 'KA',
      riskScore: 0,
      totalCases: 0,
      highRiskCases: 0,
      mediumRiskCases: 0,
      lowRiskCases: 0,
      path: 'M280,320 L330,315 L350,340 L340,380 L300,385 L270,360 Z'
    },
    {
      name: 'Tamil Nadu',
      code: 'TN',
      riskScore: 0,
      totalCases: 0,
      highRiskCases: 0,
      mediumRiskCases: 0,
      lowRiskCases: 0,
      path: 'M320,380 L370,375 L390,400 L380,430 L340,435 L310,410 Z'
    },
    {
      name: 'Gujarat',
      code: 'GJ',
      riskScore: 0,
      totalCases: 0,
      highRiskCases: 0,
      mediumRiskCases: 0,
      lowRiskCases: 0,
      path: 'M200,200 L250,195 L270,220 L260,260 L220,265 L190,240 Z'
    },
    {
      name: 'Rajasthan',
      code: 'RJ',
      riskScore: 0,
      totalCases: 0,
      highRiskCases: 0,
      mediumRiskCases: 0,
      lowRiskCases: 0,
      path: 'M220,150 L280,145 L300,180 L290,220 L240,225 L200,190 Z'
    },
    {
      name: 'Uttar Pradesh',
      code: 'UP',
      riskScore: 0,
      totalCases: 0,
      highRiskCases: 0,
      mediumRiskCases: 0,
      lowRiskCases: 0,
      path: 'M300,120 L380,115 L400,140 L390,180 L340,185 L280,160 Z'
    },
    {
      name: 'West Bengal',
      code: 'WB',
      riskScore: 0,
      totalCases: 0,
      highRiskCases: 0,
      mediumRiskCases: 0,
      lowRiskCases: 0,
      path: 'M420,180 L460,175 L480,200 L470,230 L440,235 L410,210 Z'
    },
    {
      name: 'Andhra Pradesh',
      code: 'AP',
      riskScore: 0,
      totalCases: 0,
      highRiskCases: 0,
      mediumRiskCases: 0,
      lowRiskCases: 0,
      path: 'M350,300 L400,295 L420,320 L410,360 L370,365 L340,340 Z'
    },
    {
      name: 'Telangana',
      code: 'TS',
      riskScore: 0,
      totalCases: 0,
      highRiskCases: 0,
      mediumRiskCases: 0,
      lowRiskCases: 0,
      path: 'M330,280 L370,275 L380,300 L370,320 L340,325 L320,300 Z'
    },
    {
      name: 'Kerala',
      code: 'KL',
      riskScore: 0,
      totalCases: 0,
      highRiskCases: 0,
      mediumRiskCases: 0,
      lowRiskCases: 0,
      path: 'M270,380 L300,375 L310,400 L300,430 L280,435 L260,410 Z'
    },
    {
      name: 'Odisha',
      code: 'OR',
      riskScore: 0,
      totalCases: 0,
      highRiskCases: 0,
      mediumRiskCases: 0,
      lowRiskCases: 0,
      path: 'M380,220 L420,215 L440,240 L430,270 L400,275 L370,250 Z'
    },
    {
      name: 'Madhya Pradesh',
      code: 'MP',
      riskScore: 0,
      totalCases: 0,
      highRiskCases: 0,
      mediumRiskCases: 0,
      lowRiskCases: 0,
      path: 'M280,200 L340,195 L360,220 L350,260 L300,265 L260,240 Z'
    },
    {
      name: 'Punjab',
      code: 'PB',
      riskScore: 0,
      totalCases: 0,
      highRiskCases: 0,
      mediumRiskCases: 0,
      lowRiskCases: 0,
      path: 'M280,80 L320,75 L340,100 L330,130 L300,135 L270,110 Z'
    },
    {
      name: 'Haryana',
      code: 'HR',
      riskScore: 0,
      totalCases: 0,
      highRiskCases: 0,
      mediumRiskCases: 0,
      lowRiskCases: 0,
      path: 'M300,100 L340,95 L360,120 L350,150 L320,155 L290,130 Z'
    },
    {
      name: 'Delhi',
      code: 'DL',
      riskScore: 0,
      totalCases: 0,
      highRiskCases: 0,
      mediumRiskCases: 0,
      lowRiskCases: 0,
      path: 'M320,120 L330,115 L340,125 L335,135 L325,140 L315,130 Z'
    }
  ]

  // Process data to map to Indian states
  const processedStates = indianStates.map(state => {
    const stateData = data.find(item => 
      item.key.toLowerCase().includes(state.name.toLowerCase()) ||
      item.key.toLowerCase().includes(state.code.toLowerCase()) ||
      state.name.toLowerCase().includes(item.key.toLowerCase())
    )

    if (stateData) {
      return {
        ...state,
        riskScore: stateData.risk_score,
        totalCases: stateData.total_count,
        highRiskCases: stateData.high_risk_count,
        mediumRiskCases: stateData.medium_risk_count,
        lowRiskCases: stateData.low_risk_count
      }
    }

    // Generate mock data for demonstration
    const mockRiskScore = Math.random() * 100
    const mockTotalCases = Math.floor(Math.random() * 50) + 1
    
    return {
      ...state,
      riskScore: mockRiskScore,
      totalCases: mockTotalCases,
      highRiskCases: Math.floor(mockTotalCases * (mockRiskScore > 70 ? 0.6 : mockRiskScore > 40 ? 0.3 : 0.1)),
      mediumRiskCases: Math.floor(mockTotalCases * (mockRiskScore > 70 ? 0.3 : mockRiskScore > 40 ? 0.5 : 0.3)),
      lowRiskCases: Math.floor(mockTotalCases * (mockRiskScore > 70 ? 0.1 : mockRiskScore > 40 ? 0.2 : 0.6))
    }
  })

  // Get color based on risk score
  const getStateColor = (riskScore: number) => {
    if (riskScore >= 80) return '#dc2626' // red-600
    if (riskScore >= 60) return '#ea580c' // orange-600
    if (riskScore >= 40) return '#d97706' // amber-600
    if (riskScore >= 20) return '#ca8a04' // yellow-600
    return '#16a34a' // green-600
  }

  // Build a lookup by lowercase name for quick risk/color retrieval
  const riskByName = React.useMemo(() => {
    const map = new Map<string, number>()
    for (const s of processedStates) {
      map.set(s.name.toLowerCase(), s.riskScore)
    }
    return map
  }, [processedStates])

  // Helper to (re)color paths based on current data
  const recolorPaths = React.useCallback(() => {
    const root = svgContainerRef.current
    if (!root) return
    const paths = root.querySelectorAll('svg path[id], svg path[name]')
    paths.forEach((p) => {
      const el = p as SVGPathElement
      const stateName = (el.getAttribute('name') || el.getAttribute('id') || '').trim()
      const risk = riskByName.get(stateName.toLowerCase())
      if (risk != null) {
        el.style.fill = getStateColor(risk)
      } else {
        // fallback to a neutral green similar to asset default but toned
        el.style.fill = '#9ec6a6'
      }
      // Ensure strokes remain visible
      el.style.stroke = el.style.stroke || '#ffffff'
      el.style.strokeWidth = el.style.strokeWidth || '.5'
    })
  }, [riskByName])

  // Attach interaction handlers when SVG content changes
  useEffect(() => {
    const root = svgContainerRef.current
    if (!root) return

    const paths = Array.from(root.querySelectorAll('svg path[id], svg path[name]')) as SVGPathElement[]
    const cleanups: Array<() => void> = []

    paths.forEach((el) => {
      // cursor and basic accessibility
      el.style.cursor = 'pointer'
      const name = (el.getAttribute('name') || el.getAttribute('id') || 'Region').trim()

      // title tooltip for accessibility (avoid duplicating titles)
      if (!el.querySelector('title')) {
        const t = document.createElementNS('http://www.w3.org/2000/svg', 'title')
        t.textContent = name
        el.appendChild(t)
      }

      const enter = () => {
        el.dataset.originalOpacity = el.style.opacity || ''
        el.dataset.originalStrokeWidth = el.style.strokeWidth || ''
        el.style.opacity = '0.9'
        el.style.strokeWidth = '1.5'
      }
      const leave = () => {
        el.style.opacity = el.dataset.originalOpacity || ''
        el.style.strokeWidth = el.dataset.originalStrokeWidth || '.5'
      }
      const click = () => {
        if (onCellClick) {
          onCellClick(name)
        }
      }

      el.addEventListener('mouseenter', enter)
      el.addEventListener('mouseleave', leave)
      el.addEventListener('click', click)
      cleanups.push(() => {
        el.removeEventListener('mouseenter', enter)
        el.removeEventListener('mouseleave', leave)
        el.removeEventListener('click', click)
      })
    })

    // Initial color pass
    recolorPaths()

    return () => {
      cleanups.forEach((fn) => fn())
    }
    // Rebind when the underlying SVG string changes
  }, [customSvg, recolorPaths, onCellClick])

  // Recolor when data changes
  useEffect(() => {
    recolorPaths()
  }, [recolorPaths])

  // Apply visual scale to the injected SVG to "zoom out" a bit
  useEffect(() => {
    const root = svgContainerRef.current
    if (!root) return
    const svg = root.querySelector('svg') as SVGSVGElement | null
    if (!svg) return
    svg.style.transformOrigin = 'center center'
    svg.style.transform = `scale(${mapScale})`
    svg.style.width = '100%'
    svg.style.height = '100%'
    // Ensure viewbox scaling behaves predictably
    if (!svg.getAttribute('preserveAspectRatio')) {
      svg.setAttribute('preserveAspectRatio', 'xMidYMid meet')
    }
  }, [mapScale, customSvg])

  // Fetch multi-source indicators
  useEffect(() => {
    const fetchIndicators = async () => {
      try {
        const response = await multiSourceApi.getIndicators({
          min_relevance: 40
        })
        setIndicators(response.data.indicators)
      } catch (error) {
        console.error('Error fetching multi-source indicators:', error)
      }
    }

    if (showOverlays) {
      fetchIndicators()
    }
  }, [showOverlays])

  // Handle source toggle
  const handleSourceToggle = async (source: keyof DataSourceToggle) => {
    const newSources = {
      ...sourcesEnabled,
      [source]: !sourcesEnabled[source]
    }
    setSourcesEnabled(newSources)
    
    try {
      await multiSourceApi.refreshData(newSources)
    } catch (error) {
      console.error('Error refreshing data sources:', error)
    }
  }

  return (
    <div className={`bg-white dark:bg-dark-secondary rounded-lg shadow-md p-6 border border-gray-200 dark:border-dark-border ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-semibold text-gray-900 dark:text-dark-text">
          India Fraud Risk Heatmap - {dimension === 'sector' ? 'By Sector' : 'By Region'}
        </h3>
        
        {/* Multi-Source Data Controls */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-sm">
            <span className="text-gray-600 dark:text-dark-muted">Data Sources:</span>
            <button
              onClick={() => handleSourceToggle('fmp_enabled')}
              className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                sourcesEnabled.fmp_enabled
                  ? 'bg-blue-100 text-blue-800 border border-blue-200'
                  : 'bg-gray-100 text-gray-500 border border-gray-200'
              }`}
            >
              📈 FMP
            </button>
            <button
              onClick={() => handleSourceToggle('google_trends_enabled')}
              className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                sourcesEnabled.google_trends_enabled
                  ? 'bg-red-100 text-red-800 border border-red-200'
                  : 'bg-gray-100 text-gray-500 border border-gray-200'
              }`}
            >
              🔍 Trends
            </button>
            <button
              onClick={() => handleSourceToggle('economic_times_enabled')}
              className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                sourcesEnabled.economic_times_enabled
                  ? 'bg-green-100 text-green-800 border border-green-200'
                  : 'bg-gray-100 text-gray-500 border border-gray-200'
              }`}
            >
              📰 News
            </button>
            {showOverlays && (
              <span className="ml-2 text-gray-500">Indicators: {indicators.length}</span>
            )}
          </div>

          <button
            onClick={() => setShowOverlays(!showOverlays)}
            className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
              showOverlays
                ? 'bg-purple-100 text-purple-800 border border-purple-200'
                : 'bg-gray-100 text-gray-600 border border-gray-200'
            }`}
          >
            {showOverlays ? '🔍 Hide Overlays' : '🔍 Show Overlays'}
          </button>
        </div>
      </div>

      {/* Risk Level Legend */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4 text-sm">
          <span className="text-gray-600">Risk Level:</span>
          <div className="flex items-center space-x-2">
            <div className="flex items-center space-x-1">
              <div className="w-4 h-4 bg-green-600 rounded"></div>
              <span>Low (0-20)</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-4 h-4 bg-yellow-600 rounded"></div>
              <span>Medium (20-60)</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-4 h-4 bg-red-600 rounded"></div>
              <span>High (60+)</span>
            </div>
          </div>
        </div>
      </div>

      {/* India Map SVG (from asset or custom) */}
      <div className="relative bg-gray-50 rounded-lg p-4 mb-6">
        <div
          ref={svgContainerRef}
          className="w-full h-96 mx-auto overflow-hidden"
          style={{ maxHeight: '400px' }}
          dangerouslySetInnerHTML={{ __html: customSvg || indiaSvg }}
        />
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-gray-200">
        <div className="text-center">
          <div className="text-2xl font-bold text-dark-primary">
            {processedStates.reduce((sum, state) => sum + state.totalCases, 0)}
          </div>
          <div className="text-sm text-gray-600">Total Cases</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-red-600">
            {processedStates.filter(state => state.riskScore >= 70).length}
          </div>
          <div className="text-sm text-gray-600">High Risk States</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-yellow-600">
            {processedStates.filter(state => state.riskScore >= 40 && state.riskScore < 70).length}
          </div>
          <div className="text-sm text-gray-600">Medium Risk States</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-600">
            {processedStates.length > 0 
              ? (processedStates.reduce((sum, state) => sum + state.riskScore, 0) / processedStates.length).toFixed(1)
              : '0.0'
            }
          </div>
          <div className="text-sm text-gray-600">Avg Risk Score</div>
        </div>
      </div>

      {/* Interactive Instructions */}
      <div className="mt-4 p-3 bg-blue-50 rounded-lg">
        <p className="text-sm text-blue-800">
          💡 <strong>Interactive Features:</strong> Hover over states for details, click to drill down into specific state data. 
          Map shows fraud risk distribution across Indian states.
        </p>
      </div>
    </div>
  )
}

export default IndiaHeatmap
