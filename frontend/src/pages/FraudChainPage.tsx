import React, { useState, useEffect } from 'react'
import { fraudChainApi, FraudChain, FraudChainListItem, FraudChainNode, FraudChainEdge } from '../services/api'
import FraudChainVisualization from '../components/FraudChainVisualization'
import FraudChainDetailsModal from '../components/FraudChainDetailsModal'

const FraudChainPage: React.FC = () => {
  const [chains, setChains] = useState<FraudChainListItem[]>([])
  const [selectedChain, setSelectedChain] = useState<FraudChain | null>(null)
  const [selectedNode, setSelectedNode] = useState<FraudChainNode | null>(null)
  const [selectedEdge, setSelectedEdge] = useState<FraudChainEdge | null>(null)
  const [loading, setLoading] = useState(true)
  const [loadingChain, setLoadingChain] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false)
  const [autoLinking, setAutoLinking] = useState(false)

  useEffect(() => {
    loadChains()
  }, [statusFilter])

  const loadChains = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await fraudChainApi.getChains({
        status: statusFilter || undefined,
        limit: 50
      })
      setChains(response.data)
    } catch (err) {
      setError('Failed to load fraud chains')
      console.error('Error loading chains:', err)
    } finally {
      setLoading(false)
    }
  }

  const loadChainDetails = async (chainId: string) => {
    try {
      setLoadingChain(true)
      setError(null)
      const response = await fraudChainApi.getChain(chainId)
      setSelectedChain(response.data)
    } catch (err) {
      setError('Failed to load chain details')
      console.error('Error loading chain details:', err)
    } finally {
      setLoadingChain(false)
    }
  }

  const handleChainSelect = (chain: FraudChainListItem) => {
    loadChainDetails(chain.id)
  }

  const handleNodeClick = (node: FraudChainNode) => {
    setSelectedNode(node)
    setSelectedEdge(null)
    setIsDetailsModalOpen(true)
  }

  const handleEdgeClick = (edge: FraudChainEdge) => {
    setSelectedEdge(edge)
    setSelectedNode(null)
    setIsDetailsModalOpen(true)
  }

  const handleExportChain = async (format: 'json' | 'csv') => {
    if (!selectedChain) return

    try {
      const response = await fraudChainApi.exportChain(selectedChain.id, format)
      
      if (format === 'csv') {
        // Handle CSV blob download
        const blob = response.data as Blob
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `fraud_chain_${selectedChain.id}.csv`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      } else {
        // Handle JSON download
        const data = response.data as any
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `fraud_chain_${selectedChain.id}.json`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      }
    } catch (err) {
      setError('Failed to export chain data')
      console.error('Error exporting chain:', err)
    }
  }

  const handleAutoLink = async () => {
    try {
      setAutoLinking(true)
      setError(null)
      const response = await fraudChainApi.autoLink()
      
      // Show success message
      alert(`Auto-linking completed: ${response.data.chains_created} chains created, ${response.data.links_added} links added`)
      
      // Reload chains
      await loadChains()
    } catch (err) {
      setError('Failed to auto-link fraud cases')
      console.error('Error auto-linking:', err)
    } finally {
      setAutoLinking(false)
    }
  }

  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800'
      case 'investigating':
        return 'bg-yellow-100 text-yellow-800'
      case 'closed':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="min-h-screen bg-dark-950">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-dark-primary">Fraud Chain Detection</h1>
          <p className="mt-2 text-dark-secondary">
            Visualize and analyze fraud patterns and relationships between cases
          </p>
        </div>

        {error && (
          <div className="mb-6 bg-danger-900 border border-danger-700 rounded-md p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-danger-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-danger-200">{error}</p>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar - Chain List */}
          <div className="lg:col-span-1">
            <div className="bg-dark-900 rounded-lg shadow-lg border border-dark-primary">
              <div className="p-4 border-b border-dark-primary">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-dark-primary">Fraud Chains</h2>
                  <button
                    onClick={handleAutoLink}
                    disabled={autoLinking}
                    className="px-3 py-1 text-sm bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {autoLinking ? 'Linking...' : 'Auto-Link'}
                  </button>
                </div>
                
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="w-full px-3 py-2 bg-dark-800 border border-dark-primary rounded-md text-sm text-dark-primary focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="">All Statuses</option>
                  <option value="active">Active</option>
                  <option value="investigating">Investigating</option>
                  <option value="closed">Closed</option>
                </select>
              </div>

              <div className="max-h-96 overflow-y-auto">
                {loading ? (
                  <div className="p-4 text-center text-dark-muted">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600 mx-auto"></div>
                    <p className="mt-2 text-sm">Loading chains...</p>
                  </div>
                ) : chains.length === 0 ? (
                  <div className="p-4 text-center text-dark-muted">
                    <p className="text-sm">No fraud chains found</p>
                  </div>
                ) : (
                  <div className="divide-y divide-dark-primary">
                    {chains.map((chain) => (
                      <div
                        key={chain.id}
                        onClick={() => handleChainSelect(chain)}
                        className={`p-4 cursor-pointer hover:bg-dark-800 transition-colors ${
                          selectedChain?.id === chain.id ? 'bg-primary-900 border-r-2 border-primary-500' : ''
                        }`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1 min-w-0">
                            <h3 className="text-sm font-medium text-dark-primary truncate">
                              {chain.name || `Chain ${chain.id.slice(0, 8)}`}
                            </h3>
                            {chain.description && (
                              <p className="text-xs text-dark-secondary mt-1 line-clamp-2">
                                {chain.description}
                              </p>
                            )}
                            <div className="flex items-center gap-2 mt-2">
                              <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadgeColor(chain.status)}`}>
                                {chain.status}
                              </span>
                            </div>
                            <div className="flex items-center gap-4 mt-2 text-xs text-dark-muted">
                              <span>{chain.node_count} nodes</span>
                              <span>{chain.edge_count} edges</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Main Content - Visualization */}
          <div className="lg:col-span-3">
            <div className="bg-dark-900 rounded-lg shadow-lg border border-dark-primary">
              {selectedChain ? (
                <>
                  <div className="p-4 border-b border-dark-primary">
                    <div className="flex items-center justify-between">
                      <div>
                        <h2 className="text-lg font-semibold text-dark-primary">
                          {selectedChain.name || `Chain ${selectedChain.id.slice(0, 8)}`}
                        </h2>
                        {selectedChain.description && (
                          <p className="text-sm text-dark-secondary mt-1">{selectedChain.description}</p>
                        )}
                        <div className="flex items-center gap-4 mt-2 text-sm text-dark-muted">
                          <span>{selectedChain.nodes.length} nodes</span>
                          <span>{selectedChain.edges.length} edges</span>
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadgeColor(selectedChain.status)}`}>
                            {selectedChain.status}
                          </span>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleExportChain('json')}
                          className="px-3 py-2 text-sm bg-dark-700 text-dark-primary rounded-md hover:bg-dark-600 transition-colors border border-dark-primary"
                        >
                          Export JSON
                        </button>
                        <button
                          onClick={() => handleExportChain('csv')}
                          className="px-3 py-2 text-sm bg-dark-700 text-dark-primary rounded-md hover:bg-dark-600 transition-colors border border-dark-primary"
                        >
                          Export CSV
                        </button>
                      </div>
                    </div>
                  </div>

                  <div className="relative">
                    {loadingChain ? (
                      <div className="flex items-center justify-center h-96">
                        <div className="text-center">
                          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
                          <p className="mt-2 text-sm text-dark-muted">Loading chain details...</p>
                        </div>
                      </div>
                    ) : (
                      <FraudChainVisualization
                        chain={selectedChain}
                        onNodeClick={handleNodeClick}
                        onEdgeClick={handleEdgeClick}
                        className="h-96"
                      />
                    )}
                  </div>
                </>
              ) : (
                <div className="flex items-center justify-center h-96">
                  <div className="text-center">
                    <svg className="mx-auto h-12 w-12 text-dark-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                    </svg>
                    <h3 className="mt-2 text-sm font-medium text-dark-primary">No chain selected</h3>
                    <p className="mt-1 text-sm text-dark-secondary">
                      Select a fraud chain from the sidebar to view its visualization
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Details Modal */}
      <FraudChainDetailsModal
        isOpen={isDetailsModalOpen}
        onClose={() => setIsDetailsModalOpen(false)}
        selectedNode={selectedNode}
        selectedEdge={selectedEdge}
      />
    </div>
  )
}

export default FraudChainPage