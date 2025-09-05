import React, { useEffect, useMemo, useRef, useState } from 'react'
import cytoscape, { Core, ElementDefinition } from 'cytoscape'
import CytoscapeComponent from 'react-cytoscapejs'
import fcose from 'cytoscape-fcose'
import dagre from 'cytoscape-dagre'
import { FraudChain, FraudChainNode, FraudChainEdge } from '../services/api'

// Register layouts
cytoscape.use(fcose as any)
cytoscape.use(dagre as any)

interface Props {
  chain: FraudChain
  chains?: FraudChain[]
  onNodeClick?: (node: FraudChainNode) => void
  onEdgeClick?: (edge: FraudChainEdge) => void
  className?: string
  layout?: 'fcose' | 'dagre'
  enableControls?: boolean
  // New: highlight and focus controls
  nodeHighlightQuery?: string
  focusOnHighlight?: boolean
  // New: highlight nodes by reference IDs (e.g., from backend search results)
  nodeHighlightIds?: string[]
}

const typeColor: Record<string, string> = {
  tip: '#000000',
  assessment: '#ef4444',
  document: '#10b981',
  stock: '#f59e0b',
  complaint: '#8b5cf6',
  advisor: '#06b6d4',
}

const FraudChainGraph: React.FC<Props> = ({ chain, chains, onNodeClick, onEdgeClick, className = '', layout = 'fcose', enableControls = true, nodeHighlightQuery, focusOnHighlight = false, nodeHighlightIds }) => {
  const cyRef = useRef<Core | null>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const [dimensions, setDimensions] = useState<{ width: number; height: number }>({ width: 800, height: 600 })
  const [currentLayout, setCurrentLayout] = useState<'fcose' | 'dagre'>(layout)
  const [edgeTip, setEdgeTip] = useState<null | {
    edgeId: string
    x: number
    y: number
    relation: string
    confidence?: number
    sourceLabel: string
    targetLabel: string
  }>(null)

  useEffect(() => {
    const resize = () => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect()
        setDimensions({ width: Math.max(600, rect.width), height: Math.max(500, rect.height) })
      }
    }
    resize()
    window.addEventListener('resize', resize)
    return () => {
      window.removeEventListener('resize', resize)
    }
  }, [])

  // Highlight nodes based on nodeHighlightQuery or nodeHighlightIds
  useEffect(() => {
    const cy = cyRef.current
    if (!cy) return

    // Clear previous classes
    cy.nodes().removeClass('matched')
    cy.nodes().removeClass('dimmed')

    let matches = cy.collection()
    const ids = (nodeHighlightIds || []).map((v) => v.toLowerCase())
    if (ids.length > 0) {
      matches = cy.nodes().filter((n) => {
        const raw: FraudChainNode = n.data('raw')
        const refId = (raw?.reference_id || '').toString().toLowerCase()
        return ids.includes(refId)
      })
    } else {
      const q = (nodeHighlightQuery || '').trim().toLowerCase()
      if (!q) return
      matches = cy.nodes().filter((n) => {
        const raw: FraudChainNode = n.data('raw')
        const label = (n.data('label') || '').toString().toLowerCase()
        const type = (n.data('type') || '').toString().toLowerCase()
        const refId = (raw?.reference_id || '').toString().toLowerCase()
        let meta = ''
        try {
          const md = (raw?.metadata || {}) as any
          const ref = md.reference_data || {}
          meta = JSON.stringify({ ...md, reference_data: ref }).toLowerCase()
        } catch {
          meta = ''
        }
        return (
          label.includes(q) ||
          type.includes(q) ||
          refId.includes(q) ||
          meta.includes(q)
        )
      })
    }

    matches.addClass('matched')
    const unmatched = cy.nodes().difference(matches)
    unmatched.addClass('dimmed')

    if (focusOnHighlight && matches.length > 0) {
      try {
        cy.animate({ fit: { eles: matches, padding: 100 } }, { duration: 350 })
      } catch {
        cy.fit(matches, 100)
      }
    }
  }, [nodeHighlightQuery, focusOnHighlight, nodeHighlightIds])

  const elements = useMemo<ElementDefinition[]>(() => {
    const sourceChains = chains && chains.length > 0 ? chains : [chain]

    const nodes: ElementDefinition[] = sourceChains.flatMap((c) => c.nodes.map(n => ({
      data: {
        id: (chains && chains.length > 0) ? `${c.id}:${n.id}` : n.id,
        label: n.label || n.node_type,
        type: n.node_type,
        raw: n,
      },
      position: (n.position_x != null && n.position_y != null) ? { x: n.position_x!, y: n.position_y! } : undefined,
    })))

    const edges: ElementDefinition[] = sourceChains.flatMap((c) => c.edges.map(e => ({
      data: {
        id: (chains && chains.length > 0) ? `${c.id}:${e.id}` : e.id,
        source: (chains && chains.length > 0) ? `${c.id}:${e.from_node_id}` : e.from_node_id,
        target: (chains && chains.length > 0) ? `${c.id}:${e.to_node_id}` : e.to_node_id,
        label: e.relationship_type.replace('_', ' '),
        type: e.relationship_type,
        confidence: e.confidence,
        raw: e,
      },
    })))

    return [...nodes, ...edges]
  }, [chain])

  const stylesheet = useMemo(() => [
    {
      selector: 'node',
      style: {
        'background-color': (ele: any) => typeColor[ele.data('type')] || '#6b7280',
        'label': 'data(label)',
        'color': '#e5e7eb',
        'font-size': 11,
        'min-zoomed-font-size': 8,
        'text-wrap': 'wrap',
        'text-max-width': 120,
        'text-valign': 'bottom',
        'text-halign': 'center',
        'text-margin-y': 8,
        'border-width': 2,
        'border-color': '#e5e7eb',
        'width': (ele: any) => (ele.data('type') === 'assessment' ? 56 : 48),
        'height': (ele: any) => (ele.data('type') === 'assessment' ? 56 : 48),
        'overlay-opacity': 0,
        'shadow-blur': 12,
        'shadow-color': 'rgba(0,0,0,0.45)',
        'shadow-offset-x': 0,
        'shadow-offset-y': 2,
      },
    },
    // Stagger per relationship type to avoid overlapping parallel edges
    { selector: 'edge[type = "leads_to"]', style: { 'control-point-distances': 60, 'control-point-weights': 0.4 } },
    { selector: 'edge[type = "references"]', style: { 'control-point-distances': -60, 'control-point-weights': 0.6 } },
    { selector: 'edge[type = "mentions"]', style: { 'control-point-distances': 90, 'control-point-weights': 0.3 } },
    { selector: 'edge[type = "involves"]', style: { 'control-point-distances': -90, 'control-point-weights': 0.7 } },
    { selector: 'edge[type = "similar_pattern"]', style: { 'control-point-distances': 120, 'control-point-weights': 0.25 } },
    { selector: 'edge[type = "escalates_to"]', style: { 'control-point-distances': -120, 'control-point-weights': 0.75 } },
    {
      selector: 'node[type = "tip"]',
      style: {
        'font-family': 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace',
        'color': '#000000',
      },
    },
    {
      selector: 'node[type = "assessment"]',
      style: {
        'color': '#000000',
      },
    },
    {
      selector: 'edge',
      style: {
        'curve-style': 'bezier',
        'control-point-step-size': 50,
        'control-point-distances': 50,
        'control-point-weights': 0.5,
        'line-color': (ele: any) => edgeColor(ele.data('type')),
        'target-arrow-color': (ele: any) => edgeColor(ele.data('type')),
        'width': (ele: any) => Math.max(1.5, ele.data('confidence') / 25),
        'opacity': 0.9,
        'target-arrow-shape': 'triangle',
        'arrow-scale': 1,
        'label': 'data(label)',
        'font-size': 9,
        'min-zoomed-font-size': 8,
        'text-rotation': 'autorotate',
        'text-margin-y': -6,
        'text-margin-x': 6,
        'text-background-opacity': 0.9,
        'text-background-color': 'rgba(17,24,39,0.9)',
        'text-background-padding': 2,
        'text-border-width': 1,
        'text-border-color': '#1f2937',
        'text-border-opacity': 1,
        'color': '#e5e7eb',
      },
    },
    {
      selector: '.selected',
      style: {
        'border-color': '#ff6b35',
        'border-width': 3,
      },
    },
    {
      selector: '.matched',
      style: {
        'border-color': '#22d3ee',
        'border-width': 4,
        'shadow-blur': 18,
        'shadow-color': 'rgba(34,211,238,0.7)'
      }
    },
    {
      selector: '.dimmed',
      style: {
        'opacity': 0.2
      }
    },
  ], [])

  const layoutOptions = useMemo(() => {
    if (currentLayout === 'dagre') {
      return { name: 'dagre', rankDir: 'LR', spacingFactor: 1.6, nodeSep: 90, rankSep: 140, edgeSep: 60, fit: true, animate: true }
    }
    // default: fcose (force-directed)
    return {
      name: 'fcose',
      quality: 'default',
      animate: true,
      randomize: false,
      fit: true,
      nodeDimensionsIncludeLabels: true,
      packComponents: true,
      nodeSeparation: 180,
      nodeRepulsion: 20000,
      idealEdgeLength: 260,
      gravity: 0.08,
      gravityRangeCompound: 1.0,
      edgeElasticity: 0.3,
      coolingFactor: 0.9,
      nestingFactor: 0.8,
      componentSpacing: 160,
      padding: 64,
    } as any
  }, [currentLayout])

  // Re-run layout on data or layout changes
  useEffect(() => {
    if (!cyRef.current) return
    const l = cyRef.current.layout(layoutOptions as any)
    // After layout finishes, nudge nodes to resolve any residual overlaps
    const cy = cyRef.current
    const onStop = () => {
      separateOverlaps(cy)
    }
    cy.one('layoutstop', onStop)
    l.run()
    // Fit after animation settles
    const t = setTimeout(() => cyRef.current && cyRef.current.fit(undefined, 60), 450)
    return () => clearTimeout(t)
  }, [layoutOptions, elements])

  const handleMount = (cy: Core) => {
    cyRef.current = cy

    // Events
    cy.on('tap', 'node', (evt) => {
      const data = evt.target.data()
      if (onNodeClick) onNodeClick(data.raw as FraudChainNode)
      cy.elements().removeClass('selected')
      evt.target.addClass('selected')
    })

    cy.on('tap', 'edge', (evt) => {
      const data = evt.target.data()
      if (onEdgeClick) onEdgeClick(data.raw as FraudChainEdge)
      cy.elements().removeClass('selected')
      evt.target.addClass('selected')
      // show tooltip on tap as well (for touch)
      const pos = evt.position
      const rp = modelToRendered(cy, pos)
      const sLabel = evt.target.source().data('label') || evt.target.source().id()
      const tLabel = evt.target.target().data('label') || evt.target.target().id()
      setEdgeTip({
        edgeId: evt.target.id(),
        x: rp.x,
        y: rp.y,
        relation: data.label,
        confidence: data.confidence,
        sourceLabel: sLabel,
        targetLabel: tLabel,
      })
    })

    cy.on('tap', (evt) => {
      if (evt.target === cy) {
        cy.elements().removeClass('selected')
        setEdgeTip(null)
      }
    })

    // Hover tooltip for edges
    cy.on('mouseover', 'edge', (evt) => {
      const edge = evt.target
      const data = edge.data()
      const mid = (edge as any).midpoint()
      const rp = modelToRendered(cy, mid)
      const sLabel = edge.source().data('label') || edge.source().id()
      const tLabel = edge.target().data('label') || edge.target().id()
      setEdgeTip({
        edgeId: edge.id(),
        x: rp.x,
        y: rp.y,
        relation: data.label,
        confidence: data.confidence,
        sourceLabel: sLabel,
        targetLabel: tLabel,
      })
    })
    cy.on('mouseout', 'edge', () => setEdgeTip(null))

    // Keep tooltip in place on pan/zoom
    cy.on('pan zoom', () => {
      if (!edgeTip) return
      const edge = cy.getElementById(edgeTip.edgeId)
      if (!edge || edge.empty()) return
      const mid = (edge as any).midpoint()
      const rp = modelToRendered(cy, mid)
      setEdgeTip(prev => (prev ? { ...prev, x: rp.x, y: rp.y } : prev))
    })
  }

  const fit = () => cyRef.current?.fit(undefined, 30)
  const getRenderedCenter = () => {
    if (!cyRef.current) return { x: 0, y: 0 }
    // center of the viewport in rendered (pixel) coordinates
    return { x: cyRef.current.width() / 2, y: cyRef.current.height() / 2 }
  }
  const zoomIn = () => {
    if (!cyRef.current) return
    const center = getRenderedCenter()
    cyRef.current.zoom({ level: (cyRef.current.zoom() || 1) * 1.2, renderedPosition: center as any })
  }
  const zoomOut = () => {
    if (!cyRef.current) return
    const center = getRenderedCenter()
    cyRef.current.zoom({ level: (cyRef.current.zoom() || 1) / 1.2, renderedPosition: center as any })
  }
  const exportPng = () => {
    if (!cyRef.current) return
    const png = cyRef.current.png({ bg: '#0b1220', full: true, scale: 2 })
    const a = document.createElement('a')
    a.href = png
    a.download = `fraud_chain_${chain.id}.png`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  }

  return (
    <div ref={containerRef} className={`relative overflow-hidden ${className}`}>
      {enableControls && (
        <div className="absolute top-3 left-3 z-10 flex items-center gap-2 bg-dark-800/80 border border-dark-primary rounded-md px-2 py-1">
          <label className="text-xs text-dark-secondary">Layout</label>
          <select
            className="bg-dark-900 text-dark-primary text-xs rounded p-1 border border-dark-primary"
            value={currentLayout}
            onChange={(e) => setCurrentLayout(e.target.value as 'fcose' | 'dagre')}
          >
            <option value="fcose">Force (fCoSE)</option>
            <option value="dagre">Hierarchical (Dagre)</option>
          </select>
        </div>
      )}

      <div className="absolute top-3 right-3 z-10 flex flex-col gap-2">
        <button onClick={zoomIn} title="Zoom In" className="bg-dark-800 shadow-lg rounded-md p-2 hover:bg-dark-700 border border-dark-primary text-dark-primary">
          +
        </button>
        <button onClick={zoomOut} title="Zoom Out" className="bg-dark-800 shadow-lg rounded-md p-2 hover:bg-dark-700 border border-dark-primary text-dark-primary">
          −
        </button>
        <button onClick={fit} title="Fit" className="bg-dark-800 shadow-lg rounded-md p-2 hover:bg-dark-700 border border-dark-primary text-dark-primary">
          ⤢
        </button>
        <button onClick={exportPng} title="Export PNG" className="bg-primary-600 shadow-lg rounded-md p-2 hover:bg-primary-700 text-white">
          ⬇
        </button>
      </div>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 z-10 bg-dark-800 shadow-lg rounded-md p-3 border border-dark-primary">
        <h4 className="font-semibold text-sm mb-2 text-dark-primary">Legend</h4>
        <div className="grid grid-cols-2 gap-2 text-xs text-dark-secondary">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full" style={{ backgroundColor: typeColor.tip }} />
            <span>Tip</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full" style={{ backgroundColor: typeColor.assessment }} />
            <span>Assessment</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full" style={{ backgroundColor: typeColor.document }} />
            <span>Document</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full" style={{ backgroundColor: typeColor.stock }} />
            <span>Stock</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full" style={{ backgroundColor: typeColor.complaint }} />
            <span>Complaint</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full" style={{ backgroundColor: typeColor.advisor }} />
            <span>Advisor</span>
          </div>
        </div>
      </div>

      <CytoscapeComponent
        elements={elements}
        style={{ width: '100%', height: Math.max(600, dimensions.height) }}
        className="border border-dark-primary rounded-lg bg-dark-950 overflow-hidden"
        layout={layoutOptions as any}
        cy={handleMount}
        stylesheet={stylesheet as any}
        wheelSensitivity={0.2}
      />

      {/* Glassmorphism Edge Tooltip */}
      {edgeTip && (
        <div
          className="pointer-events-auto absolute z-20"
          style={{ left: Math.max(12, edgeTip.x + 8), top: Math.max(12, edgeTip.y + 8) }}
        >
          <div className="backdrop-blur-md bg-white/10 border border-white/20 shadow-xl rounded-lg p-3 text-sm text-white max-w-xs">
            <div className="text-xs uppercase tracking-wide text-dark-secondary mb-1">Relationship</div>
            <div className="font-medium mb-2">{edgeTip.relation}</div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div>
                <div className="text-dark-secondary">From</div>
                <div className="truncate">{edgeTip.sourceLabel}</div>
              </div>
              <div>
                <div className="text-dark-secondary">To</div>
                <div className="truncate">{edgeTip.targetLabel}</div>
              </div>
              {typeof edgeTip.confidence === 'number' && (
                <div className="col-span-2 mt-1">
                  <div className="text-dark-secondary">Confidence</div>
                  <div className="w-full h-1.5 bg-white/10 rounded overflow-hidden">
                    <div className="h-full bg-primary-400" style={{ width: `${Math.min(100, Math.max(0, edgeTip.confidence))}%` }} />
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function edgeColor(type: string): string {
  const colors: Record<string, string> = {
    leads_to: '#3b82f6',
    references: '#10b981',
    mentions: '#f59e0b',
    involves: '#ef4444',
    similar_pattern: '#8b5cf6',
    escalates_to: '#dc2626',
  }
  return colors[type] || '#6b7280'
}

export default FraudChainGraph

// Helpers
function modelToRendered(cy: Core, pos: { x: number; y: number }) {
  const z = cy.zoom()
  const pan = cy.pan()
  return { x: pos.x * z + pan.x, y: pos.y * z + pan.y }
}

// Push nodes apart if they are closer than a minimum distance
function separateOverlaps(cy: Core) {
  const minDist = 90
  const maxIters = 4
  for (let iter = 0; iter < maxIters; iter++) {
    let moved = false
    const nodes = cy.nodes()
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const a = nodes[i]
        const b = nodes[j]
        // skip if connected by an edge (natural closeness allowed but still separate slightly)
        const pa = a.position()
        const pb = b.position()
        const dx = pb.x - pa.x
        const dy = pb.y - pa.y
        const dist = Math.hypot(dx, dy)
        if (dist < minDist && dist > 0.0001) {
          const overlap = (minDist - dist) / 2
          const ux = dx / dist
          const uy = dy / dist
          a.position({ x: pa.x - ux * overlap, y: pa.y - uy * overlap })
          b.position({ x: pb.x + ux * overlap, y: pb.y + uy * overlap })
          moved = true
        }
      }
    }
    if (!moved) break
  }
}
