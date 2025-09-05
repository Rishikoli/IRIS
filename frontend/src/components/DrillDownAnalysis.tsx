import React, { useState } from 'react';
import { X, ChevronDown, ChevronRight, Filter, Search, Download } from 'lucide-react';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface DrillDownProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  data: any;
  type: 'sector' | 'region' | 'trend' | 'document';
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82ca9d'];

const DrillDownAnalysis: React.FC<DrillDownProps> = ({ isOpen, onClose, title, data, type }) => {
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['overview']));

  if (!isOpen) return null;

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  const generateDetailedData = () => {
    switch (type) {
      case 'sector':
        return {
          overview: {
            totalCases: data?.total_cases || 234,
            highRiskCases: data?.high_risk_cases || 23,
            riskPercentage: data?.high_risk_percentage || 9.8,
            trendDirection: 'increasing'
          },
          subSectors: [
            { name: 'Retail Banking', cases: 89, highRisk: 8, percentage: 9.0 },
            { name: 'Corporate Banking', cases: 67, highRisk: 12, percentage: 17.9 },
            { name: 'Investment Banking', cases: 45, highRisk: 2, percentage: 4.4 },
            { name: 'Private Banking', cases: 33, highRisk: 1, percentage: 3.0 }
          ],
          timeSeriesData: [
            { month: 'Jan', cases: 18, highRisk: 2 },
            { month: 'Feb', cases: 22, highRisk: 3 },
            { month: 'Mar', cases: 19, highRisk: 1 },
            { month: 'Apr', cases: 25, highRisk: 4 },
            { month: 'May', cases: 28, highRisk: 3 },
            { month: 'Jun', cases: 31, highRisk: 5 }
          ],
          riskFactors: [
            { factor: 'Unusual transaction patterns', impact: 'High', frequency: 45 },
            { factor: 'Suspicious account activity', impact: 'Medium', frequency: 32 },
            { factor: 'Document inconsistencies', impact: 'High', frequency: 28 },
            { factor: 'Geographic anomalies', impact: 'Low', frequency: 15 }
          ]
        };
      
      case 'region':
        return {
          overview: {
            totalCases: data?.total_cases || 345,
            highRiskCases: data?.high_risk_cases || 42,
            riskPercentage: data?.high_risk_percentage || 12.2,
            populationCategory: data?.population_category || 'metro'
          },
          districts: [
            { name: 'South Mumbai', cases: 89, highRisk: 12, percentage: 13.5 },
            { name: 'Central Mumbai', cases: 76, highRisk: 9, percentage: 11.8 },
            { name: 'Western Suburbs', cases: 98, highRisk: 11, percentage: 11.2 },
            { name: 'Eastern Suburbs', cases: 82, highRisk: 10, percentage: 12.2 }
          ],
          demographics: [
            { ageGroup: '18-25', cases: 45, percentage: 13.0 },
            { ageGroup: '26-35', cases: 128, percentage: 37.1 },
            { ageGroup: '36-50', cases: 112, percentage: 32.5 },
            { ageGroup: '51+', cases: 60, percentage: 17.4 }
          ],
          fraudTypes: [
            { type: 'Investment Scams', count: 18, percentage: 42.9 },
            { type: 'Identity Theft', count: 12, percentage: 28.6 },
            { type: 'Phishing', count: 8, percentage: 19.0 },
            { type: 'Other', count: 4, percentage: 9.5 }
          ]
        };
      
      default:
        return {
          overview: {
            totalCases: 100,
            highRiskCases: 15,
            riskPercentage: 15.0,
            trendDirection: 'stable'
          }
        };
    }
  };

  const detailedData = generateDetailedData();

  const exportDetailedData = () => {
    const exportData = {
      title,
      type,
      timestamp: new Date().toISOString(),
      data: detailedData
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${title.toLowerCase().replace(/\s+/g, '-')}-detailed-analysis.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">{title} - Detailed Analysis</h2>
            <p className="text-sm text-gray-600 mt-1">Comprehensive drill-down view with advanced insights</p>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={exportDetailedData}
              className="px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center space-x-1"
            >
              <Download className="h-4 w-4" />
              <span>Export</span>
            </button>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-md"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="overflow-y-auto max-h-[calc(90vh-80px)]">
          <div className="p-6 space-y-6">
            {/* Filters and Search */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Filter className="h-4 w-4 text-gray-500" />
                <select
                  value={selectedFilter}
                  onChange={(e) => setSelectedFilter(e.target.value)}
                  className="px-3 py-1 border border-gray-300 rounded-md text-sm"
                >
                  <option value="all">All Data</option>
                  <option value="high-risk">High Risk Only</option>
                  <option value="recent">Recent Activity</option>
                </select>
              </div>
              <div className="flex items-center space-x-2 flex-1 max-w-md">
                <Search className="h-4 w-4 text-gray-500" />
                <input
                  type="text"
                  placeholder="Search within data..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="flex-1 px-3 py-1 border border-gray-300 rounded-md text-sm"
                />
              </div>
            </div>

            {/* Overview Section */}
            <div className="border border-gray-200 rounded-lg">
              <button
                onClick={() => toggleSection('overview')}
                className="w-full flex items-center justify-between p-4 hover:bg-gray-50"
              >
                <h3 className="text-lg font-semibold text-gray-900">Overview</h3>
                {expandedSections.has('overview') ? 
                  <ChevronDown className="h-5 w-5" /> : 
                  <ChevronRight className="h-5 w-5" />
                }
              </button>
              
              {expandedSections.has('overview') && (
                <div className="p-4 border-t border-gray-200">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center p-3 bg-blue-50 rounded-lg">
                      <p className="text-2xl font-bold text-blue-600">{detailedData.overview.totalCases}</p>
                      <p className="text-sm text-blue-800">Total Cases</p>
                    </div>
                    <div className="text-center p-3 bg-red-50 rounded-lg">
                      <p className="text-2xl font-bold text-red-600">{detailedData.overview.highRiskCases}</p>
                      <p className="text-sm text-red-800">High Risk</p>
                    </div>
                    <div className="text-center p-3 bg-yellow-50 rounded-lg">
                      <p className="text-2xl font-bold text-yellow-600">{detailedData.overview.riskPercentage}%</p>
                      <p className="text-sm text-yellow-800">Risk Rate</p>
                    </div>
                    <div className="text-center p-3 bg-green-50 rounded-lg">
                      <p className="text-2xl font-bold text-green-600 capitalize">{detailedData.overview.trendDirection}</p>
                      <p className="text-sm text-green-800">Trend</p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Detailed Breakdown */}
            {type === 'sector' && detailedData.subSectors && (
              <div className="border border-gray-200 rounded-lg">
                <button
                  onClick={() => toggleSection('breakdown')}
                  className="w-full flex items-center justify-between p-4 hover:bg-gray-50"
                >
                  <h3 className="text-lg font-semibold text-gray-900">Sub-Sector Breakdown</h3>
                  {expandedSections.has('breakdown') ? 
                    <ChevronDown className="h-5 w-5" /> : 
                    <ChevronRight className="h-5 w-5" />
                  }
                </button>
                
                {expandedSections.has('breakdown') && (
                  <div className="p-4 border-t border-gray-200">
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={detailedData.subSectors}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="cases" fill="#3b82f6" name="Total Cases" />
                        <Bar dataKey="highRisk" fill="#ef4444" name="High Risk" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </div>
            )}

            {/* Regional Districts */}
            {type === 'region' && detailedData.districts && (
              <div className="border border-gray-200 rounded-lg">
                <button
                  onClick={() => toggleSection('districts')}
                  className="w-full flex items-center justify-between p-4 hover:bg-gray-50"
                >
                  <h3 className="text-lg font-semibold text-gray-900">District Analysis</h3>
                  {expandedSections.has('districts') ? 
                    <ChevronDown className="h-5 w-5" /> : 
                    <ChevronRight className="h-5 w-5" />
                  }
                </button>
                
                {expandedSections.has('districts') && (
                  <div className="p-4 border-t border-gray-200">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <ResponsiveContainer width="100%" height={250}>
                        <PieChart>
                          <Pie
                            data={detailedData.districts}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ name, percentage }) => `${name}: ${percentage}%`}
                            outerRadius={80}
                            fill="#8884d8"
                            dataKey="cases"
                          >
                            {detailedData.districts.map((_: any, index: number) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip />
                        </PieChart>
                      </ResponsiveContainer>
                      
                      <div className="space-y-3">
                        {detailedData.districts.map((district: any, index: number) => (
                          <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <div>
                              <p className="font-medium text-gray-900">{district.name}</p>
                              <p className="text-sm text-gray-600">{district.cases} cases</p>
                            </div>
                            <div className="text-right">
                              <p className="font-medium text-red-600">{district.highRisk} high risk</p>
                              <p className="text-sm text-gray-600">{district.percentage}%</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Time Series Analysis */}
            {detailedData.timeSeriesData && (
              <div className="border border-gray-200 rounded-lg">
                <button
                  onClick={() => toggleSection('timeseries')}
                  className="w-full flex items-center justify-between p-4 hover:bg-gray-50"
                >
                  <h3 className="text-lg font-semibold text-gray-900">Trend Analysis</h3>
                  {expandedSections.has('timeseries') ? 
                    <ChevronDown className="h-5 w-5" /> : 
                    <ChevronRight className="h-5 w-5" />
                  }
                </button>
                
                {expandedSections.has('timeseries') && (
                  <div className="p-4 border-t border-gray-200">
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={detailedData.timeSeriesData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="month" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="cases" stroke="#3b82f6" strokeWidth={2} name="Total Cases" />
                        <Line type="monotone" dataKey="highRisk" stroke="#ef4444" strokeWidth={2} name="High Risk Cases" />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </div>
            )}

            {/* Risk Factors */}
            {detailedData.riskFactors && (
              <div className="border border-gray-200 rounded-lg">
                <button
                  onClick={() => toggleSection('riskfactors')}
                  className="w-full flex items-center justify-between p-4 hover:bg-gray-50"
                >
                  <h3 className="text-lg font-semibold text-gray-900">Risk Factors</h3>
                  {expandedSections.has('riskfactors') ? 
                    <ChevronDown className="h-5 w-5" /> : 
                    <ChevronRight className="h-5 w-5" />
                  }
                </button>
                
                {expandedSections.has('riskfactors') && (
                  <div className="p-4 border-t border-gray-200">
                    <div className="space-y-3">
                      {detailedData.riskFactors.map((factor: any, index: number) => (
                        <div key={index} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                          <div className="flex-1">
                            <p className="font-medium text-gray-900">{factor.factor}</p>
                            <p className="text-sm text-gray-600">Frequency: {factor.frequency} cases</p>
                          </div>
                          <div className="text-right">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              factor.impact === 'High' ? 'bg-red-100 text-red-800' :
                              factor.impact === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-green-100 text-green-800'
                            }`}>
                              {factor.impact} Impact
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DrillDownAnalysis;
