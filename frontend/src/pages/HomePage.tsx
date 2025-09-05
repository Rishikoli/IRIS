import { Link } from 'react-router-dom'
import { Shield, FileCheck, Users, BarChart3, TrendingUp, Network, AlertTriangle, Zap, Activity } from 'lucide-react'
import Plasma from '../components/Plasma'
import { whaleLogo } from '../assets'
import '../assets/fonts/merchant-black.css'
import PixelArtFishVideo from '../assets/videos/Pixel_Art_Fish_Animation_Video.mp4';
const HomePage = () => {
  return (
    <div className="max-w-7xl mx-auto">
      <style>{`
        
        @keyframes blob {
          0% {
            transform: translate(0px, 0px) scale(1);
          }
          33% {
            transform: translate(30px, -50px) scale(1.1);
          }
          66% {
            transform: translate(-20px, 20px) scale(0.9);
          }
          100% {
            transform: translate(0px, 0px) scale(1);
          }
        }
        
        @keyframes plasma {
          0%, 100% {
            transform: rotate(0deg) scale(1);
          }
          33% {
            transform: rotate(120deg) scale(1.1);
          }
          66% {
            transform: rotate(240deg) scale(0.9);
          }
        }
        
        @keyframes plasma-flow {
          0%, 100% {
            transform: translateX(-50%) translateY(-50%) rotate(0deg);
          }
          50% {
            transform: translateX(-50%) translateY(-50%) rotate(180deg);
          }
        }
        
        .animate-blob {
          animation: blob 7s infinite;
        }
        
        .animate-plasma {
          animation: plasma 8s ease-in-out infinite;
        }
        
        .animate-plasma-flow {
          animation: plasma-flow 12s linear infinite;
        }
        
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animation-delay-4000 {
          animation-delay: 4s;
        }
        .animation-delay-6000 {
          animation-delay: 6s;
        }
        .animation-delay-8000 {
          animation-delay: 8s;
        }
      `}</style>
      {/* Bento Box Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-8">

        {/* IRIS Platform Info - Hero Card */}
        <div className="md:col-span-4 lg:col-span-3 rounded-2xl text-white relative overflow-hidden">
          {/* Full background video */}
          <video
            className="absolute inset-0 w-full h-full object-cover rounded-2xl"
            autoPlay
            loop
            muted
            playsInline
            src={PixelArtFishVideo}
          >
            Your browser does not support the video tag.
          </video>

          {/* Dark overlay for text readability */}
          <div className="absolute inset-0 bg-black/40 rounded-2xl" />

          <div className="relative z-10 p-8">
            <div className="flex items-center mb-6">
              <img
                src={whaleLogo}
                alt="IRIS Logo"
                className="h-20 w-20 mr-6 object-contain"
              />
              <div>
                <h1 className="text-5xl merchant-black mb-2 text-white">IRIS</h1>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                  <span className="text-green-400 text-sm font-medium">System Online</span>
                </div>
              </div>
            </div>
            <p className="text-slate-200 text-lg mb-6 leading-relaxed">
              <span className="font-semibold text-white">Intelligent Risk & Investigation System</span> for detecting,
              explaining, and forecasting fraud chains affecting retail investors in India.
            </p>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-white/20 rounded-lg p-3 backdrop-blur-sm">
                <div className="text-2xl font-bold text-blue-400">AI-Powered</div>
                <div className="text-slate-300 text-sm">Detection Engine</div>
              </div>
              <div className="bg-white/20 rounded-lg p-3 backdrop-blur-sm">
                <div className="text-2xl font-bold text-purple-400">Real-time</div>
                <div className="text-slate-300 text-sm">Monitoring</div>
              </div>
            </div>
          </div>
        </div>

        {/* Main Dashboard - Large Card */}
        <Link
          to="/dashboard"
          className="md:col-span-2 lg:col-span-3 bg-gradient-to-br from-blue-600 to-blue-800 rounded-2xl p-4 text-white hover:shadow-2xl transition-all duration-300 group relative overflow-hidden"
        >
          {/* WebGL Plasma Background */}
          <div className="absolute inset-0 opacity-60">
            <Plasma
              color="#ffffff"
              speed={0.9}
              direction="forward"
              scale={1.5}
              opacity={0.7}
              mouseInteractive={true}
            />
          </div>

          {/* Gradient overlay for better text readability */}
          <div className="absolute inset-0 bg-gradient-to-br from-blue-900/40 via-transparent to-purple-900/30" />
          <div className="absolute inset-0 bg-gradient-to-br from-blue-500/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

          <div className="relative z-10">
            <BarChart3 className="h-8 w-8 mb-3 group-hover:scale-110 transition-transform duration-300" />
            <h3 className="text-xl font-bold mb-2">Unified Dashboard</h3>
            <p className="text-blue-100 mb-3 text-sm text-center">
              IRIS RegTech Platform Comprehensive fraud detection and regulatory compliance dashboard
            </p>
            <div className="flex items-center text-blue-200 font-medium text-sm">
              Launch Platform
              <svg className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </div>
        </Link>

        {/* Tip Analysis */}
        <Link
          to="/dashboard"
          className="md:col-span-2 lg:col-span-2 bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 group border border-gray-200 dark:border-gray-700"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-xl">
              <FileCheck className="h-6 w-6 text-green-600 dark:text-green-400" />
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-gray-900 dark:text-white">94%</div>
              <div className="text-sm text-gray-500 dark:text-gray-400">Accuracy</div>
            </div>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Tip Risk Analysis</h3>
          <p className="text-gray-600 dark:text-gray-300 text-sm">
            AI-powered analysis of investment tips for fraud detection
          </p>
        </Link>

        {/* Fraud Chains */}
        <Link
          to="/fraud-chains"
          className="md:col-span-2 lg:col-span-1 bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 group border border-gray-200 dark:border-gray-700"
        >
          <div className="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-xl mb-4">
            <Network className="h-6 w-6 text-purple-600 dark:text-purple-400" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Fraud Chains</h3>
          <p className="text-gray-600 dark:text-gray-300 text-sm">
            Network analysis
          </p>
        </Link>

        {/* Document Verification */}
        <Link
          to="/dashboard"
          className="md:col-span-2 lg:col-span-2 bg-gradient-to-br from-orange-500 to-red-600 rounded-2xl p-6 text-white hover:shadow-xl transition-all duration-300 group"
        >
          <div className="flex items-center justify-between mb-4">
            <Shield className="h-8 w-8" />
            <AlertTriangle className="h-6 w-6 text-orange-200" />
          </div>
          <h3 className="text-xl font-bold mb-2">Document Authentication</h3>
          <p className="text-orange-100 text-sm mb-4">
            Advanced PDF analysis with OCR and authenticity verification
          </p>
          <div className="flex items-center space-x-4 text-sm">
            <div>
              <div className="font-semibold">1,247</div>
              <div className="text-orange-200">Scanned</div>
            </div>
            <div>
              <div className="font-semibold">89</div>
              <div className="text-orange-200">Flagged</div>
            </div>
          </div>
        </Link>

        {/* Real-time Alerts */}
        <Link
          to="/websocket-test"
          className="md:col-span-1 lg:col-span-1 bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 group border border-gray-200 dark:border-gray-700"
        >
          <div className="p-3 bg-red-100 dark:bg-red-900/30 rounded-xl mb-4">
            <Zap className="h-6 w-6 text-red-600 dark:text-red-400" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Live Alerts</h3>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-sm text-gray-600 dark:text-gray-300">Active</span>
          </div>
        </Link>

        {/* Advisor Verification */}
        <Link
          to="/dashboard"
          className="md:col-span-2 lg:col-span-2 bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 group border border-gray-200 dark:border-gray-700"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-indigo-100 dark:bg-indigo-900/30 rounded-xl">
              <Users className="h-6 w-6 text-indigo-600 dark:text-indigo-400" />
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-gray-900 dark:text-white">2.1K</div>
              <div className="text-sm text-gray-500 dark:text-gray-400">Verified</div>
            </div>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Advisor Verification</h3>
          <p className="text-gray-600 dark:text-gray-300 text-sm">
            SEBI registration and compliance checking
          </p>
        </Link>

        {/* Risk Forecasting */}
        <Link
          to="/dashboard"
          className="md:col-span-2 lg:col-span-1 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl p-6 text-white hover:shadow-xl transition-all duration-300 group"
        >
          <TrendingUp className="h-8 w-8 mb-4" />
          <h3 className="text-lg font-bold mb-2">Risk Forecasting</h3>
          <p className="text-emerald-100 text-sm mb-3">
            AI predictions
          </p>
          <div className="flex items-center">
            <Activity className="h-4 w-4 mr-2" />
            <span className="text-sm">Live Model</span>
          </div>
        </Link>

      </div>
    </div>
  )
}

export default HomePage