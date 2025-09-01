import React from 'react'
import { FraudChainNode, FraudChainEdge } from '../services/api'

interface FraudChainDetailsModalProps {
  isOpen: boolean
  onClose: () => void
  selectedNode?: FraudChainNode | null
  selectedEdge?: FraudChainEdge | null
}

const FraudChainDetailsModal: React.FC<FraudChainDetailsModalProps> = ({
  isOpen,
  onClose,
  selectedNode,
  selectedEdge
}) => {
  if (!isOpen) return null

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  const getNodeTypeDescription = (nodeType: string) => {
    const descriptions = {
      tip: 'Investment tip or suspicious message',
      assessment: 'AI risk assessment result',
      document: 'PDF document or file',
      stock: 'Stock symbol or financial instrument',
      complaint: 'User complaint or report',
      advisor: 'Financial advisor or entity'
    }
    return descriptions[nodeType as keyof typeof descriptions] || 'Unknown node type'
  }

  const getRelationshipDescription = (relationshipType: string) => {
    const descriptions = {
      leads_to: 'Directly leads to or causes',
      references: 'References or mentions',
      mentions: 'Contains mention of',
      involves: 'Involves or includes',
      similar_pattern: 'Shows similar fraud pattern',
      escalates_to: 'Escalates or progresses to'
    }
    return descriptions[relationshipType as keyof typeof descriptions] || 'Unknown relationship'
  }

  const renderReferenceData = (metadata: any) => {
    if (!metadata?.reference_data) return null

    const refData = metadata.reference_data

    return (
      <div className="mt-4 p-3 bg-gray-50 rounded-lg">
        <h4 className="font-semibold text-sm mb-2">Reference Data</h4>
        <div className="space-y-2 text-sm">
          {refData.message && (
            <div>
              <span className="font-medium">Message:</span>
              <p className="text-gray-700 mt-1">{refData.message}</p>
            </div>
          )}
          {refData.level && (
            <div>
              <span className="font-medium">Risk Level:</span>
              <span className={`ml-2 px-2 py-1 rounded text-xs font-medium ${
                refData.level === 'High' ? 'bg-red-100 text-red-800' :
                refData.level === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                'bg-green-100 text-green-800'
              }`}>
                {refData.level}
              </span>
            </div>
          )}
          {refData.score !== undefined && (
            <div>
              <span className="font-medium">Score:</span>
              <span className="ml-2">{refData.score}%</span>
            </div>
          )}
          {refData.stock_symbols && refData.stock_symbols.length > 0 && (
            <div>
              <span className="font-medium">Stock Symbols:</span>
              <div className="flex flex-wrap gap-1 mt-1">
                {refData.stock_symbols.map((symbol: string, index: number) => (
                  <span key={index} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
                    {symbol}
                  </span>
                ))}
              </div>
            </div>
          )}
          {refData.filename && (
            <div>
              <span className="font-medium">Filename:</span>
              <span className="ml-2 text-gray-700">{refData.filename}</span>
            </div>
          )}
          {refData.is_likely_fake !== undefined && (
            <div>
              <span className="font-medium">Authenticity:</span>
              <span className={`ml-2 px-2 py-1 rounded text-xs font-medium ${
                refData.is_likely_fake ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
              }`}>
                {refData.is_likely_fake ? 'Likely Fake' : 'Appears Authentic'}
              </span>
            </div>
          )}
          {refData.source && (
            <div>
              <span className="font-medium">Source:</span>
              <span className="ml-2 text-gray-700">{refData.source}</span>
            </div>
          )}
          {refData.created_at && (
            <div>
              <span className="font-medium">Created:</span>
              <span className="ml-2 text-gray-700">{formatDate(refData.created_at)}</span>
            </div>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
      <div className="bg-dark-900 rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto border border-dark-primary">
        <div className="flex items-center justify-between p-6 border-b border-dark-primary">
          <h2 className="text-xl font-semibold text-dark-primary">
            {selectedNode ? 'Node Details' : 'Edge Details'}
          </h2>
          <button
            onClick={onClose}
            className="text-dark-muted hover:text-dark-primary transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="p-6">
          {selectedNode && (
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div 
                  className="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold"
                  style={{ 
                    backgroundColor: selectedNode.node_type === 'tip' ? '#3b82f6' :
                                   selectedNode.node_type === 'assessment' ? '#ef4444' :
                                   selectedNode.node_type === 'document' ? '#10b981' :
                                   selectedNode.node_type === 'stock' ? '#f59e0b' :
                                   selectedNode.node_type === 'complaint' ? '#8b5cf6' :
                                   selectedNode.node_type === 'advisor' ? '#06b6d4' : '#6b7280'
                  }}
                >
                  {selectedNode.node_type === 'tip' ? '💡' :
                   selectedNode.node_type === 'assessment' ? '⚠️' :
                   selectedNode.node_type === 'document' ? '📄' :
                   selectedNode.node_type === 'stock' ? '📈' :
                   selectedNode.node_type === 'complaint' ? '📢' :
                   selectedNode.node_type === 'advisor' ? '👤' : '●'}
                </div>
                <div>
                  <h3 className="font-semibold text-lg">{selectedNode.label || selectedNode.node_type}</h3>
                  <p className="text-gray-600 text-sm">{getNodeTypeDescription(selectedNode.node_type)}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium">Node ID:</span>
                  <p className="text-gray-700 font-mono text-xs mt-1">{selectedNode.id}</p>
                </div>
                <div>
                  <span className="font-medium">Reference ID:</span>
                  <p className="text-gray-700 font-mono text-xs mt-1">{selectedNode.reference_id}</p>
                </div>
                <div>
                  <span className="font-medium">Node Type:</span>
                  <p className="text-gray-700 mt-1 capitalize">{selectedNode.node_type}</p>
                </div>
                <div>
                  <span className="font-medium">Created:</span>
                  <p className="text-gray-700 mt-1">{formatDate(selectedNode.created_at)}</p>
                </div>
              </div>

              {selectedNode.position_x !== null && selectedNode.position_y !== null && (
                <div>
                  <span className="font-medium text-sm">Position:</span>
                  <p className="text-gray-700 text-sm mt-1">
                    X: {selectedNode.position_x}, Y: {selectedNode.position_y}
                  </p>
                </div>
              )}

              {Object.keys(selectedNode.metadata).length > 0 && (
                <div>
                  <span className="font-medium text-sm">Metadata:</span>
                  <div className="mt-2 p-3 bg-gray-50 rounded-lg">
                    <pre className="text-xs text-gray-700 whitespace-pre-wrap">
                      {JSON.stringify(selectedNode.metadata, null, 2)}
                    </pre>
                  </div>
                </div>
              )}

              {renderReferenceData(selectedNode.metadata)}
            </div>
          )}

          {selectedEdge && (
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center text-white font-bold">
                  →
                </div>
                <div>
                  <h3 className="font-semibold text-lg capitalize">{selectedEdge.relationship_type.replace('_', ' ')}</h3>
                  <p className="text-gray-600 text-sm">{getRelationshipDescription(selectedEdge.relationship_type)}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium">Edge ID:</span>
                  <p className="text-gray-700 font-mono text-xs mt-1">{selectedEdge.id}</p>
                </div>
                <div>
                  <span className="font-medium">Confidence:</span>
                  <div className="flex items-center gap-2 mt-1">
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-500 h-2 rounded-full" 
                        style={{ width: `${selectedEdge.confidence}%` }}
                      ></div>
                    </div>
                    <span className="text-gray-700">{selectedEdge.confidence}%</span>
                  </div>
                </div>
                <div>
                  <span className="font-medium">From Node:</span>
                  <p className="text-gray-700 font-mono text-xs mt-1">{selectedEdge.from_node_id}</p>
                </div>
                <div>
                  <span className="font-medium">To Node:</span>
                  <p className="text-gray-700 font-mono text-xs mt-1">{selectedEdge.to_node_id}</p>
                </div>
                <div>
                  <span className="font-medium">Relationship:</span>
                  <p className="text-gray-700 mt-1 capitalize">{selectedEdge.relationship_type.replace('_', ' ')}</p>
                </div>
                <div>
                  <span className="font-medium">Created:</span>
                  <p className="text-gray-700 mt-1">{formatDate(selectedEdge.created_at)}</p>
                </div>
              </div>

              {Object.keys(selectedEdge.metadata).length > 0 && (
                <div>
                  <span className="font-medium text-sm">Metadata:</span>
                  <div className="mt-2 p-3 bg-gray-50 rounded-lg">
                    <pre className="text-xs text-gray-700 whitespace-pre-wrap">
                      {JSON.stringify(selectedEdge.metadata, null, 2)}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="flex justify-end gap-3 p-6 border-t border-dark-primary bg-dark-800">
          <button
            onClick={onClose}
            className="px-4 py-2 text-dark-primary bg-dark-700 border border-dark-primary rounded-md hover:bg-dark-600 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

export default FraudChainDetailsModal