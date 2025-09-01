import React, { useEffect, useRef, useState } from 'react'
import * as d3 from 'd3'
import { FraudChain, FraudChainNode, FraudChainEdge } from '../services/api'

interface FraudChainVisualizationProps {
  chain: FraudChain
  onNodeClick?: (node: FraudChainNode) => void
  onEdgeClick?: (edge: FraudChainEdge) => void
  className?: string
}

interface D3Node extends FraudChainNode {
  x?: number
  y?: number
  fx?: number | null
  fy?: number | null
}

interface D3Edge extends FraudChainEdge {
  source: D3Node
  target: D3Node
}

const FraudChainVisualization: React.FC<FraudChainVisualizationProps> = ({
  chain,
  onNodeClick,
  onEdgeClick,
  className = ''
}) => {
  const svgRef = useRef<SVGSVGElement>(null)
  const [selectedNode, setSelectedNode] = useState<string | null>(null)
  const [selectedEdge, setSelectedEdge] = useState<string | null>(null)
  const [zoomLevel, setZoomLevel] = useState(1)

  useEffect(() => {
    if (!svgRef.current || !chain.nodes.length) return

    // Clear previous visualization
    d3.select(svgRef.current).selectAll('*').remove()

    const svg = d3.select(svgRef.current)
    const width = 800
    const height = 600

    svg.attr('width', width).attr('height', height)

    // Create zoom behavior
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        const { transform } = event
        setZoomLevel(transform.k)
        g.attr('transform', transform)
      })

    svg.call(zoom)

    // Create main group for zooming/panning
    const g = svg.append('g')

    // Prepare data
    const nodes: D3Node[] = chain.nodes.map(node => ({
      ...node,
      x: node.position_x || Math.random() * width,
      y: node.position_y || Math.random() * height
    }))

    const edges: D3Edge[] = chain.edges.map(edge => {
      const source = nodes.find(n => n.id === edge.from_node_id)!
      const target = nodes.find(n => n.id === edge.to_node_id)!
      return { ...edge, source, target }
    })

    // Create force simulation
    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(edges).id((d: any) => d.id).distance(150))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(40))

    // Create arrow markers for directed edges
    const defs = g.append('defs')
    
    defs.append('marker')
      .attr('id', 'arrowhead')
      .attr('viewBox', '-0 -5 10 10')
      .attr('refX', 25)
      .attr('refY', 0)
      .attr('orient', 'auto')
      .attr('markerWidth', 8)
      .attr('markerHeight', 8)
      .attr('xoverflow', 'visible')
      .append('svg:path')
      .attr('d', 'M 0,-5 L 10 ,0 L 0,5')
      .attr('fill', '#666')
      .style('stroke', 'none')

    // Create edges
    const link = g.append('g')
      .attr('class', 'links')
      .selectAll('line')
      .data(edges)
      .enter().append('line')
      .attr('class', 'edge')
      .attr('stroke', (d) => getEdgeColor(d.relationship_type))
      .attr('stroke-width', (d) => Math.max(1, d.confidence / 25))
      .attr('stroke-opacity', 0.8)
      .attr('marker-end', 'url(#arrowhead)')
      .style('cursor', 'pointer')
      .on('click', (event, d) => {
        event.stopPropagation()
        setSelectedEdge(d.id)
        onEdgeClick?.(d)
      })
      .on('mouseover', function(event, d) {
        d3.select(this).attr('stroke-width', Math.max(3, d.confidence / 15))
        
        // Show tooltip (implementation removed for now)
          .style('font-size', '12px')
          .style('pointer-events', 'none')
          .style('z-index', '1000')
          .html(`
            <strong>${d.relationship_type}</strong><br/>
            Confidence: ${d.confidence}%<br/>
            Created: ${new Date(d.created_at).toLocaleDateString()}
          `)
          .style('left', (event.pageX + 10) + 'px')
          .style('top', (event.pageY - 10) + 'px')
      })
      .on('mouseout', function(_event, d) {
        d3.select(this).attr('stroke-width', Math.max(1, d.confidence / 25))
        d3.selectAll('.fraud-chain-tooltip').remove()
      })

    // Create nodes
    const node = g.append('g')
      .attr('class', 'nodes')
      .selectAll('g')
      .data(nodes)
      .enter().append('g')
      .attr('class', 'node')
      .style('cursor', 'pointer')
      .call(d3.drag<SVGGElement, D3Node>()
        .on('start', (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart()
          d.fx = d.x
          d.fy = d.y
        })
        .on('drag', (event, d) => {
          d.fx = event.x
          d.fy = event.y
        })
        .on('end', (event, d) => {
          if (!event.active) simulation.alphaTarget(0)
          d.fx = null
          d.fy = null
        })
      )

    // Add circles for nodes
    node.append('circle')
      .attr('r', (d) => getNodeRadius(d.node_type))
      .attr('fill', (d) => getNodeColor(d.node_type))
      .attr('stroke', (d) => selectedNode === d.id ? '#ff6b35' : '#fff')
      .attr('stroke-width', (d) => selectedNode === d.id ? 3 : 2)
      .on('click', (event, d) => {
        event.stopPropagation()
        setSelectedNode(d.id)
        onNodeClick?.(d)
      })

    // Add icons for different node types
    node.append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', '0.35em')
      .attr('font-size', '14px')
      .attr('fill', 'white')
      .attr('font-weight', 'bold')
      .text((d) => getNodeIcon(d.node_type))

    // Add labels
    node.append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', '2.5em')
      .attr('font-size', '10px')
      .attr('fill', '#333')
      .text((d) => d.label || d.node_type)
      .call(wrapText, 80)

    // Update positions on simulation tick
    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y)

      node.attr('transform', (d) => `translate(${d.x},${d.y})`)
    })

    // Clear selections when clicking on empty space
    svg.on('click', () => {
      setSelectedNode(null)
      setSelectedEdge(null)
    })

    return () => {
      simulation.stop()
    }
  }, [chain, selectedNode, selectedEdge, onNodeClick, onEdgeClick])

  const getNodeColor = (nodeType: string): string => {
    const colors = {
      tip: '#3b82f6',      // Blue
      assessment: '#ef4444', // Red
      document: '#10b981',   // Green
      stock: '#f59e0b',      // Amber
      complaint: '#8b5cf6',  // Purple
      advisor: '#06b6d4'     // Cyan
    }
    return colors[nodeType as keyof typeof colors] || '#6b7280'
  }

  const getNodeRadius = (nodeType: string): number => {
    const sizes = {
      tip: 25,
      assessment: 30,
      document: 25,
      stock: 20,
      complaint: 25,
      advisor: 25
    }
    return sizes[nodeType as keyof typeof sizes] || 25
  }

  const getNodeIcon = (nodeType: string): string => {
    const icons = {
      tip: '💡',
      assessment: '⚠️',
      document: '📄',
      stock: '📈',
      complaint: '📢',
      advisor: '👤'
    }
    return icons[nodeType as keyof typeof icons] || '●'
  }

  const getEdgeColor = (relationshipType: string): string => {
    const colors = {
      leads_to: '#3b82f6',
      references: '#10b981',
      mentions: '#f59e0b',
      involves: '#ef4444',
      similar_pattern: '#8b5cf6',
      escalates_to: '#dc2626'
    }
    return colors[relationshipType as keyof typeof colors] || '#6b7280'
  }

  const wrapText = (text: any, width: number) => {
    text.each(function(this: SVGTextElement) {
      const textElement = d3.select(this)
      const words = textElement.text().split(/\s+/).reverse()
      let word: string | undefined
      let line: string[] = []
      let lineNumber = 0
      const lineHeight = 1.1
      const y = textElement.attr('y')
      const dy = parseFloat(textElement.attr('dy'))
      let tspan = textElement.text(null).append('tspan').attr('x', 0).attr('y', y).attr('dy', dy + 'em')
      
      while (word = words.pop()) {
        line.push(word)
        tspan.text(line.join(' '))
        if (tspan.node()!.getComputedTextLength() > width) {
          line.pop()
          tspan.text(line.join(' '))
          line = [word]
          tspan = textElement.append('tspan').attr('x', 0).attr('y', y).attr('dy', ++lineNumber * lineHeight + dy + 'em').text(word)
        }
      }
    })
  }

  const handleZoomIn = () => {
    const svg = d3.select(svgRef.current)
    svg.transition().call(
      d3.zoom<SVGSVGElement, unknown>().scaleBy as any,
      1.5
    )
  }

  const handleZoomOut = () => {
    const svg = d3.select(svgRef.current)
    svg.transition().call(
      d3.zoom<SVGSVGElement, unknown>().scaleBy as any,
      1 / 1.5
    )
  }

  const handleResetZoom = () => {
    const svg = d3.select(svgRef.current)
    svg.transition().call(
      d3.zoom<SVGSVGElement, unknown>().transform as any,
      d3.zoomIdentity
    )
  }

  return (
    <div className={`fraud-chain-visualization ${className}`}>
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
      </div>

      {/* Zoom level indicator */}
      <div className="absolute top-4 left-4 z-10 bg-dark-800 shadow-lg rounded-md px-3 py-1 text-sm border border-dark-primary text-dark-primary">
        Zoom: {Math.round(zoomLevel * 100)}%
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

      {/* Main SVG */}
      <svg
        ref={svgRef}
        className="w-full h-full border border-dark-primary rounded-lg bg-dark-950"
        style={{ minHeight: '600px' }}
      />
    </div>
  )
}

export default FraudChainVisualization