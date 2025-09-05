import React, { useEffect, useMemo, useState } from 'react'
import { fraudChainApi, FraudChain, FraudChainListItem, NodeSearchResponse } from '../services/api'
import FraudChainList from '../components/FraudChainList'
import FraudChainGraph from '../components/FraudChainGraph'
import CaseNotesPanel from '../components/CaseNotesPanel'
import Card, { CardContent } from '../components/ui/Card'
import Skeleton from '../components/ui/Skeleton'

const InvestigationPage: React.FC = () => {
  const [chains, setChains] = useState<FraudChainListItem[]>([])
  const [chainsLoading, setChainsLoading] = useState<boolean>(false)
  const [selectedChainId, setSelectedChainId] = useState<string | undefined>(undefined)
  const [chain, setChain] = useState<FraudChain | null>(null)
  const [chainLoading, setChainLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [nodeSearchQuery, setNodeSearchQuery] = useState<string>('')
  const [zoomToMatches, setZoomToMatches] = useState<boolean>(true)
  const [useBackendSearch, setUseBackendSearch] = useState<boolean>(false)
  const [backendSearchInfo, setBackendSearchInfo] = useState<{ used_backend?: string; total?: number; took_ms?: number } | null>(null)
  const [nodeHighlightIds, setNodeHighlightIds] = useState<string[] | undefined>(undefined)

  const loadChains = async () => {
    setChainsLoading(true)
    setError(null)
    try {
      const { data } = await fraudChainApi.getChains({ limit: 25 })
      setChains(data)
      const hash = window.location.hash
      const hashId = hash.startsWith('#chain:') ? hash.slice('#chain:'.length) : undefined
      if (data.length > 0) {
        const initialId = (hashId && data.find(c => c.id === hashId)?.id) || data[0].id
        setSelectedChainId(initialId)
        await loadChain(initialId)
      } else {
        setSelectedChainId(undefined)
        setChain(null)
      }
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Failed to load chains')
    } finally {
      setChainsLoading(false)
    }
  }

  const loadChain = async (id: string) => {
    setChainLoading(true)
    setError(null)
    try {
      const { data } = await fraudChainApi.getChain(id)
      setChain(data)
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Failed to load chain')
      setChain(null)
    } finally {
      setChainLoading(false)
    }
  }

  useEffect(() => {
    loadChains()
  }, [])

  // Support deep linking: watch hash changes and load chain if available
  useEffect(() => {
    const onHashChange = () => {
      const hash = window.location.hash
      const hashId = hash.startsWith('#chain:') ? hash.slice('#chain:'.length) : undefined
      if (hashId && hashId !== selectedChainId && chains.some(c => c.id === hashId)) {
        handleSelectChain(hashId)
      }
    }
    window.addEventListener('hashchange', onHashChange)
    return () => window.removeEventListener('hashchange', onHashChange)
  }, [chains, selectedChainId])

  // Backend node-level search with debouncing; sets nodeHighlightIds for precise highlighting
  useEffect(() => {
    let cancelled = false
    const timer = setTimeout(async () => {
      if (!useBackendSearch || !nodeSearchQuery.trim()) {
        if (!cancelled) {
          setBackendSearchInfo(null)
          setNodeHighlightIds(undefined)
        }
        return
      }
      try {
        const { data } = await fraudChainApi.nodeSearch({ query: nodeSearchQuery, chain_id: selectedChainId })
        if (cancelled) return
        const res: NodeSearchResponse = data
        setBackendSearchInfo({ used_backend: res.used_backend, total: res.total, took_ms: res.took_ms })
        // If searching within a selected chain, prefer that group's reference_ids
        const byChain = res.results.find(r => r.chain_id === selectedChainId)
        const ids = byChain ? byChain.reference_ids : res.results.flatMap(r => r.reference_ids)
        setNodeHighlightIds(ids)
      } catch (e) {
        if (cancelled) return
        setBackendSearchInfo({ used_backend: 'unknown', total: 0, took_ms: 0 })
        setNodeHighlightIds(undefined)
      }
    }, 300)
    return () => { cancelled = true; clearTimeout(timer) }
  }, [nodeSearchQuery, useBackendSearch, selectedChainId])

  const filteredChains = useMemo(() => {
    if (!searchQuery.trim()) return chains
    const q = searchQuery.toLowerCase()
    return chains.filter(c =>
      (c.name || '').toLowerCase().includes(q) ||
      (c.description || '').toLowerCase().includes(q) ||
      c.id.toLowerCase().includes(q)
    )
  }, [chains, searchQuery])

  const handleSelectChain = async (id: string) => {
    setSelectedChainId(id)
    window.location.hash = `chain:${id}`
    await loadChain(id)
  }

  const handleResetDemo = async () => {
    setError(null)
    setChainLoading(true)
    try {
      const { data } = await fraudChainApi.resetDemoGraph()
      await loadChains()
      if (data?.chain_id) {
        setSelectedChainId(data.chain_id)
        await loadChain(data.chain_id)
      }
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Reset demo graph failed')
    } finally {
      setChainLoading(false)
    }
  }

  const handleAutoLink = async () => {
    setError(null)
    setChainsLoading(true)
    try {
      await fraudChainApi.autoLink()
      await loadChains()
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Auto-link failed')
    } finally {
      setChainsLoading(false)
    }
  }

  return (
    <div className="p-4 md:p-6">
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-xl font-semibold">Investigation</h1>
        <div className="flex items-center gap-2">
          <button onClick={handleAutoLink} className="px-3 py-1.5 rounded-lg bg-amber-600 text-white hover:bg-amber-700">Auto-link</button>
          <button onClick={handleResetDemo} className="px-3 py-1.5 rounded-lg bg-rose-600 text-white hover:bg-rose-700">Reset Demo Graph</button>
        </div>
      </div>

      {error && (
        <div className="mb-3 p-3 rounded-md border border-rose-300 bg-rose-50 text-rose-800 text-sm">{error}</div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        <div className="lg:col-span-1">
          <div className="mb-3">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search chains by name or description..."
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-dark-secondary dark:text-white dark:border-gray-600"
            />
          </div>
          <FraudChainList
            chains={filteredChains}
            onSelectChain={handleSelectChain}
            loading={chainsLoading}
            selectedChainId={selectedChainId}
          />
        </div>
        <div className="lg:col-span-3 space-y-4">
          <Card>
            <CardContent>
              {/* Node-level search and options */}
              <div className="mb-3 flex flex-col md:flex-row md:items-center md:justify-between gap-2">
                <div className="flex-1">
                  <input
                    type="text"
                    value={nodeSearchQuery}
                    onChange={(e) => setNodeSearchQuery(e.target.value)}
                    placeholder="Search nodes in chain (label, type, reference data)..."
                    className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-dark-secondary dark:text-white dark:border-gray-600"
                  />
                </div>
                <div className="flex items-center gap-3">
                  <label className="inline-flex items-center gap-2 text-sm">
                    <input type="checkbox" checked={zoomToMatches} onChange={(e) => setZoomToMatches(e.target.checked)} />
                    <span>Zoom to matches</span>
                  </label>
                  <label className="inline-flex items-center gap-2 text-sm">
                    <input type="checkbox" checked={useBackendSearch} onChange={(e) => setUseBackendSearch(e.target.checked)} />
                    <span>Use backend search</span>
                  </label>
                </div>
              </div>
              {backendSearchInfo && (
                <div className="mb-3 text-xs text-contrast-500">
                  Backend: <span className="font-medium">{backendSearchInfo.used_backend}</span> ·
                  Hits: <span className="font-medium">{backendSearchInfo.total}</span> ·
                  Took: <span className="font-medium">{backendSearchInfo.took_ms}ms</span>
                </div>
              )}
              {chainLoading && !chain && (
                <div className="space-y-3">
                  <Skeleton height={32} />
                  <Skeleton height={480} />
                </div>
              )}
              {!chainLoading && !chain && (
                <div className="text-sm text-contrast-500">No chain selected.</div>
              )}
              {chain && (
                <div className="h-[70vh] min-h-[560px]">
                  <FraudChainGraph
                    chain={chain}
                    className="h-full"
                    enableControls
                    nodeHighlightQuery={useBackendSearch ? undefined : nodeSearchQuery}
                    nodeHighlightIds={useBackendSearch ? nodeHighlightIds : undefined}
                    focusOnHighlight={zoomToMatches}
                  />
                </div>
              )}
            </CardContent>
          </Card>
          <Card>
            <CardContent>
              <div className="mb-3">
                <h2 className="text-base font-medium">Case & Notes</h2>
                <div className="text-xs text-contrast-500">Create a case for this fraud chain and add investigation notes.</div>
              </div>
              {selectedChainId ? (
                <CaseNotesPanel relatedEntityType="fraud_chain" relatedEntityId={selectedChainId} />
              ) : (
                <div className="text-sm text-contrast-500">Select a fraud chain to manage its case and notes.</div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default InvestigationPage
