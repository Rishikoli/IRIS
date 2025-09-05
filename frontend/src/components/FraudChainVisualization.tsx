  import React, { useEffect, useRef, useState } from 'react'

import cytoscape, { Core, ElementDefinition } from 'cytoscape'
import fcose from 'cytoscape-fcose'
import dagre from 'cytoscape-dagre'
import { FraudChain, FraudChainNode, FraudChainEdge } from '../services/api'

// Register layouts
cytoscape.use(fcose as any)
cytoscape.use(dagre as any)

interface FraudChainVisualizationProps {
  chain: FraudChain
  onNodeClick?: (node: FraudChainNode) => void
  onEdgeClick?: (edge: FraudChainEdge) => void
  className?: string
}

type LayoutMode = 'fcose' | 'hierarchical'

const FraudChainVisualization: React.FC<FraudChainVisualizationProps> = ({
  chain,
  onNodeClick,
  onEdgeClick,
  className = ''
}) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const cyRef = useRef<Core | null>(null)
  const [zoomLevel, setZoomLevel] = useState(100)
  const [layoutMode, setLayoutMode] = useState<LayoutMode>('fcose')

  // Initialize Cytoscape once
  useEffect(() => {
    if (!containerRef.current) return
    const cy = cytoscape({
      container: containerRef.current,
      style: [
        // Nodes base
        {
          selector: 'node',
          style: {
            'background-color': '#6b7280',
            'label': 'data(label)',
            'color': '#e5e7eb',
            'font-size': '10px',
            'text-wrap': 'wrap',
            'text-max-width': '100px',
            'text-valign': 'bottom',
            'text-halign': 'center',
            'text-margin-y': 6,
            'border-width': 2,
            'border-color': '#e5e7eb',
            'width': 40,
            'height': 40,
          }
        },
        // Node type colors and sizes
        { selector: 'node.tip', style: { 'background-color': '#000000', 'width': 50, 'height': 50 } },
        { selector: 'node.assessment', style: { 'background-color': '#ef4444', 'width': 56, 'height': 56 } },
        { selector: 'node.document', style: { 'background-color': '#10b981' } },
        { selector: 'node.stock', style: { 'background-color': '#f59e0b' } },
        { selector: 'node.complaint', style: { 'background-color': '#8b5cf6' } },
        { selector: 'node.advisor', style: { 'background-color': '#06b6d4' } },
        // Selected node
        { selector: 'node:selected', style: { 'border-color': '#ff6b35', 'border-width': 3 } },

        // Edges
        {
          selector: 'edge',
          style: {
            'line-color': '#6b7280',
            'width': 2,
            'opacity': 0.85,
            'curve-style': 'bezier',
            'target-arrow-shape': 'triangle',
            'target-arrow-color': '#6b7280',
            'label': 'data(relLabel)',
            'font-size': '9px',
            'color': '#d1d5db',
            'text-background-color': 'rgba(17,24,39,0.9)',
            'text-background-opacity': 1,
            'text-background-padding': 2,
            'text-border-color': 'rgba(17,24,39,0.9)',
            'text-border-width': 1,
            'text-border-opacity': 1,
            'text-rotation': 'autorotate',
          }
        },
        { selector: 'edge.leads_to', style: { 'line-color': '#3b82f6', 'target-arrow-color': '#3b82f6', 'width': 3 } },
        { selector: 'edge.references', style: { 'line-color': '#10b981', 'target-arrow-color': '#10b981' } },
        { selector: 'edge.mentions', style: { 'line-color': '#f59e0b', 'target-arrow-color': '#f59e0b' } },
        { selector: 'edge.involves', style: { 'line-color': '#ef4444', 'target-arrow-color': '#ef4444' } },
        { selector: 'edge.similar_pattern', style: { 'line-color': '#8b5cf6', 'target-arrow-color': '#8b5cf6' } },
        { selector: 'edge.escalates_to', style: { 'line-color': '#dc2626', 'target-arrow-color': '#dc2626' } },
        { selector: 'edge:selected', style: { 'width': 4 } },
      ] as any,
      wheelSensitivity: 0.2,
      pixelRatio: 1,
    })

    cy.on('select', 'node', (evt) => {
      const n = evt.target
      const data = n.data('_raw') as FraudChainNode
      onNodeClick?.(data)
    })
    cy.on('unselect', 'node', () => {})

    cy.on('select', 'edge', (evt) => {
      const e = evt.target
      const data = e.data('_raw') as FraudChainEdge
      onEdgeClick?.(data)
    })
    cy.on('unselect', 'edge', () => {})

    cy.on('zoom', () => setZoomLevel(Math.round(cy.zoom() * 100)))

    cyRef.current = cy
    return () => {
      cy.destroy()
      cyRef.current = null
    }
  }, [onNodeClick, onEdgeClick])

  // Update elements whenever chain changes
  useEffect(() => {
    const cy = cyRef.current
    if (!cy) return

    // Build elements
    const nodeElems: ElementDefinition[] = chain.nodes.map((n) => ({
      group: 'nodes',
      data: {
        id: n.id,
        label: n.label || n.node_type,
        _raw: n,
      },
      position: n.position_x && n.position_y ? { x: n.position_x, y: n.position_y } : undefined,
      classes: n.node_type,
    }))

    const edgeElems: ElementDefinition[] = chain.edges.map((e) => ({
      group: 'edges',
      data: {
        id: e.id,
        source: e.from_node_id,
        target: e.to_node_id,
        relLabel: (e.relationship_type || '').replace('_', ' '),
        _raw: e,
      },
      classes: e.relationship_type,
    }))

    cy.elements().remove()
    cy.add([...nodeElems, ...edgeElems])
    cy.fit(undefined, 50)

    runLayout()
  }, [chain])

  // Re-run layout when mode changes
  useEffect(() => {
    runLayout()
  }, [layoutMode])

  const runLayout = () => {
    const cy = cyRef.current
    if (!cy) return
    if (layoutMode === 'fcose') {
      cy.layout({
        name: 'fcose',
        animate: true,
        animationDuration: 400,
        quality: 'default',
        randomize: true,
        nodeSeparation: 120,
        nodeDimensionsIncludeLabels: true,
        idealEdgeLength: 140,
      } as any).run()
    } else {
      cy.layout({
        name: 'dagre',
        rankDir: 'TB',
        nodeSep: 60,
        edgeSep: 20,
        rankSep: 100,
        animate: true,
      } as any).run()
    }
  }

  // Utilities retained for legend only (styles moved to Cytoscape stylesheet)

  const handleZoomIn = () => {
    const cy = cyRef.current
    if (!cy) return
    cy.zoom({ level: cy.zoom() * 1.2, renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 } })
  }

  const handleZoomOut = () => {
    const cy = cyRef.current
    if (!cy) return
    cy.zoom({ level: cy.zoom() / 1.2, renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 } })
  }

  const handleResetZoom = () => {
    const cy = cyRef.current
    if (!cy) return
    cy.fit(undefined, 50)
    setZoomLevel(Math.round(cy.zoom() * 100))
  }

  const handleExportPNG = async () => {
    const cy = cyRef.current
    if (!cy) return
    const png64 = cy.png({ full: true, bg: '#0b1220', scale: 2 })
    const a = document.createElement('a')
    a.href = png64
    a.download = 'fraud_chain.png'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  }

  return (
    <div ref={containerRef} className={`fraud-chain-visualization relative ${className}`}>
      {/* Controls */}
      <div className="absolute top-4 right-4 z-10 flex flex-col gap-2">
        <button
          onClick={handleZoomIn}
          className="bg-dark-800 shadow-lg rounded-md p-2 hover:bg-dark-700 transition-colors border border-dark-primary text-dark-primary"
          title="Zoom In"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
        </button>
        <button
          onClick={handleZoomOut}
          className="bg-dark-800 shadow-lg rounded-md p-2 hover:bg-dark-700 transition-colors border border-dark-primary text-dark-primary"
          title="Zoom Out"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 12H6" />
          </svg>
        </button>
        <button
          onClick={handleResetZoom}
          className="bg-dark-800 shadow-lg rounded-md p-2 hover:bg-dark-700 transition-colors border border-dark-primary text-dark-primary"
          title="Reset Zoom"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
        {/* Layout toggle */}
        <div className="bg-dark-800 shadow-lg rounded-md p-1 border border-dark-primary flex gap-1" title="Layout">
          <button
            className={`px-2 py-1 rounded ${layoutMode === 'fcose' ? 'bg-primary-600 text-white' : 'hover:bg-dark-700 text-dark-primary'}`}
            onClick={() => setLayoutMode('fcose')}
          >
            fCoSE
          </button>
          <button
            className={`px-2 py-1 rounded ${layoutMode === 'hierarchical' ? 'bg-primary-600 text-white' : 'hover:bg-dark-700 text-dark-primary'}`}
            onClick={() => setLayoutMode('hierarchical')}
          >
            Hierarchy
          </button>
        </div>
        <button
          onClick={handleExportPNG}
          className="bg-primary-600 shadow-lg rounded-md p-2 hover:bg-primary-700 transition-colors text-white"
          title="Export PNG"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M7 10l5 5m0 0l5-5m-5 5V4" />
          </svg>
        </button>
      </div>

      {/* Zoom level indicator */}
      <div className="absolute top-4 left-4 z-10 bg-dark-800 shadow-lg rounded-md px-3 py-1 text-sm border border-dark-primary text-dark-primary">
        Zoom: {zoomLevel}%
      </div>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 z-10 bg-dark-800 shadow-lg rounded-md p-3 border border-dark-primary">
        <h4 className="font-semibold text-sm mb-2 text-dark-primary">Legend</h4>
        <div className="grid grid-cols-2 gap-2 text-xs text-dark-secondary">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-blue-500"></div>
            <span>Tip</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-red-500"></div>
            <span>Assessment</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-green-500"></div>
            <span>Document</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-amber-500"></div>
            <span>Stock</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-purple-500"></div>
            <span>Complaint</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-cyan-500"></div>
            <span>Advisor</span>
          </div>
        </div>
      </div>

      {/* Cytoscape container */}
      <div
        ref={containerRef}
        className="w-full h-full border border-dark-primary rounded-lg bg-dark-950"
        style={{ minHeight: '600px' }}
      />
    </div>
  )
}

export default FraudChainVisualization