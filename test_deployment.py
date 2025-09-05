#!/usr/bin/env python3
"""
IRIS RegTech Platform - End-to-End Deployment Test
Comprehensive testing of all demo features and workflows
"""

import requests
import json
import time
import sys
from datetime import datetime

class IRISDeploymentTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.frontend_url = "http://localhost"
        self.test_results = []
        
    def log_test(self, test_name, success, message="", response_time=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        time_info = f" ({response_time:.2f}s)" if response_time else ""
        print(f"{status} {test_name}{time_info}")
        if message:
            print(f"    {message}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        })
    
    def test_health_endpoints(self):
        """Test basic health endpoints"""
        print("\n🏥 Testing Health Endpoints")
        print("=" * 40)
        
        # Backend health
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                self.log_test("Backend Health Check", True, "Backend is healthy", response_time)
            else:
                self.log_test("Backend Health Check", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Backend Health Check", False, f"Error: {str(e)}")
        
        # Frontend health
        try:
            start_time = time.time()
            response = requests.get(f"{self.frontend_url}/health", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                self.log_test("Frontend Health Check", True, "Frontend is healthy", response_time)
            else:
                self.log_test("Frontend Health Check", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Frontend Health Check", False, f"Error: {str(e)}")
    
    def test_tip_analysis_workflow(self):
        """Test complete tip analysis workflow"""
        print("\n📝 Testing Tip Analysis Workflow")
        print("=" * 40)
        
        # Test tip submission and analysis
        test_tip = {
            "message": "🚀 URGENT! Buy RELIANCE NOW! Guaranteed 500% returns in 2 weeks! Inside information from company director. Limited time offer!",
            "source": "test",
            "submitter_id": "test_user"
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/api/check-tip",
                json=test_tip,
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if "assessment" in data and "level" in data["assessment"]:
                    risk_level = data["assessment"]["level"]
                    risk_score = data["assessment"]["score"]
                    self.log_test(
                        "Tip Analysis", 
                        True, 
                        f"Risk: {risk_level}, Score: {risk_score}", 
                        response_time
                    )
                else:
                    self.log_test("Tip Analysis", False, "Invalid response format")
            else:
                self.log_test("Tip Analysis", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Tip Analysis", False, f"Error: {str(e)}")
    
    def test_advisor_verification(self):
        """Test advisor verification workflow"""
        print("\n👨‍💼 Testing Advisor Verification")
        print("=" * 40)
        
        try:
            start_time = time.time()
            response = requests.get(
                f"{self.base_url}/api/verify-advisor",
                params={"name": "Rajesh Kumar"},
                timeout=15
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if "results" in data:
                    self.log_test(
                        "Advisor Verification", 
                        True, 
                        f"Found {len(data['results'])} matches", 
                        response_time
                    )
                else:
                    self.log_test("Advisor Verification", False, "Invalid response format")
            else:
                self.log_test("Advisor Verification", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Advisor Verification", False, f"Error: {str(e)}")
    
    def test_heatmap_data(self):
        """Test heatmap data endpoints"""
        print("\n🗺️ Testing Heatmap Data")
        print("=" * 40)
        
        # Test sector heatmap
        try:
            start_time = time.time()
            response = requests.get(
                f"{self.base_url}/api/fraud-heatmap",
                params={"dimension": "sector", "period": "7d"},
                timeout=15
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if "heatmap_data" in data:
                    self.log_test(
                        "Sector Heatmap", 
                        True, 
                        f"Retrieved {len(data['heatmap_data'])} data points", 
                        response_time
                    )
                else:
                    self.log_test("Sector Heatmap", False, "Invalid response format")
            else:
                self.log_test("Sector Heatmap", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Sector Heatmap", False, f"Error: {str(e)}")
        
        # Test region heatmap
        try:
            start_time = time.time()
            response = requests.get(
                f"{self.base_url}/api/fraud-heatmap",
                params={"dimension": "region", "period": "30d"},
                timeout=15
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if "heatmap_data" in data:
                    self.log_test(
                        "Region Heatmap", 
                        True, 
                        f"Retrieved {len(data['heatmap_data'])} data points", 
                        response_time
                    )
                else:
                    self.log_test("Region Heatmap", False, "Invalid response format")
            else:
                self.log_test("Region Heatmap", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Region Heatmap", False, f"Error: {str(e)}")
    
    def test_forecasting_endpoints(self):
        """Test AI forecasting endpoints"""
        print("\n🔮 Testing AI Forecasting")
        print("=" * 40)
        
        try:
            start_time = time.time()
            response = requests.get(
                f"{self.base_url}/api/forecast",
                params={"dimension": "sector", "period": "2024-12"},
                timeout=20
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if "forecasts" in data:
                    self.log_test(
                        "Sector Forecasting", 
                        True, 
                        f"Retrieved {len(data['forecasts'])} forecasts", 
                        response_time
                    )
                else:
                    self.log_test("Sector Forecasting", False, "Invalid response format")
            else:
                self.log_test("Sector Forecasting", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Sector Forecasting", False, f"Error: {str(e)}")
    
    def test_fraud_chains(self):
        """Test fraud chain endpoints"""
        print("\n🔗 Testing Fraud Chain Analysis")
        print("=" * 40)
        
        # Get fraud chains list
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/fraud-chains", timeout=15)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if "chains" in data and len(data["chains"]) > 0:
                    chain_id = data["chains"][0]["id"]
                    self.log_test(
                        "Fraud Chains List", 
                        True, 
                        f"Found {len(data['chains'])} chains", 
                        response_time
                    )
                    
                    # Test individual chain details
                    try:
                        start_time = time.time()
                        detail_response = requests.get(
                            f"{self.base_url}/api/fraud-chains/{chain_id}",
                            timeout=15
                        )
                        response_time = time.time() - start_time
                        
                        if detail_response.status_code == 200:
                            chain_data = detail_response.json()
                            if "nodes" in chain_data and "edges" in chain_data:
                                self.log_test(
                                    "Fraud Chain Details", 
                                    True, 
                                    f"Nodes: {len(chain_data['nodes'])}, Edges: {len(chain_data['edges'])}", 
                                    response_time
                                )
                            else:
                                self.log_test("Fraud Chain Details", False, "Invalid chain data format")
                        else:
                            self.log_test("Fraud Chain Details", False, f"Status: {detail_response.status_code}")
                    except Exception as e:
                        self.log_test("Fraud Chain Details", False, f"Error: {str(e)}")
                else:
                    self.log_test("Fraud Chains List", False, "No chains found or invalid format")
            else:
                self.log_test("Fraud Chains List", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Fraud Chains List", False, f"Error: {str(e)}")
    
    def test_review_system(self):
        """Test human review system"""
        print("\n👥 Testing Review System")
        print("=" * 40)
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/review-queue", timeout=15)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if "reviews" in data:
                    self.log_test(
                        "Review Queue", 
                        True, 
                        f"Found {len(data['reviews'])} review cases", 
                        response_time
                    )
                else:
                    self.log_test("Review Queue", False, "Invalid response format")
            else:
                self.log_test("Review Queue", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Review Queue", False, f"Error: {str(e)}")
    
    def test_multi_source_data(self):
        """Test multi-source data integration"""
        print("\n📊 Testing Multi-Source Data Integration")
        print("=" * 40)
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/multi-source/indicators", timeout=15)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if "indicators" in data:
                    self.log_test(
                        "Multi-Source Indicators", 
                        True, 
                        f"Retrieved {len(data['indicators'])} indicators", 
                        response_time
                    )
                else:
                    self.log_test("Multi-Source Indicators", False, "Invalid response format")
            else:
                self.log_test("Multi-Source Indicators", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Multi-Source Indicators", False, f"Error: {str(e)}")
    
    def test_performance_benchmarks(self):
        """Test performance benchmarks"""
        print("\n⚡ Testing Performance Benchmarks")
        print("=" * 40)
        
        # Test multiple concurrent requests
        import concurrent.futures
        import threading
        
        def make_request():
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}/health", timeout=5)
                return time.time() - start_time, response.status_code == 200
            except:
                return None, False
        
        # Test concurrent load
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(20)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        successful_requests = [r for r in results if r[1]]
        if len(successful_requests) >= 18:  # Allow 2 failures
            avg_response_time = sum(r[0] for r in successful_requests) / len(successful_requests)
            self.log_test(
                "Concurrent Load Test", 
                True, 
                f"{len(successful_requests)}/20 requests successful, avg: {avg_response_time:.3f}s"
            )
        else:
            self.log_test(
                "Concurrent Load Test", 
                False, 
                f"Only {len(successful_requests)}/20 requests successful"
            )
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 IRIS RegTech Platform - End-to-End Deployment Test")
        print("=" * 60)
        print(f"Testing against: {self.base_url}")
        print(f"Frontend URL: {self.frontend_url}")
        print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all test categories
        self.test_health_endpoints()
        self.test_tip_analysis_workflow()
        self.test_advisor_verification()
        self.test_heatmap_data()
        self.test_forecasting_endpoints()
        self.test_fraud_chains()
        self.test_review_system()
        self.test_multi_source_data()
        self.test_performance_benchmarks()
        
        # Generate test summary
        self.generate_test_summary()
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for test in self.test_results:
                if not test["success"]:
                    print(f"  • {test['test']}: {test['message']}")
        
        # Performance summary
        timed_tests = [t for t in self.test_results if t["response_time"]]
        if timed_tests:
            avg_response_time = sum(t["response_time"] for t in timed_tests) / len(timed_tests)
            print(f"\n⚡ Performance Summary:")
            print(f"  • Average Response Time: {avg_response_time:.3f}s")
            print(f"  • Fastest Response: {min(t['response_time'] for t in timed_tests):.3f}s")
            print(f"  • Slowest Response: {max(t['response_time'] for t in timed_tests):.3f}s")
        
        # Demo readiness assessment
        critical_failures = [
            t for t in self.test_results 
            if not t["success"] and any(keyword in t["test"].lower() 
                for keyword in ["health", "tip analysis", "heatmap"])
        ]
        
        print(f"\n🎯 Demo Readiness Assessment:")
        if len(critical_failures) == 0:
            print("  ✅ READY FOR DEMO - All critical systems operational")
        elif len(critical_failures) <= 2:
            print("  ⚠️  DEMO READY WITH CAUTION - Minor issues detected")
        else:
            print("  ❌ NOT READY FOR DEMO - Critical systems failing")
        
        # Save results to file
        with open("test_results.json", "w") as f:
            json.dump({
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": failed_tests,
                    "success_rate": (passed_tests/total_tests)*100,
                    "test_timestamp": datetime.now().isoformat()
                },
                "results": self.test_results
            }, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: test_results.json")
        
        return failed_tests == 0

if __name__ == "__main__":
    # Allow custom base URL
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    tester = IRISDeploymentTester(base_url)
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
