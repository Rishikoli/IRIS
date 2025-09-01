import { PDFAnalysisResponse } from '../services/api'
import RiskBadge from './RiskBadge'

interface PDFAnalysisResultsProps {
  analysis: PDFAnalysisResponse
}

const PDFAnalysisResults = ({ analysis }: PDFAnalysisResultsProps) => {
  const getRiskLevel = (score: number): 'Low' | 'Medium' | 'High' => {
    if (score >= 70) return 'Low'
    if (score >= 40) return 'Medium'
    return 'High'
  }

  const getSeverityColor = (severity: 'low' | 'medium' | 'high') => {
    switch (severity) {
      case 'low': return 'text-yellow-600 bg-yellow-100'
      case 'medium': return 'text-orange-600 bg-orange-100'
      case 'high': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const formatProcessingTime = (ms: number) => {
    if (ms < 1000) return `${ms}ms`
    return `${(ms / 1000).toFixed(1)}s`
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  return (
    <div className="bg-primary-900/30  rounded-lg shadow-md p-6 space-y-6">
      <div className="border-b pb-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-dark-primary">Analysis Results</h3>
          <RiskBadge 
            level={getRiskLevel(analysis.score)} 
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
            <p className="font-medium">{formatFileSize(analysis.file_size)}</p>
          </div>
          <div>
            <span className="text-gray-500">Processing Time:</span>
            <p className="font-medium">{formatProcessingTime(analysis.processing_time_ms)}</p>
          </div>
        </div>
      </div>

      <div>
        <h4 className="text-md font-semibold text-dark-primary mb-3">Authenticity Assessment</h4>
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Authenticity Score</span>
            <span className="text-2xl font-bold text-dark-primary">{analysis.score}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className={`h-2 rounded-full ${
                analysis.score >= 70 ? 'bg-green-500' : 
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

      {analysis.anomalies && analysis.anomalies.length > 0 && (
        <div>
          <h4 className="text-md font-semibold text-dark-primary mb-3">Detected Anomalies</h4>
          <div className="space-y-3">
            {analysis.anomalies.map((anomaly, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSeverityColor(anomaly.severity)}`}>
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

      <div className="text-xs text-gray-500 border-t pt-4">
        <div className="flex justify-between">
          <span>Analysis ID: {analysis.id}</span>
          <span>Analyzed: {new Date(analysis.created_at).toLocaleString()}</span>
        </div>
      </div>
    </div>
  )
}

export default PDFAnalysisResults