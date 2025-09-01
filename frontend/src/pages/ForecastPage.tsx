const ForecastPage = () => {
  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-dark-primary mb-2">
          AI Risk Forecasting
        </h1>
        <p className="text-gray-600">
          AI-generated forecasts of potential fraud hotspots by sector and region.
        </p>
      </div>
      
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
        <p className="text-yellow-800 text-sm">
          <strong>Coming Soon:</strong> AI-powered forecasting with explainable factors will be implemented in a future task.
        </p>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-primary-900  rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-dark-primary mb-4">
              Risk Forecast Visualization
            </h2>
            <div className="h-80 bg-gray-100 rounded-lg flex items-center justify-center">
              <p className="text-gray-500">Forecast charts coming soon</p>
            </div>
          </div>
        </div>
        
        <div className="space-y-6">
          <div className="bg-primary-900  rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-dark-primary mb-4">
              Top Risk Sectors
            </h3>
            <div className="space-y-3">
              {['Technology', 'Healthcare', 'Finance'].map((sector, i) => (
                <div key={sector} className="flex items-center justify-between">
                  <span className="text-sm text-gray-700">{sector}</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-16 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-red-500 h-2 rounded-full" 
                        style={{ width: `${(3-i) * 30}%` }}
                      ></div>
                    </div>
                    <span className="text-xs text-gray-500">{90 - i*10}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="bg-primary-900  rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-dark-primary mb-4">
              Forecast Confidence
            </h3>
            <div className="text-center">
              <div className="text-3xl font-bold text-primary-600 mb-2">87%</div>
              <p className="text-sm text-gray-600">Average Model Confidence</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ForecastPage