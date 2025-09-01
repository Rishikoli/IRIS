import { useState } from 'react'
import PDFUpload from '../components/PDFUpload'
import PDFPreview from '../components/PDFPreview'
import { pdfCheckApi, PDFAnalysisResponse } from '../services/api'
import RiskBadge from '../components/RiskBadge'

const UploadPDFPage = () => {
  const [loading, setLoading] = useState(false)
  const [analysis, setAnalysis] = useState<PDFAnalysisResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [showPreview, setShowPreview] = useState(false)

  const handleFileSelect = async (file: File) => {
    setSelectedFile(file)
    setError(null)
    setAnalysis(null)
    setShowPreview(true)
    setLoading(true)

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
      setAnalysis(response.data)
    } catch (err: any) {
      console.error('PDF analysis error:', err)

      if (err.response?.status === 413) {
        setError('File size exceeds the 10MB limit. Please select a smaller file.')
      } else if (err.response?.status === 400) {
        setError(err.response.data?.detail || 'Invalid file format. Please select a PDF file.')
      } else if (err.response?.status === 500) {
        setError('Server error while processing the PDF. Please try again later.')
      } else if (err.message) {
        setError(err.message)
      } else {
        setError('An unexpected error occurred while analyzing the PDF. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setSelectedFile(null)
    setAnalysis(null)
    setError(null)
    setShowPreview(false)
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="bg-primary-900/30  rounded-lg shadow-md p-8">
        <h1 className="text-3xl font-bold text-dark-primary mb-6">
          PDF Document Authentication
        </h1>
        <p className="text-gray-600 mb-8">
          Upload PDF documents to verify their authenticity and check for fraud markers.
          Our AI-powered system analyzes document structure, content, and metadata to detect potential forgeries.
        </p>

        {/* File Upload Section */}
        {!analysis && !showPreview && (
          <PDFUpload
            onFileSelect={handleFileSelect}
            loading={loading}
            disabled={loading}
          />
        )}

        {/* PDF Preview Section */}
        {showPreview && selectedFile && !analysis && (
          <PDFPreview
            file={selectedFile}
            onClose={() => setShowPreview(false)}
          />
        )}

        {/* Error Display */}
        {error && (
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
                  <p>{error}</p>
                </div>
                <div className="mt-4">
                  <button
                    type="button"
                    onClick={handleReset}
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
        {loading && selectedFile && (
          <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-blue-800">
                  Analyzing PDF: {selectedFile.name}
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
      {analysis && (
        <div className="space-y-4">
          {/* PDF Analysis Results Component */}
          <div className="bg-primary-900/30  rounded-lg shadow-md p-6 space-y-6">
            <div className="border-b pb-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-dark-primary">Analysis Results</h3>
                <RiskBadge
                  level={analysis.score >= 70 ? 'Low' : analysis.score >= 40 ? 'Medium' : 'High'}
                  score={analysis.score}
                  reasons={[`Authenticity Score: ${analysis.score}%`]}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Filename:</span>
                  <p className="font-medium truncate">{analysis.filename}</p>
                </div>
                <div>
                  <span className="text-gray-500">File Size:</span>
                  <p className="font-medium">
                    {analysis.file_size < 1024 ? `${analysis.file_size} B` :
                      analysis.file_size < 1024 * 1024 ? `${(analysis.file_size / 1024).toFixed(1)} KB` :
                        `${(analysis.file_size / (1024 * 1024)).toFixed(1)} MB`}
                  </p>
                </div>
                <div>
                  <span className="text-gray-500">Processing Time:</span>
                  <p className="font-medium">
                    {analysis.processing_time_ms < 1000 ? `${analysis.processing_time_ms}ms` :
                      `${(analysis.processing_time_ms / 1000).toFixed(1)}s`}
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
                  <span className="text-2xl font-bold text-dark-primary">{analysis.score}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${analysis.score >= 70 ? 'bg-green-500' :
                      analysis.score >= 40 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                    style={{ width: `${analysis.score}%` }}
                  ></div>
                </div>
                <div className="mt-2">
                  {analysis.is_likely_fake ? (
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

            {/* Enhanced Multi-Source Validation */}
            {analysis.enhanced_validation && (
              <div>
                <h4 className="text-md font-semibold text-dark-primary mb-3">
                  🔍 Multi-Source Validation Results
                </h4>
                <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 space-y-4">
                  
                  {/* Validation Summary */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">
                        {analysis.enhanced_validation.overall_authenticity_score}%
                      </div>
                      <div className="text-sm text-gray-600">Enhanced Score</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-purple-600">
                        {(analysis.enhanced_validation.validation_confidence * 100).toFixed(0)}%
                      </div>
                      <div className="text-sm text-gray-600">Confidence</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">
                        {analysis.enhanced_validation.validation_sources.length}
                      </div>
                      <div className="text-sm text-gray-600">Sources Checked</div>
                    </div>
                  </div>

                  {/* Validation Sources */}
                  <div>
                    <h5 className="font-medium text-gray-800 mb-2">Data Sources Validated:</h5>
                    <div className="flex flex-wrap gap-2">
                      {analysis.enhanced_validation.validation_sources.map((source, index) => (
                        <span key={index} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                          {source.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Cross-Source Confirmations */}
                  {analysis.enhanced_validation.cross_source_confirmations.length > 0 && (
                    <div>
                      <h5 className="font-medium text-green-800 mb-2">✅ Confirmations:</h5>
                      <ul className="space-y-1">
                        {analysis.enhanced_validation.cross_source_confirmations.map((confirmation, index) => (
                          <li key={index} className="text-sm text-green-700 flex items-start">
                            <span className="text-green-500 mr-2">•</span>
                            {confirmation}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Cross-Source Flags */}
                  {analysis.enhanced_validation.cross_source_flags.length > 0 && (
                    <div>
                      <h5 className="font-medium text-red-800 mb-2">⚠️ Red Flags:</h5>
                      <ul className="space-y-1">
                        {analysis.enhanced_validation.cross_source_flags.map((flag, index) => (
                          <li key={index} className="text-sm text-red-700 flex items-start">
                            <span className="text-red-500 mr-2">•</span>
                            {flag}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Company Verification Results */}
                  {analysis.enhanced_validation.company_verification && (
                    <div className="border-t pt-4">
                      <h5 className="font-medium text-gray-800 mb-2">🏢 Company Verification:</h5>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-gray-600">Verified Companies:</span>
                          <span className="ml-2 font-medium text-green-600">
                            {analysis.enhanced_validation.company_verification.companies_verified?.length || 0}
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-600">Not Found:</span>
                          <span className="ml-2 font-medium text-red-600">
                            {analysis.enhanced_validation.company_verification.companies_not_found?.length || 0}
                          </span>
                        </div>
                      </div>
                      
                      {analysis.enhanced_validation.company_verification.companies_verified?.length > 0 && (
                        <div className="mt-2">
                          <span className="text-xs text-gray-500">Verified: </span>
                          {analysis.enhanced_validation.company_verification.companies_verified.map((company: any, index: number) => (
                            <span key={index} className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded mr-1">
                              {company.symbol} - {company.name}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* News Correlation */}
                  {analysis.enhanced_validation.news_correlation && (
                    <div className="border-t pt-4">
                      <h5 className="font-medium text-gray-800 mb-2">📰 News Correlation:</h5>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                        <div>
                          <span className="text-gray-600">Relevant Articles:</span>
                          <span className="ml-2 font-medium">
                            {analysis.enhanced_validation.news_correlation.relevant_articles?.length || 0}
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-600">Supporting:</span>
                          <span className="ml-2 font-medium text-green-600">
                            {analysis.enhanced_validation.news_correlation.supporting_news?.length || 0}
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-600">Contradictory:</span>
                          <span className="ml-2 font-medium text-red-600">
                            {analysis.enhanced_validation.news_correlation.contradictory_news?.length || 0}
                          </span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Trend Analysis */}
                  {analysis.enhanced_validation.trend_analysis && (
                    <div className="border-t pt-4">
                      <h5 className="font-medium text-gray-800 mb-2">📈 Trend Analysis:</h5>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-gray-600">Trend Spikes:</span>
                          <span className="ml-2 font-medium">
                            {analysis.enhanced_validation.trend_analysis.trend_spikes?.length || 0}
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-600">Fraud Correlations:</span>
                          <span className="ml-2 font-medium text-red-600">
                            {analysis.enhanced_validation.trend_analysis.fraud_correlations?.length || 0}
                          </span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* AI Content Analysis */}
                  {analysis.enhanced_validation.ai_content_analysis && (
                    <div className="border-t pt-4">
                      <h5 className="font-medium text-gray-800 mb-2">🤖 Enhanced AI Analysis:</h5>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-gray-600">AI Authenticity Score:</span>
                          <span className="ml-2 font-medium">
                            {analysis.enhanced_validation.ai_content_analysis.authenticity_score}%
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-600">AI Confidence:</span>
                          <span className="ml-2 font-medium">
                            {((analysis.enhanced_validation.ai_content_analysis.confidence || 0) * 100).toFixed(0)}%
                          </span>
                        </div>
                      </div>
                      
                      {analysis.enhanced_validation.ai_content_analysis.entity_consistency && (
                        <div className="mt-2 text-xs">
                          <span className="text-gray-500">Entity Consistency: </span>
                          <span className={`px-2 py-1 rounded ${
                            analysis.enhanced_validation.ai_content_analysis.entity_consistency.companies_legitimate 
                              ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                          }`}>
                            Companies: {analysis.enhanced_validation.ai_content_analysis.entity_consistency.companies_legitimate ? 'Valid' : 'Invalid'}
                          </span>
                          <span className={`ml-1 px-2 py-1 rounded ${
                            analysis.enhanced_validation.ai_content_analysis.entity_consistency.regulatory_language_accurate 
                              ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                          }`}>
                            Language: {analysis.enhanced_validation.ai_content_analysis.entity_consistency.regulatory_language_accurate ? 'Accurate' : 'Inaccurate'}
                          </span>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Enhanced Recommendations */}
                  {analysis.enhanced_validation.recommendations.length > 0 && (
                    <div className="border-t pt-4">
                      <h5 className="font-medium text-gray-800 mb-2">💡 Enhanced Recommendations:</h5>
                      <ul className="space-y-1">
                        {analysis.enhanced_validation.recommendations.map((recommendation, index) => (
                          <li key={index} className="text-sm text-gray-700 flex items-start">
                            <span className="text-blue-500 mr-2">•</span>
                            {recommendation}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Processing Info */}
                  <div className="border-t pt-4 text-xs text-gray-500">
                    <div className="flex justify-between">
                      <span>Enhanced validation time: {analysis.enhanced_validation.processing_time_ms}ms</span>
                      <span>Sources: {Object.keys(analysis.enhanced_validation.sources_checked).join(', ')}</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Detected Anomalies */}
            {analysis.anomalies && analysis.anomalies.length > 0 && (
              <div>
                <h4 className="text-md font-semibold text-dark-primary mb-3">Detected Anomalies</h4>
                <div className="space-y-3">
                  {analysis.anomalies.map((anomaly, index) => (
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
            {analysis.is_likely_fake && (
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
            {analysis.ocr_text && (
              <div>
                <h4 className="text-md font-semibold text-dark-primary mb-3">Extracted Text Preview</h4>
                <div className="bg-gray-50 rounded-lg p-4 max-h-40 overflow-y-auto">
                  <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                    {analysis.ocr_text.substring(0, 500)}
                    {analysis.ocr_text.length > 500 && '...'}
                  </pre>
                </div>
              </div>
            )}

            {/* Analysis Metadata */}
            <div className="text-xs text-gray-500 border-t pt-4">
              <div className="flex justify-between">
                <span>Analysis ID: {analysis.id}</span>
                <span>Analyzed: {new Date(analysis.created_at).toLocaleString()}</span>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="bg-primary-900/30  rounded-lg shadow-md p-6">
            <div className="flex flex-col sm:flex-row gap-4">
              <button
                onClick={handleReset}
                className="flex-1 bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
              >
                Analyze Another Document
              </button>

              <button
                onClick={() => {
                  const dataStr = JSON.stringify(analysis, null, 2)
                  const dataBlob = new Blob([dataStr], { type: 'application/json' })
                  const url = URL.createObjectURL(dataBlob)
                  const link = document.createElement('a')
                  link.href = url
                  link.download = `pdf-analysis-${analysis.id}.json`
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
        <h3 className="text-lg font-semibold text-dark-primary mb-4">Enhanced PDF Authentication with Multi-Source Validation</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <h4 className="font-medium text-dark-primary mb-2">📄 Document Analysis</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• OCR text extraction and validation</li>
              <li>• Metadata and structure analysis</li>
              <li>• Digital signature verification</li>
              <li>• Font and formatting consistency checks</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-dark-primary mb-2">🤖 AI-Powered Detection</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Content authenticity assessment</li>
              <li>• Fraud pattern recognition</li>
              <li>• Regulatory document validation</li>
              <li>• Entity consistency verification</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-dark-primary mb-2">🔍 Multi-Source Validation</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Financial market data cross-reference (FMP)</li>
              <li>• Real-time news correlation (Economic Times)</li>
              <li>• Search trend analysis (Google Trends)</li>
              <li>• Company verification and fraud alerts</li>
            </ul>
          </div>
        </div>

        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h5 className="font-medium text-blue-800 mb-2">🚀 Enhanced Features</h5>
            <ul className="text-sm text-blue-700 space-y-1">
              <li>• Cross-validates company mentions with live financial data</li>
              <li>• Checks for recent fraud-related news about mentioned entities</li>
              <li>• Analyzes search trends for fraud indicators</li>
              <li>• Provides confidence scores from multiple data sources</li>
            </ul>
          </div>
          <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
            <h5 className="font-medium text-green-800 mb-2">✅ Validation Sources</h5>
            <ul className="text-sm text-green-700 space-y-1">
              <li>• FMP API: Real-time market and company data</li>
              <li>• Economic Times: Latest financial news scraping</li>
              <li>• Google Trends: Fraud-related search patterns</li>
              <li>• Gemini AI: Enhanced content analysis</li>
            </ul>
          </div>
        </div>

        <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-sm text-yellow-800">
            <strong>Enhanced Disclaimer:</strong> This multi-source analysis provides comprehensive validation but is for informational purposes only.
            The system cross-references multiple data sources including financial markets, news, and search trends to provide enhanced authenticity assessment.
            Always verify critical documents through official regulatory channels.
          </p>
        </div>
      </div>
    </div>
  )
}

export default UploadPDFPage