import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { type SearchHit, fraudChainApi, relationsApi, type RelationsResponse, type FraudChainNode } from '../services/api'
import { useToast } from '../contexts/ToastContext'
import SearchRelationsPanel from './SearchRelationsPanel'
import Card, { CardHeader, CardTitle, CardContent } from './ui/Card'
import Badge from './ui/Badge'
import Toolbar from './ui/Toolbar'
import EmptyState from './ui/EmptyState'

interface Props {
  hits: SearchHit[]
  total: number
  page: number
  pageSize: number
  loading?: boolean
  onPageChange: (page: number) => void
  onViewRelationships?: (hit: SearchHit) => void
}

const SearchResults: React.FC<Props> = ({ hits, total, page, pageSize, loading = false, onPageChange, onViewRelationships }) => {
  const totalPages = Math.max(1, Math.ceil(total / pageSize))
  const navigate = useNavigate()
  const [relationsOpen, setRelationsOpen] = useState(false)
  const [selectedEntityType, setSelectedEntityType] = useState<string | null>(null)
  const [selectedReferenceId, setSelectedReferenceId] = useState<string | number | null>(null)
  const [rebuilding, setRebuilding] = useState(false)
  const { addToast } = useToast()

  // Prefetched relations per hit (shallow depth for quick chain context)
  const [relationsMap, setRelationsMap] = useState<Record<string | number, RelationsResponse | null>>({})

  useEffect(() => {
    let cancelled = false
    // Prefetch only for currently visible hits (limit to 10 to keep it light)
    const toFetch = hits.slice(0, 10).filter((h) => relationsMap[h.id] === undefined)
    if (toFetch.length === 0) return

    ;(async () => {
      const results = await Promise.allSettled(
        toFetch.map((h) => relationsApi.getRelations(h.entity_type, h.id, { depth: 2, limit: 50 }))
      )
      if (cancelled) return
      const updates: Record<string | number, RelationsResponse | null> = {}
      results.forEach((res, idx) => {
        const hit = toFetch[idx]
        if (res.status === 'fulfilled') updates[hit.id] = res.value.data
        else updates[hit.id] = null
      })
      setRelationsMap((prev) => ({ ...prev, ...updates }))
    })()

    return () => { cancelled = true }
  }, [hits])

  const summarizeByType = (nodes: FraudChainNode[]) => {
    const groups: Record<string, FraudChainNode[]> = {}
    nodes.forEach((n) => {
      groups[n.node_type] = groups[n.node_type] || []
      groups[n.node_type].push(n)
    })
    return groups
  }

  const openRelations = async (hit: SearchHit) => {
    if (onViewRelationships) {
      onViewRelationships(hit)
    } else {
      // Inline relations panel fallback
      const entityType = hit.entity_type
      setSelectedEntityType(entityType)
      setSelectedReferenceId(hit.id)
      setRelationsOpen(true)
    }
    // Fire-and-forget deterministic upsert into a chain so Fraud Chains reflects this quickly
    try {
      void fraudChainApi.upsertEntity({
        entity_type: hit.entity_type,
        reference_id: String(hit.id),
        label: hit.title,
        create_new_chain: true,
      })
    } catch {}
  }

  return (
    <Card className="bg-background-50">
      <CardHeader>
        <CardTitle>Results</CardTitle>
        <Toolbar dense className="bg-white border-contrast-200">
          <div className="flex items-center gap-2">
            <span className="text-xs text-contrast-600">{loading ? 'Loading…' : `${total} results`}</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              className="px-3 py-1.5 border border-contrast-200 rounded-lg text-sm disabled:opacity-50"
              disabled={rebuilding}
              onClick={async () => {
                setRebuilding(true)
                try {
                  const { data } = await fraudChainApi.autoLink()
                  addToast({
                    title: 'Fraud chains rebuilt',
                    description: `Chains +${data.chains_created}, Links +${data.links_added}`,
                    variant: 'success'
                  })
                } catch (e) {
                  addToast({
                    title: 'Rebuild failed',
                    description: 'Unable to rebuild chains. Please try again.',
                    variant: 'error'
                  })
                } finally {
                  setRebuilding(false)
                }
              }}
            >{rebuilding ? 'Rebuilding…' : 'Rebuild Chains'}</button>
          </div>
          <div className="flex items-center gap-2">
            <button
              className="px-3 py-1.5 border border-contrast-200 rounded-lg text-sm disabled:opacity-50"
              onClick={() => onPageChange(Math.max(1, page - 1))}
              disabled={page <= 1 || loading}
            >Prev</button>
            <span className="text-xs text-contrast-600">Page {page} / {totalPages}</span>
            <button
              className="px-3 py-1.5 border border-contrast-200 rounded-lg text-sm disabled:opacity-50"
              onClick={() => onPageChange(Math.min(totalPages, page + 1))}
              disabled={page >= totalPages || loading}
            >Next</button>
          </div>
        </Toolbar>
      </CardHeader>

      <CardContent>
        {hits.length === 0 && !loading ? (
          <EmptyState title="No results" description="Try adjusting filters or searching different keywords." />
        ) : (
          <ul className="space-y-2">
            {hits.map((hit) => (
              <li key={`${hit.entity_type}-${hit.id}`}>
                <div
                  className="w-full text-left p-3 rounded-lg border transition-colors bg-white hover:bg-contrast-50 border-contrast-200"
                >
                  <div className="font-semibold capitalize">{hit.title || String(hit.id)}</div>
                  <div className="text-xs text-contrast-600 mt-0.5 line-clamp-2">{hit.snippet || ''}</div>
                  {/* Chain-focused mini summary */}
                  <div className="text-xs text-contrast-600 mt-2">
                    {relationsMap[hit.id] ? (
                      (() => {
                        const rel = relationsMap[hit.id]!
                        const groups = summarizeByType(rel.nodes)
                        const typeOrder = ['tip','assessment','document','stock','complaint','advisor']
                        return (
                          <div className="flex flex-col gap-1">
                            <div className="flex flex-wrap gap-2">
                              {typeOrder.filter(t => groups[t]?.length).map((t) => (
                                <span key={t} className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full border border-contrast-200 bg-contrast-50">
                                  <span className="capitalize">{t}</span>
                                  <span className="text-contrast-500">{groups[t].length}</span>
                                </span>
                              ))}
                              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full border border-contrast-200 bg-contrast-50">
                                edges <span className="text-contrast-500">{rel.edges.length}</span>
                              </span>
                            </div>
                            {/* Show a few related labels */}
                            <div className="flex flex-wrap gap-1 text-contrast-700">
                              {rel.nodes.slice(0, 6).map((n) => (
                                <span key={n.id} className="px-2 py-0.5 rounded border border-contrast-200 bg-white text-[11px]">
                                  {n.label || n.reference_id}
                                </span>
                              ))}
                              {rel.nodes.length > 6 && (
                                <span className="text-[11px] text-contrast-500">+{rel.nodes.length - 6} more</span>
                              )}
                            </div>
                          </div>
                        )
                      })()
                    ) : relationsMap[hit.id] === null ? (
                      <span className="text-contrast-400">No relations found</span>
                    ) : (
                      <span className="text-contrast-400">Loading chain context…</span>
                    )}
                  </div>
                  <div className="text-xs text-contrast-400 mt-1 flex items-center gap-3">
                    {hit.created_at && <span>{new Date(hit.created_at).toLocaleString()}</span>}
                    {hit.risk_level && <Badge className="capitalize">{hit.risk_level}</Badge>}
                  </div>
                  <div className="mt-2 flex gap-3">
                    <button
                      className="text-sm text-primary-700 hover:underline"
                      onClick={() => openRelations(hit)}
                    >View Relationships</button>
                    <button
                      className="text-sm text-contrast-700 hover:underline"
                      onClick={async () => {
                        // Trigger backend to auto-link more edges for this context, then refresh this hit's relations
                        try {
                          await fraudChainApi.autoLink()
                        } catch {}
                        try {
                          const { data } = await relationsApi.getRelations(hit.entity_type, hit.id, { depth: 2, limit: 100 })
                          setRelationsMap((prev) => ({ ...prev, [hit.id]: data }))
                        } catch {
                          setRelationsMap((prev) => ({ ...prev, [hit.id]: prev[hit.id] ?? null }))
                        }
                      }}
                    >Add related edges</button>
                    <button
                      className="text-sm text-contrast-700 hover:underline"
                      onClick={async () => {
                        try {
                          const { data } = await relationsApi.getRelations(hit.entity_type, hit.id, { depth: 3, limit: 150 })
                          setRelationsMap((prev) => ({ ...prev, [hit.id]: data }))
                        } catch {}
                      }}
                    >Expand context</button>
                    <button
                      className="text-sm text-contrast-700 hover:underline"
                      onClick={() => {
                        const params = new URLSearchParams({
                          entityType: hit.entity_type,
                          refId: String(hit.id),
                        })
                        if (hit.title) params.set('label', hit.title)
                        navigate(`/investigation?${params.toString()}`)
                        // Best-effort deterministic upsert when opening in investigation too
                        try {
                          void fraudChainApi.upsertEntity({
                            entity_type: hit.entity_type,
                            reference_id: String(hit.id),
                            label: hit.title,
                            create_new_chain: true,
                          })
                        } catch {}
                      }}
                    >Open in Investigation</button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </CardContent>

      {!onViewRelationships && (
        <SearchRelationsPanel
          open={relationsOpen}
          onClose={() => setRelationsOpen(false)}
          entityType={selectedEntityType}
          referenceId={selectedReferenceId}
          depth={2}
          limit={150}
        />
      )}
    </Card>
  )
}

export default SearchResults
