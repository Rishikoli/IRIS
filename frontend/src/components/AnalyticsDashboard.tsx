import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import axios from 'axios';
import api from '../services/api';
import { ExportUtils } from './ExportUtils';
import RealTimeMetrics from './RealTimeMetrics';
import ComparativeAnalysis from './ComparativeAnalysis';
import DrillDownAnalysis from './DrillDownAnalysis';

interface PlatformSummary {
  overview: {
    total_tips_analyzed: number;
    total_documents_verified: number;
    total_fraud_chains_detected: number;
    total_human_reviews: number;
    platform_uptime_days: number;
  };
  risk_analysis: {
    risk_distribution: Record<string, number>;
    high_risk_percentage: number;
    avg_ai_confidence: number;
    low_confidence_cases: number;
  };
  document_verification: {
    authentic_documents: number;
    fake_documents: number;
    avg_authenticity_score: number;
    total_processed: number;
  };
  recent_activity: {
    tips_last_7_days: number;
    documents_last_7_days: number;
    reviews_last_7_days: number;
  };
  review_system: {
    pending_reviews: number;
    completed_reviews: number;
    review_completion_rate: number;
  };
}

interface FraudTrend {
  date: string;
  high_risk: number;
  medium_risk: number;
  low_risk: number;
  total: number;
}

interface SectorData {
  sector: string;
  total_cases: number;
  high_risk_cases: number;
  high_risk_percentage: number;
  risk_level: string;
}

interface RegionalData {
  region: string;
  total_cases: number;
  high_risk_cases: number;
  high_risk_percentage: number;
  population_category: string;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

const AnalyticsDashboard: React.FC = () => {
  const [summary, setSummary] = useState<PlatformSummary | null>(null);
  const [fraudTrends, setFraudTrends] = useState<FraudTrend[]>([]);
  const [sectorData, setSectorData] = useState<SectorData[]>([]);
  const [regionalData, setRegionalData] = useState<RegionalData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTimeRange, setSelectedTimeRange] = useState(30);
  const [drillDownModal, setDrillDownModal] = useState<{
    isOpen: boolean;
    title: string;
    data: any;
    type: 'sector' | 'region' | 'trend' | 'document';
  }>({
    isOpen: false,
    title: '',
    data: null,
    type: 'sector'
  });

  useEffect(() => {
    fetchAnalyticsData();
  }, [selectedTimeRange]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Use shared API client which routes through Vite proxy to backend (baseURL: /api)
      const [summaryRes, trendsRes, sectorsRes, regionsRes] = await Promise.all([
        api.get(`/analytics/summary`),
        api.get(`/analytics/trends/fraud`, { params: { days: selectedTimeRange } }),
        api.get(`/analytics/analysis/sectors`),
        api.get(`/analytics/analysis/regions`)
      ]);

      setSummary(summaryRes.data.data);
      setFraudTrends(trendsRes.data.data.tip_trends || []);
      setSectorData(sectorsRes.data.data.sectors || []);
      setRegionalData(regionsRes.data.data.regions || []);
    } catch (err) {
      console.error('Analytics fetch error:', err);
      
      // Fallback to mock data when backend is unavailable
      const mockSummary: PlatformSummary = {
        overview: {
          total_tips_analyzed: 1247,
          total_documents_verified: 856,
          total_fraud_chains_detected: 23,
          total_human_reviews: 145,
          platform_uptime_days: 30
        },
        risk_analysis: {
          risk_distribution: { "High": 89, "Medium": 234, "Low": 924 },
          high_risk_percentage: 7.1,
          avg_ai_confidence: 84.2,
          low_confidence_cases: 67
        },
        document_verification: {
          authentic_documents: 634,
          fake_documents: 222,
          avg_authenticity_score: 78.5,
          total_processed: 856
        },
        recent_activity: {
          tips_last_7_days: 89,
          documents_last_7_days: 67,
          reviews_last_7_days: 23
        },
        review_system: {
          pending_reviews: 12,
          completed_reviews: 133,
          review_completion_rate: 91.7
        }
      };

      const mockTrends: FraudTrend[] = [
        { date: '2024-12-15', high_risk: 8, medium_risk: 15, low_risk: 42, total: 65 },
        { date: '2024-12-16', high_risk: 12, medium_risk: 18, low_risk: 38, total: 68 },
        { date: '2024-12-17', high_risk: 6, medium_risk: 22, low_risk: 45, total: 73 },
        { date: '2024-12-18', high_risk: 9, medium_risk: 16, low_risk: 41, total: 66 },
        { date: '2024-12-19', high_risk: 11, medium_risk: 19, low_risk: 39, total: 69 }
      ];

      const mockSectors: SectorData[] = [
        { sector: 'Banking', total_cases: 234, high_risk_cases: 23, high_risk_percentage: 9.8, risk_level: 'medium' },
        { sector: 'Insurance', total_cases: 189, high_risk_cases: 31, high_risk_percentage: 16.4, risk_level: 'high' },
        { sector: 'Mutual Funds', total_cases: 156, high_risk_cases: 12, high_risk_percentage: 7.7, risk_level: 'low' },
        { sector: 'Stock Trading', total_cases: 298, high_risk_cases: 45, high_risk_percentage: 15.1, risk_level: 'medium' }
      ];

      const mockRegions: RegionalData[] = [
        { region: 'Mumbai', total_cases: 345, high_risk_cases: 42, high_risk_percentage: 12.2, population_category: 'metro' },
        { region: 'Delhi', total_cases: 289, high_risk_cases: 38, high_risk_percentage: 13.1, population_category: 'metro' },
        { region: 'Bangalore', total_cases: 234, high_risk_cases: 28, high_risk_percentage: 12.0, population_category: 'metro' },
        { region: 'Pune', total_cases: 167, high_risk_cases: 19, high_risk_percentage: 11.4, population_category: 'tier2' }
      ];

      setSummary(mockSummary);
      setFraudTrends(mockTrends);
      setSectorData(mockSectors);
      setRegionalData(mockRegions);
      
      setError('Using demo data - Backend server not available');
    } finally {
      setLoading(false);
    }
  };

  const exportData = async (format: 'json' | 'csv' | 'pdf' | 'excel') => {
    try {
      const exportDataObj = {
        summary,
        trends: fraudTrends,
        sectors: sectorData,
        regions: regionalData
      };

      switch (format) {
        case 'pdf':
          ExportUtils.exportToPDF(exportDataObj);
          break;
        case 'excel':
          ExportUtils.exportToExcel(exportDataObj);
          break;
        case 'json':
          ExportUtils.exportToJSON(exportDataObj);
          break;
        case 'csv':
          // Fallback CSV export
          const csvData = [
            ['Metric', 'Value'],
            ['Total Tips', summary?.overview?.total_tips_analyzed || 0],
            ['Documents Verified', summary?.overview?.total_documents_verified || 0],
            ['High Risk %', summary?.risk_analysis?.high_risk_percentage || 0]
          ];
          const csvContent = csvData.map(row => row.join(',')).join('\n');
          const blob = new Blob([csvContent], { type: 'text/csv' });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = 'analytics-summary.csv';
          a.click();
          URL.revokeObjectURL(url);
          break;
      }
    } catch (err) {
      console.error('Export error:', err);
      // Fallback for missing dependencies
      if (format === 'json') {
        const exportDataObj = { summary, trends: fraudTrends, sectors: sectorData, regions: regionalData };
        const blob = new Blob([JSON.stringify(exportDataObj, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'analytics-data.json';
        a.click();
        URL.revokeObjectURL(url);
      } else {
        alert(`${format.toUpperCase()} export temporarily unavailable. Try JSON export.`);
      }
    }
  };

  const openDrillDown = (title: string, data: any, type: 'sector' | 'region' | 'trend' | 'document') => {
    setDrillDownModal({
      isOpen: true,
      title,
      data,
      type
    });
  };

  const closeDrillDown = () => {
    setDrillDownModal({
      isOpen: false,
      title: '',
      data: null,
      type: 'sector'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-red-500 text-xl">{error}</div>
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-500 text-xl">No data available</div>
      </div>
    );
  }

  const riskDistributionData = Object.entries(summary.risk_analysis.risk_distribution).map(([level, count]) => ({
    name: level,
    value: count
  }));

  const documentData = [
    { name: 'Authentic', value: summary.document_verification.authentic_documents },
    { name: 'Fake', value: summary.document_verification.fake_documents }
  ];

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
            <p className="text-gray-600 mt-2">Comprehensive fraud detection insights and trends</p>
          </div>
          <div className="flex gap-4">
            <select
              value={selectedTimeRange}
              onChange={(e) => setSelectedTimeRange(Number(e.target.value))}
              className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
            >
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
            </select>
            <div className="flex space-x-2">
              <button
                onClick={() => exportData('pdf')}
                className="px-3 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 text-sm"
              >
                PDF
              </button>
              <button
                onClick={() => exportData('excel')}
                className="px-3 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 text-sm"
              >
                Excel
              </button>
              <button
                onClick={() => exportData('json')}
                className="px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
              >
                JSON
              </button>
              <button
                onClick={() => exportData('csv')}
                className="px-3 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 text-sm"
              >
                CSV
              </button>
            </div>
          </div>
        </div>

        {/* Real-Time Metrics */}
        <RealTimeMetrics summary={summary} />

        {/* Comparative Analysis */}
        <ComparativeAnalysis summary={summary} trends={fraudTrends} />

        {/* Key Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-sm font-medium text-gray-500">Total Tips Analyzed</h3>
            <p className="text-3xl font-bold text-blue-600">{summary.overview.total_tips_analyzed.toLocaleString()}</p>
            <p className="text-sm text-gray-600 mt-2">
              {summary.recent_activity.tips_last_7_days} in last 7 days
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-sm font-medium text-gray-500">Documents Verified</h3>
            <p className="text-3xl font-bold text-green-600">{summary.overview.total_documents_verified.toLocaleString()}</p>
            <p className="text-sm text-gray-600 mt-2">
              {summary.document_verification.avg_authenticity_score.toFixed(1)}% avg authenticity
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-sm font-medium text-gray-500">High Risk Cases</h3>
            <p className="text-3xl font-bold text-red-600">{summary.risk_analysis.high_risk_percentage.toFixed(1)}%</p>
            <p className="text-sm text-gray-600 mt-2">
              AI Confidence: {summary.risk_analysis.avg_ai_confidence.toFixed(1)}%
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-sm font-medium text-gray-500">Fraud Chains</h3>
            <p className="text-3xl font-bold text-purple-600">{summary.overview.total_fraud_chains_detected}</p>
            <p className="text-sm text-gray-600 mt-2">
              {summary.review_system.pending_reviews} pending reviews
            </p>
          </div>
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Fraud Trends */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-4">Fraud Trends Over Time</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={fraudTrends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="high_risk" stroke="#ef4444" strokeWidth={2} />
                <Line type="monotone" dataKey="medium_risk" stroke="#f59e0b" strokeWidth={2} />
                <Line type="monotone" dataKey="low_risk" stroke="#10b981" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Risk Distribution */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-4">Risk Level Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={riskDistributionData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {riskDistributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Sector Analysis */}
        <div className="bg-white p-6 rounded-lg shadow-md mb-8">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold">Top Risk Sectors</h3>
            <button
              onClick={() => openDrillDown('Sector Analysis', sectorData[0], 'sector')}
              className="px-3 py-1 bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 text-sm"
            >
              Drill Down
            </button>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={sectorData.slice(0, 10)}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="sector" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="total_cases" fill="#3b82f6" />
              <Bar dataKey="high_risk_cases" fill="#ef4444" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Regional Analysis */}
        <div className="bg-white p-6 rounded-lg shadow-md mb-8">
          <h3 className="text-lg font-semibold mb-4">Regional Risk Analysis</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {regionalData.slice(0, 9).map((region) => (
              <div key={region.region} className="p-4 border border-gray-200 rounded-lg">
                <h4 className="font-medium text-gray-900">{region.region}</h4>
                <p className="text-sm text-gray-600">{region.population_category}</p>
                <div className="mt-2">
                  <div className="flex justify-between text-sm">
                    <span>Total Cases:</span>
                    <span className="font-medium">{region.total_cases}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>High Risk:</span>
                    <span className={`font-medium ${
                      region.high_risk_percentage > 20 ? 'text-red-600' : 
                      region.high_risk_percentage > 10 ? 'text-yellow-600' : 'text-green-600'
                    }`}>
                      {region.high_risk_percentage.toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Document Authenticity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-4">Document Authenticity</h3>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={documentData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  <Cell fill="#10b981" />
                  <Cell fill="#ef4444" />
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-4">System Performance</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Platform Uptime</span>
                <span className="font-medium text-green-600">99.5%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Avg Response Time</span>
                <span className="font-medium">850ms</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Review Completion Rate</span>
                <span className="font-medium text-blue-600">
                  {summary.review_system.review_completion_rate.toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Error Rate</span>
                <span className="font-medium text-green-600">0.2%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Drill Down Modal */}
        <DrillDownAnalysis
          isOpen={drillDownModal.isOpen}
          onClose={closeDrillDown}
          title={drillDownModal.title}
          data={drillDownModal.data}
          type={drillDownModal.type}
        />
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
