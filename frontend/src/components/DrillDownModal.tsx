import React, { useState, useEffect } from 'react';
import ConsolidatedDataModal from './ConsolidatedDataModal';

interface DrillDownModalProps {
  isOpen: boolean;
  onClose: () => void;
  dimension: 'sector' | 'region';
  key: string;
  fromDate?: string;
  toDate?: string;
}

interface DrillDownData {
  statistics: {
    total_cases: number;
    high_risk_cases: number;
    medium_risk_cases: number;
    low_risk_cases: number;
    average_risk_score: number;
  };
  cases: Array<{
    id: string;
    message: string;
    risk_level: string;
    risk_score: number;
    confidence: number;
    created_at: string;
  }>;
}

const DrillDownModal: React.FC<DrillDownModalProps> = ({
  isOpen,
  onClose,
  dimension,
  key,
  fromDate,
  toDate
}) => {
  const [data, setData] = useState<DrillDownData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showConsolidatedModal, setShowConsolidatedModal] = useState(false);

  useEffect(() => {
    if (isOpen && key) {
      fetchDrillDownData();
    }
  }, [isOpen, key, dimension, fromDate, toDate]);

  const fetchDrillDownData = async () => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();
      if (fromDate) params.append('from_date', fromDate);
      if (toDate) params.append('to_date', toDate);
      
      const response = await fetch(`/api/heatmap-drill-down/${dimension}/${key}?${params}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch drill-down data');
      }
      
      const result = await response.json();
      setData(result);
    } catch (err: any) {
      console.error('Error fetching drill-down data:', err);
      setError(err.message || 'Failed to load drill-down data');
    } finally {
      setLoading(false);
    }
  };

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'High':
        return 'bg-red-100 text-red-800';
      case 'Medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'Low':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-primary-900/30  rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-xl font-bold text-dark-primary">
              {dimension === 'sector' ? 'Sector' : 'Region'} Details: {key}
            </h2>
            <div className="flex items-center space-x-2 mt-2">
              <button
                onClick={() => setShowConsolidatedModal(true)}
                className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full hover:bg-blue-200 transition-colors"
              >
                🔍 Multi-Source Analysis
              </button>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        </div>

        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          {loading && (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <span className="ml-3 text-gray-600">Loading...</span>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-6">
              <p className="text-red-700">{error}</p>
              <button
                onClick={fetchDrillDownData}
                className="mt-2 px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
              >
                Retry
              </button>
            </div>
          )}

          {data && !loading && !error && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div className="bg-gray-50 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-dark-primary">{data.statistics.total_cases}</div>
                  <div className="text-sm text-gray-600">Total Cases</div>
                </div>
                <div className="bg-red-50 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-red-600">{data.statistics.high_risk_cases}</div>
                  <div className="text-sm text-gray-600">High Risk</div>
                </div>
                <div className="bg-yellow-50 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-yellow-600">{data.statistics.medium_risk_cases}</div>
                  <div className="text-sm text-gray-600">Medium Risk</div>
                </div>
                <div className="bg-green-50 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-green-600">{data.statistics.low_risk_cases}</div>
                  <div className="text-sm text-gray-600">Low Risk</div>
                </div>
                <div className="bg-blue-50 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-blue-600">{data.statistics.average_risk_score.toFixed(1)}</div>
                  <div className="text-sm text-gray-600">Avg Score</div>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-dark-primary mb-4">Recent Cases</h3>
                {data.cases.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    No cases found for this {dimension}.
                  </div>
                ) : (
                  <div className="space-y-3">
                    {data.cases.map((case_item) => (
                      <div key={case_item.id} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-start justify-between mb-2">
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getRiskLevelColor(case_item.risk_level)}`}>
                            {case_item.risk_level} Risk
                          </span>
                          <span className="text-xs text-gray-500">
                            {new Date(case_item.created_at).toLocaleString()}
                          </span>
                        </div>
                        <p className="text-sm text-gray-700 mb-2">{case_item.message}</p>
                        <div className="text-xs text-gray-600">
                          Score: {case_item.risk_score} | Confidence: {case_item.confidence}%
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        <div className="flex justify-end p-6 border-t border-gray-200">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-primary-900/30  border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Close
          </button>
        </div>
      </div>

      {/* Consolidated Data Modal */}
      <ConsolidatedDataModal
        isOpen={showConsolidatedModal}
        onClose={() => setShowConsolidatedModal(false)}
        sector={dimension === 'sector' ? key : 'Technology'} // Default sector if viewing by region
        region={dimension === 'region' ? key : 'Mumbai'} // Default region if viewing by sector
      />
    </div>
  );
};

export default DrillDownModal;