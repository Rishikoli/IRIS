import { useState } from 'react'
import TipAnalysisForm from '../components/TipAnalysisForm'
import RiskBadge from '../components/RiskBadge'
import UnifiedDashboard from '../components/UnifiedDashboard'
import PDFUpload from '../components/PDFUpload'
import Iridescence from '../components/Iridescence'
// import DrillDownModal from '../components/DrillDownModal'
import { tipApi, CheckTipResponse, pdfCheckApi, PDFAnalysisResponse } from '../services/api'

const DashboardPage = () => {
  const [activeTab, setActiveTab] = useState('overview')
  const [tipAnalysisResult, setTipAnalysisResult] = useState<CheckTipResponse | null>(null)
  const [tipAnalysisLoading, setTipAnalysisLoading] = useState(false)
  const [tipAnalysisError, setTipAnalysisError] = useState<string | null>(null)

  // PDF Analysis state
  const [pdfAnalysisResult, setPdfAnalysisResult] = useState<PDFAnalysisResponse | null>(null)
  const [pdfAnalysisLoading, setPdfAnalysisLoading] = useState(false)
  const [pdfAnalysisError, setPdfAnalysisError] = useState<string | null>(null)

  // Drill-down modal state - temporarily disabled
  // const [drillDownModal, setDrillDownModal] = useState({
  //   isOpen: false,
  //   dimension: 'sector' as 'sector' | 'region',
  //   key: ''
  // })

  // Tip Analysis Handler
  const handleAnalyzeTip = async (message: string) => {
    setTipAnalysisLoading(true)
    setTipAnalysisError(null)
    setTipAnalysisResult(null)

    try {
      const response = await tipApi.checkTip({
        message,
        source: 'dashboard'
      })
      setTipAnalysisResult(response.data)
    } catch (err: any) {
      console.error('Error analyzing tip:', err)
      setTipAnalysisError(
        err.response?.data?.detail ||
        'Failed to analyze the tip. Please try again later.'
      )
    } finally {
      setTipAnalysisLoading(false)
    }
  }

  // PDF Analysis Handler
  const handlePdfUpload = async (file: File) => {
    setPdfAnalysisLoading(true)
    setPdfAnalysisError(null)
    setPdfAnalysisResult(null)

    try {
      // Validate file type
      if (!file.type.includes('pdf')) {
        throw new Error('Please select a PDF file')
      }

      // Validate file size (10MB limit)
      const maxSize = 10 * 1024 * 1024 // 10MB
      if (file.size > maxSize) {
        throw new Error('File size must be less than 10MB')
      }

      const response = await pdfCheckApi.analyzePDF(file)
      setPdfAnalysisResult(response.data)
    } catch (err: any) {
      console.error('PDF analysis error:', err)

      if (err.response?.status === 413) {
        setPdfAnalysisError('File size exceeds the 10MB limit. Please select a smaller file.')
      } else if (err.response?.status === 400) {
        setPdfAnalysisError(err.response.data?.detail || 'Invalid file format. Please select a PDF file.')
      } else if (err.response?.status === 500) {
        setPdfAnalysisError('Server error while processing the PDF. Please try again later.')
      } else if (err.message) {
        setPdfAnalysisError(err.message)
      } else {
        setPdfAnalysisError('An unexpected error occurred while analyzing the PDF. Please try again.')
      }
    } finally {
      setPdfAnalysisLoading(false)
    }
  }

  const handlePdfReset = () => {
    setPdfAnalysisResult(null)
    setPdfAnalysisError(null)
  }

  // Handle heatmap cell click for drill-down
  const handleHeatmapCellClick = (key: string) => {
    // For now, show an alert with drill-down info
    alert(`Drill-down for heatmap cell: ${key}\n\nThis will show detailed fraud cases and statistics for this item.`)
  }

  const tabs = [
    { id: 'overview', name: 'Overview', icon: '📊' },
    { id: 'check-tip', name: 'Check Tip', icon: '🔍' },
    { id: 'verify-advisor', name: 'Verify Advisor', icon: '👤' },
    { id: 'upload-pdf', name: 'Upload PDF', icon: '📄' },
    { id: 'review', name: 'Review Queue', icon: '⚖️' }
  ]

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <UnifiedDashboard onHeatmapCellClick={handleHeatmapCellClick} />
        )

      case 'check-tip':
        return (
          <div className="space-y-6">
            <div className="bg-white dark:bg-dark-secondary rounded-lg shadow-md p-6 border border-gray-200 dark:border-dark-border">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-dark-text mb-4">
                Investment Tip Risk Analysis
              </h2>
              <p className="text-gray-600 dark:text-dark-muted">
                Analyze investment tips and messages for fraud indicators using AI-powered detection.
              </p>
            </div>

            {!tipAnalysisResult && (
              <TipAnalysisForm onSubmit={handleAnalyzeTip} loading={tipAnalysisLoading} />
            )}

            {tipAnalysisError && (
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/30 rounded-lg p-6">
                <div className="flex items-center space-x-3">
                  <span className="text-2xl">❌</span>
                  <div>
                    <h3 className="text-lg font-semibold text-red-900 dark:text-red-400">Analysis Failed</h3>
                    <p className="text-red-700 dark:text-red-300">{tipAnalysisError}</p>
                  </div>
                </div>
                <button
                  onClick={() => {
                    setTipAnalysisResult(null)
                    setTipAnalysisError(null)
                  }}
                  className="mt-4 bg-red-600 hover:bg-red-700 dark:bg-red-700 dark:hover:bg-red-600 text-white px-4 py-2 rounded-md transition-colors"
                >
                  Try Again
                </button>
              </div>
            )}

            {tipAnalysisResult && (
              <div className="space-y-6">
                <RiskBadge
                  level={tipAnalysisResult.assessment.level}
                  score={tipAnalysisResult.assessment.score}
                  reasons={tipAnalysisResult.assessment.reasons}
                />

                <div className="bg-primary-900/30  rounded-lg shadow-md p-6">
                  <h3 className="text-xl font-semibold text-dark-primary mb-4">Analysis Details</h3>
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-2">Stock Symbols Detected</h4>
                      {tipAnalysisResult.assessment.stock_symbols.length > 0 ? (
                        <div className="flex flex-wrap gap-2">
                          {tipAnalysisResult.assessment.stock_symbols.map((symbol, index) => (
                            <span key={index} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              {symbol}
                            </span>
                          ))}
                        </div>
                      ) : (
                        <p className="text-sm text-gray-500">No stock symbols detected</p>
                      )}
                    </div>

                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-2">Advisor Information</h4>
                      {tipAnalysisResult.assessment.advisor ? (
                        <div className="text-sm">
                          <p className="font-medium">{tipAnalysisResult.assessment.advisor.name}</p>
                          <p className="text-gray-600">Status: {tipAnalysisResult.assessment.advisor.registration_status}</p>
                        </div>
                      ) : (
                        <p className="text-sm text-gray-500">No advisor mentioned</p>
                      )}
                    </div>
                  </div>

                  <div className="mt-6 pt-4 border-t border-gray-200">
                    <div className="flex justify-between items-center text-sm text-gray-500">
                      <span>Confidence: {Math.round(tipAnalysisResult.assessment.confidence * 100)}%</span>
                      <span>Analyzed: {new Date(tipAnalysisResult.assessment.timestamp).toLocaleString()}</span>
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => {
                    setTipAnalysisResult(null)
                    setTipAnalysisError(null)
                  }}
                  className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors"
                >
                  Analyze Another Tip
                </button>
              </div>
            )}
          </div>
        )

      case 'verify-advisor':
        return (
          <div className="space-y-6">
            <div className="bg-primary-900/30  rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-bold text-dark-primary mb-4">
                Advisor Verification
              </h2>
              <p className="text-dark-primary">
                Verify if a financial advisor is registered with SEBI and check their credentials.
              </p>

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
                <p className="text-yellow-800 text-sm">
                  <strong>Coming Soon:</strong> SEBI API integration for real-time advisor verification.
                </p>
              </div>

              <div className="space-y-4">
                <div>
                  <label htmlFor="advisor-name" className="block text-sm font-medium text-gray-700 mb-2">
                    Advisor Name or Registration ID
                  </label>
                  <input
                    type="text"
                    id="advisor-name"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter advisor name or SEBI registration ID..."
                    disabled
                  />
                </div>

                <button
                  type="button"
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                  disabled
                >
                  Verify Advisor
                </button>
              </div>
            </div>
          </div>
        )

      case 'upload-pdf':
        return (
          <div className="space-y-6">
            <div className="bg-primary-900/30  rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-bold text-dark-primary mb-4">
                PDF Document Authentication
              </h2>
              <p className="text-dark-primary mb-6">
                Upload PDF documents to verify their authenticity and detect potential fraud markers.
                Our AI-powered system analyzes document structure, content, and metadata to detect potential forgeries.
              </p>

              {/* File Upload Section */}
              {!pdfAnalysisResult && (
                <PDFUpload
                  onFileSelect={handlePdfUpload}
                  loading={pdfAnalysisLoading}
                  disabled={pdfAnalysisLoading}
                />
              )}

              {/* Error Display */}
              {pdfAnalysisError && (
                <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <svg className="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-red-800">
                        Upload Error
                      </h3>
                      <div className="mt-2 text-sm text-red-700">
                        <p>{pdfAnalysisError}</p>
                      </div>
                      <div className="mt-4">
                        <button
                          type="button"
                          onClick={handlePdfReset}
                          className="bg-red-100 text-red-800 px-3 py-1 rounded text-sm hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                        >
                          Try Again
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Loading State */}
              {pdfAnalysisLoading && (
                <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
                    </div>
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-blue-800">
                        Analyzing PDF...
                      </h3>
                      <p className="text-sm text-blue-700 mt-1">
                        This may take a few moments while we extract text and analyze the document...
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Analysis Results */}
            {pdfAnalysisResult && (
              <div className="space-y-4">
                {/* PDF Analysis Results Component */}
                <div className="bg-primary-900/30  rounded-lg shadow-md p-6 space-y-6">
                  <div className="border-b pb-4">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-dark-primary">Analysis Results</h3>
                      <RiskBadge
                        level={pdfAnalysisResult.score >= 70 ? 'Low' : pdfAnalysisResult.score >= 40 ? 'Medium' : 'High'}
                        score={pdfAnalysisResult.score}
                        reasons={[`Authenticity Score: ${pdfAnalysisResult.score}%`]}
                      />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500">Filename:</span>
                        <p className="font-medium truncate">{pdfAnalysisResult.filename}</p>
                      </div>
                      <div>
                        <span className="text-gray-500">File Size:</span>
                        <p className="font-medium">
                          {pdfAnalysisResult.file_size < 1024 ? `${pdfAnalysisResult.file_size} B` :
                            pdfAnalysisResult.file_size < 1024 * 1024 ? `${(pdfAnalysisResult.file_size / 1024).toFixed(1)} KB` :
                              `${(pdfAnalysisResult.file_size / (1024 * 1024)).toFixed(1)} MB`}
                        </p>
                      </div>
                      <div>
                        <span className="text-gray-500">Processing Time:</span>
                        <p className="font-medium">
                          {pdfAnalysisResult.processing_time_ms < 1000 ? `${pdfAnalysisResult.processing_time_ms}ms` :
                            `${(pdfAnalysisResult.processing_time_ms / 1000).toFixed(1)}s`}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Authenticity Assessment */}
                  <div>
                    <h4 className="text-md font-semibold text-dark-primary mb-3">Authenticity Assessment</h4>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-700">Authenticity Score</span>
                        <span className="text-2xl font-bold text-dark-primary">{pdfAnalysisResult.score}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${pdfAnalysisResult.score >= 70 ? 'bg-green-500' :
                            pdfAnalysisResult.score >= 40 ? 'bg-yellow-500' : 'bg-red-500'
                            }`}
                          style={{ width: `${pdfAnalysisResult.score}%` }}
                        ></div>
                      </div>
                      <div className="mt-2">
                        {pdfAnalysisResult.is_likely_fake ? (
                          <div className="flex items-center text-red-600">
                            <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                            </svg>
                            <span className="text-sm font-medium">Document appears to be suspicious</span>
                          </div>
                        ) : (
                          <div className="flex items-center text-green-600">
                            <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                            </svg>
                            <span className="text-sm font-medium">Document appears to be authentic</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Detected Anomalies */}
                  {pdfAnalysisResult.anomalies && pdfAnalysisResult.anomalies.length > 0 && (
                    <div>
                      <h4 className="text-md font-semibold text-dark-primary mb-3">Detected Anomalies</h4>
                      <div className="space-y-3">
                        {pdfAnalysisResult.anomalies.map((anomaly, index) => (
                          <div key={index} className="border rounded-lg p-4">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center mb-2">
                                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${anomaly.severity === 'low' ? 'text-yellow-600 bg-yellow-100' :
                                    anomaly.severity === 'medium' ? 'text-orange-600 bg-orange-100' :
                                      anomaly.severity === 'high' ? 'text-red-600 bg-red-100' :
                                        'text-gray-600 bg-gray-100'
                                    }`}>
                                    {anomaly.severity.toUpperCase()}
                                  </span>
                                  <span className="ml-2 text-sm font-medium text-dark-primary">{anomaly.type}</span>
                                </div>
                                <p className="text-sm text-gray-700">{anomaly.description}</p>
                                {anomaly.details && (
                                  <div className="mt-2 text-xs text-gray-500">
                                    <pre className="whitespace-pre-wrap">{JSON.stringify(anomaly.details, null, 2)}</pre>
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Warning for suspicious documents */}
                  {pdfAnalysisResult.is_likely_fake && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                      <div className="flex">
                        <div className="flex-shrink-0">
                          <svg className="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                          </svg>
                        </div>
                        <div className="ml-3">
                          <h3 className="text-sm font-medium text-red-800">
                            ⚠️ Suspicious Document Detected
                          </h3>
                          <div className="mt-2 text-sm text-red-700">
                            <p>
                              This document shows signs of potential fraud or manipulation.
                              Please exercise extreme caution and verify the document through official channels before taking any action.
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* OCR Text Preview */}
                  {pdfAnalysisResult.ocr_text && (
                    <div>
                      <h4 className="text-md font-semibold text-dark-primary mb-3">Extracted Text Preview</h4>
                      <div className="bg-gray-50 rounded-lg p-4 max-h-40 overflow-y-auto">
                        <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                          {pdfAnalysisResult.ocr_text.substring(0, 500)}
                          {pdfAnalysisResult.ocr_text.length > 500 && '...'}
                        </pre>
                      </div>
                    </div>
                  )}

                  {/* Analysis Metadata */}
                  <div className="text-xs text-gray-500 border-t pt-4">
                    <div className="flex justify-between">
                      <span>Analysis ID: {pdfAnalysisResult.id}</span>
                      <span>Analyzed: {new Date(pdfAnalysisResult.created_at).toLocaleString()}</span>
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="bg-primary-900/30  rounded-lg shadow-md p-6">
                  <div className="flex flex-col sm:flex-row gap-4">
                    <button
                      onClick={handlePdfReset}
                      className="flex-1 bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
                    >
                      Analyze Another Document
                    </button>

                    <button
                      onClick={() => {
                        const dataStr = JSON.stringify(pdfAnalysisResult, null, 2)
                        const dataBlob = new Blob([dataStr], { type: 'application/json' })
                        const url = URL.createObjectURL(dataBlob)
                        const link = document.createElement('a')
                        link.href = url
                        link.download = `pdf-analysis-${pdfAnalysisResult.id}.json`
                        link.click()
                        URL.revokeObjectURL(url)
                      }}
                      className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                    >
                      Download Analysis Report
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Information Section */}
            <div className="bg-gray-50 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-dark-primary mb-4">How PDF Authentication Works</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium text-dark-primary mb-2">Document Analysis</h4>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• OCR text extraction and validation</li>
                    <li>• Metadata and structure analysis</li>
                    <li>• Digital signature verification</li>
                    <li>• Font and formatting consistency checks</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-medium text-dark-primary mb-2">AI-Powered Detection</h4>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• Content authenticity assessment</li>
                    <li>• Fraud pattern recognition</li>
                    <li>• Regulatory document validation</li>
                    <li>• Anomaly detection and scoring</li>
                  </ul>
                </div>
              </div>

              <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-sm text-yellow-800">
                  <strong>Disclaimer:</strong> This analysis is for informational purposes only.
                  Always verify important documents through official channels and regulatory authorities.
                </p>
              </div>
            </div>
          </div>
        )

      case 'forecast':
        return (
          <UnifiedDashboard onHeatmapCellClick={handleHeatmapCellClick} />
        )

      case 'review':
        return (
          <div className="space-y-6">
            <div className="bg-primary-900/30  rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-bold text-dark-primary mb-4">
                Human-in-the-Loop Review
              </h2>
              <p className="text-dark-primary">
                Review AI decisions and provide overrides with explanations for continuous improvement.
              </p>

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
                <p className="text-yellow-800 text-sm">
                  <strong>Coming Soon:</strong> Review workflow and decision override system.
                </p>
              </div>
            </div>

            <div className="bg-primary-900/30  rounded-lg shadow-md">
              <div className="px-6 py-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h3 className="text-xl font-semibold text-dark-primary">Review Queue</h3>
                  <span className="px-3 py-1 text-sm font-medium bg-blue-100 text-blue-800 rounded-full">
                    3 Pending
                  </span>
                </div>
              </div>

              <div className="p-6">
                <div className="space-y-4">
                  {[
                    { id: 1, type: 'Tip Analysis', confidence: 88, decision: 'High risk investment tip with guaranteed returns promise' },
                    { id: 2, type: 'PDF Check', confidence: 92, decision: 'Document shows signs of digital manipulation' },
                    { id: 3, type: 'Advisor Verification', confidence: 85, decision: 'Advisor claims unverifiable credentials' }
                  ].map((item) => (
                    <div key={item.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-3">
                          <span className="text-sm font-medium text-dark-primary">
                            {item.type} #{item.id.toString().padStart(3, '0')}
                          </span>
                          <span className="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded-full">
                            Pending Review
                          </span>
                        </div>
                        <span className="text-sm text-gray-500">
                          AI Confidence: {item.confidence}%
                        </span>
                      </div>

                      <p className="text-sm text-gray-600 mb-3">
                        AI Decision: {item.decision}
                      </p>

                      <div className="flex space-x-2">
                        <button
                          type="button"
                          className="px-3 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-md hover:bg-green-200 disabled:opacity-50 disabled:cursor-not-allowed"
                          disabled
                        >
                          ✓ Approve
                        </button>
                        <button
                          type="button"
                          className="px-3 py-1 text-xs font-medium bg-red-100 text-red-800 rounded-md hover:bg-red-200 disabled:opacity-50 disabled:cursor-not-allowed"
                          disabled
                        >
                          ✗ Override
                        </button>
                        <button
                          type="button"
                          className="px-3 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-md hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
                          disabled
                        >
                          📋 Details
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* IRIS Platform Header */}

      {/* GradientBlinds Section */}
      <div className="mb-8 relative rounded-2xl overflow-hidden h-32 bg-gradient-to-br from-blue-100 to-purple-200 dark:from-blue-50 dark:to-purple-100">
        <Iridescence
          className="absolute inset-0"
          color={[1, 1, 1]}
          mouseReact={false}
          amplitude={3}
          speed={0.8}
        />


        <div className="relative z-10 flex items-center justify-center h-full text-center">
          <div>
            <h2 className="text-3xl font-bold text-white mb-2 drop-shadow-lg">
              IRIS RegTech 
            </h2>
            <p className="text-white drop-shadow-md">
              Comprehensive fraud detection and regulatory compliance dashboard
            </p>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white dark:bg-dark-secondary rounded-lg shadow-lg mb-6 border border-gray-200 dark:border-dark-border">
        <div className="border-b border-gray-200 dark:border-dark-border">
          <nav className="-mb-px flex space-x-8 px-6" aria-label="Tabs">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`${activeTab === tab.id
                  ? 'border-blue-500 dark:border-dark-accent text-blue-600 dark:text-dark-accent bg-blue-50 dark:bg-dark-hover'
                  : 'border-transparent text-gray-500 dark:text-dark-muted hover:text-gray-700 dark:hover:text-dark-text hover:border-gray-300 dark:hover:border-dark-border hover:bg-gray-50 dark:hover:bg-dark-hover'
                  } whitespace-nowrap py-4 px-3 border-b-2 font-medium text-sm flex items-center space-x-2 rounded-t-md transition-all duration-200`}
              >
                <span>{tab.icon}</span>
                <span>{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Tab Content */}
      <div className="min-h-screen">
        {renderTabContent()}
      </div>

      {/* Drill-down Modal - Temporarily disabled due to import issues */}
      {/* <DrillDownModal
        isOpen={drillDownModal.isOpen}
        onClose={() => setDrillDownModal({ ...drillDownModal, isOpen: false })}
        dimension={drillDownModal.dimension}
        key={drillDownModal.key}
        fromDate={fromDate}
        toDate={toDate}
      /> */}
    </div>
  )
}

export default DashboardPage