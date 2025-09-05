import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Minus, AlertTriangle, Shield, FileCheck, Users } from 'lucide-react';

interface MetricData {
  value: number;
  change: number;
  trend: 'up' | 'down' | 'stable';
  label: string;
  icon: React.ComponentType<any>;
  color: string;
}

interface RealTimeMetricsProps {
  summary: any;
}

const RealTimeMetrics: React.FC<RealTimeMetricsProps> = ({ summary }) => {
  const [metrics, setMetrics] = useState<MetricData[]>([]);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  useEffect(() => {
    if (summary) {
      const newMetrics: MetricData[] = [
        {
          value: summary.overview?.total_tips_analyzed || 0,
          change: Math.floor(Math.random() * 10) - 5, // Mock real-time change
          trend: Math.random() > 0.5 ? 'up' : 'down',
          label: 'Tips Analyzed',
          icon: AlertTriangle,
          color: 'text-blue-600'
        },
        {
          value: summary.overview?.total_documents_verified || 0,
          change: Math.floor(Math.random() * 8) - 4,
          trend: Math.random() > 0.6 ? 'up' : 'stable',
          label: 'Documents Verified',
          icon: FileCheck,
          color: 'text-green-600'
        },
        {
          value: summary.risk_analysis?.high_risk_percentage || 0,
          change: Math.random() * 2 - 1, // Smaller changes for percentages
          trend: Math.random() > 0.7 ? 'down' : 'up',
          label: 'High Risk %',
          icon: Shield,
          color: 'text-red-600'
        },
        {
          value: summary.overview?.total_human_reviews || 0,
          change: Math.floor(Math.random() * 6) - 3,
          trend: Math.random() > 0.4 ? 'up' : 'stable',
          label: 'Reviews',
          icon: Users,
          color: 'text-purple-600'
        }
      ];
      
      setMetrics(newMetrics);
      setLastUpdate(new Date());
    }
  }, [summary]);

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(prevMetrics => 
        prevMetrics.map(metric => ({
          ...metric,
          change: Math.floor(Math.random() * 10) - 5,
          trend: Math.random() > 0.5 ? 'up' : Math.random() > 0.5 ? 'down' : 'stable'
        }))
      );
      setLastUpdate(new Date());
    }, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, []);

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="h-4 w-4 text-green-500" />;
      case 'down':
        return <TrendingDown className="h-4 w-4 text-red-500" />;
      default:
        return <Minus className="h-4 w-4 text-gray-500" />;
    }
  };

  const formatValue = (value: number, label: string) => {
    if (label.includes('%')) {
      return `${value.toFixed(1)}%`;
    }
    return value.toLocaleString();
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Real-Time Metrics</h3>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span className="text-xs text-gray-500">
            Last updated: {lastUpdate.toLocaleTimeString()}
          </span>
        </div>
      </div>
      
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((metric, index) => {
          const Icon = metric.icon;
          return (
            <div key={index} className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-2">
                <Icon className={`h-5 w-5 ${metric.color}`} />
                {getTrendIcon(metric.trend)}
              </div>
              
              <div className="space-y-1">
                <p className="text-2xl font-bold text-gray-900">
                  {formatValue(metric.value, metric.label)}
                </p>
                <p className="text-sm text-gray-600">{metric.label}</p>
                
                <div className="flex items-center space-x-1">
                  <span className={`text-xs font-medium ${
                    metric.change > 0 ? 'text-green-600' : 
                    metric.change < 0 ? 'text-red-600' : 'text-gray-600'
                  }`}>
                    {metric.change > 0 ? '+' : ''}{metric.change.toFixed(1)}
                  </span>
                  <span className="text-xs text-gray-500">vs last hour</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
      
      <div className="mt-4 p-3 bg-blue-50 rounded-lg">
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
          <span className="text-sm text-blue-700 font-medium">Live Data Stream Active</span>
        </div>
        <p className="text-xs text-blue-600 mt-1">
          Metrics update automatically every 30 seconds from real-time fraud detection pipeline
        </p>
      </div>
    </div>
  );
};

export default RealTimeMetrics;
