import React, { useState, useEffect } from 'react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Calendar, TrendingUp, TrendingDown, ArrowUpRight, ArrowDownRight } from 'lucide-react';

interface ComparisonData {
  period: string;
  current: number;
  previous: number;
  change: number;
  changePercent: number;
}

interface ComparativeAnalysisProps {
  summary: any;
  trends: any[];
}

const ComparativeAnalysis: React.FC<ComparativeAnalysisProps> = ({ summary, trends }) => {
  const [comparisonType, setComparisonType] = useState<'month' | 'quarter' | 'year'>('month');
  const [comparisonData, setComparisonData] = useState<ComparisonData[]>([]);

  useEffect(() => {
    generateComparisonData();
  }, [comparisonType, summary, trends]);

  const generateComparisonData = () => {
    // Mock comparative data based on current summary
    const baseValue = summary?.overview?.total_tips_analyzed || 1000;
    
    let data: ComparisonData[] = [];
    
    if (comparisonType === 'month') {
      // Month-over-month comparison
      data = [
        {
          period: 'Tips Analyzed',
          current: baseValue,
          previous: Math.floor(baseValue * 0.85),
          change: Math.floor(baseValue * 0.15),
          changePercent: 17.6
        },
        {
          period: 'Documents Verified',
          current: summary?.overview?.total_documents_verified || 800,
          previous: Math.floor((summary?.overview?.total_documents_verified || 800) * 0.92),
          change: Math.floor((summary?.overview?.total_documents_verified || 800) * 0.08),
          changePercent: 8.7
        },
        {
          period: 'High Risk Cases',
          current: Math.floor(baseValue * (summary?.risk_analysis?.high_risk_percentage || 7) / 100),
          previous: Math.floor(baseValue * 0.85 * 0.09),
          change: -Math.floor(baseValue * 0.02),
          changePercent: -12.3
        },
        {
          period: 'Fraud Chains',
          current: summary?.overview?.total_fraud_chains_detected || 20,
          previous: Math.floor((summary?.overview?.total_fraud_chains_detected || 20) * 0.75),
          change: Math.floor((summary?.overview?.total_fraud_chains_detected || 20) * 0.25),
          changePercent: 33.3
        }
      ];
    } else if (comparisonType === 'quarter') {
      // Quarter-over-quarter comparison
      data = [
        {
          period: 'Tips Analyzed',
          current: baseValue,
          previous: Math.floor(baseValue * 0.78),
          change: Math.floor(baseValue * 0.22),
          changePercent: 28.2
        },
        {
          period: 'Documents Verified',
          current: summary?.overview?.total_documents_verified || 800,
          previous: Math.floor((summary?.overview?.total_documents_verified || 800) * 0.83),
          change: Math.floor((summary?.overview?.total_documents_verified || 800) * 0.17),
          changePercent: 20.5
        },
        {
          period: 'High Risk Cases',
          current: Math.floor(baseValue * (summary?.risk_analysis?.high_risk_percentage || 7) / 100),
          previous: Math.floor(baseValue * 0.78 * 0.11),
          change: -Math.floor(baseValue * 0.04),
          changePercent: -18.9
        },
        {
          period: 'Fraud Chains',
          current: summary?.overview?.total_fraud_chains_detected || 20,
          previous: Math.floor((summary?.overview?.total_fraud_chains_detected || 20) * 0.65),
          change: Math.floor((summary?.overview?.total_fraud_chains_detected || 20) * 0.35),
          changePercent: 53.8
        }
      ];
    } else {
      // Year-over-year comparison
      data = [
        {
          period: 'Tips Analyzed',
          current: baseValue,
          previous: Math.floor(baseValue * 0.45),
          change: Math.floor(baseValue * 0.55),
          changePercent: 122.2
        },
        {
          period: 'Documents Verified',
          current: summary?.overview?.total_documents_verified || 800,
          previous: Math.floor((summary?.overview?.total_documents_verified || 800) * 0.52),
          change: Math.floor((summary?.overview?.total_documents_verified || 800) * 0.48),
          changePercent: 92.3
        },
        {
          period: 'High Risk Cases',
          current: Math.floor(baseValue * (summary?.risk_analysis?.high_risk_percentage || 7) / 100),
          previous: Math.floor(baseValue * 0.45 * 0.15),
          change: -Math.floor(baseValue * 0.03),
          changePercent: -35.7
        },
        {
          period: 'Fraud Chains',
          current: summary?.overview?.total_fraud_chains_detected || 20,
          previous: Math.floor((summary?.overview?.total_fraud_chains_detected || 20) * 0.3),
          change: Math.floor((summary?.overview?.total_fraud_chains_detected || 20) * 0.7),
          changePercent: 233.3
        }
      ];
    }

    setComparisonData(data);
  };

  const getChangeColor = (change: number) => {
    if (change > 0) return 'text-green-600';
    if (change < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  const getChangeIcon = (change: number) => {
    if (change > 0) return <ArrowUpRight className="h-4 w-4 text-green-600" />;
    if (change < 0) return <ArrowDownRight className="h-4 w-4 text-red-600" />;
    return <div className="h-4 w-4" />;
  };

  const chartData = comparisonData.map(item => ({
    name: item.period,
    current: item.current,
    previous: item.previous,
    change: item.changePercent
  }));

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Comparative Analysis</h3>
        <div className="flex items-center space-x-2">
          <Calendar className="h-4 w-4 text-gray-500" />
          <select
            value={comparisonType}
            onChange={(e) => setComparisonType(e.target.value as 'month' | 'quarter' | 'year')}
            className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500"
          >
            <option value="month">Month-over-Month</option>
            <option value="quarter">Quarter-over-Quarter</option>
            <option value="year">Year-over-Year</option>
          </select>
        </div>
      </div>

      {/* Comparison Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {comparisonData.map((item, index) => (
          <div key={index} className="p-4 border border-gray-200 rounded-lg">
            <h4 className="text-sm font-medium text-gray-600 mb-2">{item.period}</h4>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Current</span>
                <span className="text-lg font-bold text-gray-900">{item.current.toLocaleString()}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Previous</span>
                <span className="text-sm text-gray-600">{item.previous.toLocaleString()}</span>
              </div>
              <div className="flex items-center justify-between pt-2 border-t border-gray-100">
                <div className="flex items-center space-x-1">
                  {getChangeIcon(item.change)}
                  <span className={`text-sm font-medium ${getChangeColor(item.change)}`}>
                    {item.changePercent > 0 ? '+' : ''}{item.changePercent.toFixed(1)}%
                  </span>
                </div>
                <span className={`text-xs ${getChangeColor(item.change)}`}>
                  {item.change > 0 ? '+' : ''}{item.change.toLocaleString()}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Comparison Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <h4 className="text-md font-medium text-gray-900 mb-4">Current vs Previous Period</h4>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="current" fill="#3b82f6" name="Current Period" />
              <Bar dataKey="previous" fill="#94a3b8" name="Previous Period" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div>
          <h4 className="text-md font-medium text-gray-900 mb-4">Percentage Change</h4>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip formatter={(value) => [`${value}%`, 'Change']} />
              <Line 
                type="monotone" 
                dataKey="change" 
                stroke="#10b981" 
                strokeWidth={3}
                dot={{ fill: '#10b981', strokeWidth: 2, r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Insights */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h4 className="text-sm font-medium text-blue-900 mb-2">Key Insights</h4>
        <div className="space-y-1">
          {comparisonData.map((item, index) => {
            if (Math.abs(item.changePercent) > 20) {
              return (
                <p key={index} className="text-sm text-blue-800">
                  • <strong>{item.period}</strong> shows {item.changePercent > 0 ? 'significant growth' : 'notable decline'} 
                  of {Math.abs(item.changePercent).toFixed(1)}% compared to the previous {comparisonType}
                </p>
              );
            }
            return null;
          }).filter(Boolean)}
        </div>
      </div>
    </div>
  );
};

export default ComparativeAnalysis;
