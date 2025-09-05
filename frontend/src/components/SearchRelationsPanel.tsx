import React, { useEffect, useMemo, useState } from 'react'
import { relationsApi, type FraudChain, type FraudChainNode, type FraudChainEdge } from '../services/api'
import FraudChainGraph from './FraudChainGraph'

interface SearchRelationsPanelProps {
  open: boolean
  onClose: () => void
  entityType: string | null
  referenceId: string | number | null
  depth?: number
  limit?: number
}

const SearchRelationsPanel: React.FC<SearchRelationsPanelProps> = ({
  open,
  onClose,
  entityType,
  referenceId,
  depth = 2,
  limit = 150,
}) => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [nodes, setNodes] = useState<FraudChainNode[]>([])
  const [edges, setEdges] = useState<FraudChainEdge[]>([])
  // Local expansion controls
  const [localDepth, setLocalDepth] = useState<number>(depth)
  const [localLimit, setLocalLimit] = useState<number>(limit)
  const [lastFetch, setLastFetch] = useState<{
    entityType?: string | null
    referenceId?: string | number | null
    depth?: number
    limit?: number
    nodes?: number
    edges?: number
    retried?: boolean
    timestamp?: string
  } | null>(null)

  useEffect(() => {
    if (!open || !entityType || referenceId == null) return
    let cancelled = false
    const fetchData = async () => {
      setLoading(true)
      setError(null)
      try {
        console.debug('[SearchRelationsPanel] Fetching relations', { entityType, referenceId, depth: localDepth, limit: localLimit })
        const { data } = await relationsApi.getRelations(entityType, referenceId, { depth: localDepth, limit: localLimit })
        if (cancelled) return
        let gotNodes = data.nodes || []
        let gotEdges = data.edges || []
        console.debug('[SearchRelationsPanel] Relations response', { nodes: gotNodes.length, edges: gotEdges.length })
        // Retry with backend max if initial result is empty
        let usedRetry = false
        if (gotNodes.length === 0) {
          try {
            const retryDepth = Math.max(3, localDepth)
            const retryLimit = Math.max(300, localLimit)
            console.debug('[SearchRelationsPanel] Empty result, retrying with higher bounds', { retryDepth, retryLimit })
            const retry = await relationsApi.getRelations(entityType, referenceId, { depth: retryDepth, limit: retryLimit })
            gotNodes = retry.data.nodes || []
            gotEdges = retry.data.edges || []
            usedRetry = true
            console.debug('[SearchRelationsPanel] Retry response', { nodes: gotNodes.length, edges: gotEdges.length })
          } catch {}
        }
        setNodes(gotNodes)
        setEdges(gotEdges)
        if (gotNodes.length === 0) {
          setError('No related entities found. Try increasing depth or limit.')
        }
        setLastFetch({
          entityType,
          referenceId,
          depth: localDepth,
          limit: localLimit,
          nodes: gotNodes.length,
          edges: gotEdges.length,
          retried: usedRetry,
          timestamp: new Date().toISOString(),
        })
      } catch (e: any) {
        if (cancelled) return
        setError(e?.response?.data?.detail || e?.message || 'Failed to load relations')
        console.debug('[SearchRelationsPanel] Relations fetch error', e)
        setLastFetch({
          entityType,
          referenceId,
          depth: localDepth,
          limit: localLimit,
          nodes: 0,
          edges: 0,
          retried: false,
          timestamp: new Date().toISOString(),
        })
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    fetchData()
    return () => { cancelled = true }
  }, [open, entityType, referenceId, localDepth, localLimit])

  const chain: FraudChain = useMemo(() => ({
    id: `${entityType || 'entity'}:${referenceId || 'unknown'}`,
    status: 'active',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    nodes,
    edges,
  }), [entityType, referenceId, nodes, edges])

  return (
    <div
      className={`fixed inset-y-0 right-0 w-full sm:w-[520px] md:w-[640px] bg-dark-950 border-l border-dark-primary shadow-xl transform transition-transform duration-300 ease-in-out z-50 ${open ? 'translate-x-0' : 'translate-x-full'}`}
      aria-hidden={!open}
    >
      <div className="flex items-center justify-between px-4 py-3 border-b border-dark-primary bg-dark-900">
        <h3 className="text-lg font-semibold text-dark-primary">Relationship Graph</h3>
        <button onClick={onClose} className="text-dark-secondary hover:text-white px-2 py-1 rounded hover:bg-dark-800">✕</button>
      </div>
      {/* Persistent status banner */}
      <div className="px-4 py-2 text-xs text-dark-secondary bg-dark-900/60 border-b border-dark-primary">
        {lastFetch ? (
          <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
            <span>Entity: <span className="font-mono">{entityType}</span> · Ref: <span className="font-mono">{String(referenceId ?? '')}</span></span>
            <span>Depth: {lastFetch.depth} · Limit: {lastFetch.limit}</span>
            <span>Nodes: {lastFetch.nodes ?? 0} · Edges: {lastFetch.edges ?? 0}</span>
            {lastFetch.retried && (
              <span className="text-amber-300 bg-amber-900/30 border border-amber-800 px-1.5 py-0.5 rounded">Retried with higher bounds</span>
            )}
            <span className="text-dark-500">at {new Date(lastFetch.timestamp || '').toLocaleTimeString()}</span>
          </div>
        ) : (
          <div>No fetch yet. Select a result to view relationships.</div>
        )}
      </div>
      <div className="p-3">
        <div className="text-xs text-dark-secondary mb-2">
          Entity: <span className="font-mono">{entityType}</span> · Ref: <span className="font-mono">{String(referenceId ?? '')}</span> · Depth: {localDepth} · Limit: {localLimit}
        </div>
        {/* Expansion controls */}
        <div className="flex flex-wrap items-center gap-2 mb-3 text-xs">
          <button
            className="px-2 py-1 rounded border border-dark-primary bg-dark-800 text-dark-primary hover:bg-dark-700"
            onClick={() => setLocalDepth((d) => d + 1)}
          >Increase depth</button>
          <button
            className="px-2 py-1 rounded border border-dark-primary bg-dark-800 text-dark-primary hover:bg-dark-700"
            onClick={() => setLocalLimit((l) => Math.min(500, l + 50))}
          >Increase limit</button>
          <button
            className="px-2 py-1 rounded border border-primary-600 bg-primary-600/20 text-primary-300 hover:bg-primary-600/30"
            onClick={() => {
              // trigger effect by nudging depth state (no-op set won't trigger)
              setLocalDepth((d) => d)
              setLocalLimit((l) => l)
            }}
          >Refetch</button>
          <span className="text-dark-500">Tip: Use the ⤢ Fit button on the graph toolbar if nodes appear off-screen.</span>
        </div>
        {loading && (
          <div className="p-4 text-sm text-dark-secondary">Loading relations…</div>
        )}
        {error && (
          <div className="p-3 mb-3 text-sm text-red-300 bg-red-900/30 border border-red-800 rounded">{error}</div>
        )}
        {!loading && !error && nodes.length === 0 && (
          <div className="p-4 text-sm text-dark-secondary">No related entities found.</div>
        )}
        {!loading && !error && nodes.length > 0 && (
          <FraudChainGraph chain={chain} className="h-[70vh]" />
        )}
      </div>
    </div>
  )
}

export default SearchRelationsPanel
