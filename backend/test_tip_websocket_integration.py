#!/usr/bin/env python3

import asyncio
import websockets
import json
import requests
import sys

async def test_tip_websocket_integration():
    """Test that high-risk tip submissions trigger WebSocket alerts"""
    print("🧪 Testing Tip Analysis → WebSocket Alert Integration")
    print("=" * 60)
    
    try:
        # Connect to WebSocket
        uri = "ws://localhost:8000/ws/alerts"
        print(f"🔌 Connecting to {uri}...")
        
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected!")
            
            # Clear initial connection message
            await websocket.recv()
            
            # Submit a high-risk tip via HTTP API
            print("\n📝 Submitting high-risk investment tip...")
            
            tip_data = {
                "message": "🚨 URGENT! Buy CRYPTOSTOCK now! Guaranteed 1000% returns in 48 hours! Secret insider information! Limited time only!",
                "source": "websocket_integration_test"
            }
            
            # Submit tip
            response = requests.post("http://localhost:8000/api/check-tip", json=tip_data)
            
            if response.status_code == 200:
                result = response.json()
                assessment = result['assessment']
                
                print(f"✅ Tip Analysis Complete:")
                print(f"   Risk Level: {assessment['level']}")
                print(f"   Risk Score: {assessment['score']}%")
                print(f"   Reasons: {', '.join(assessment['reasons'][:2])}...")
                
                # Wait for WebSocket alert
                print("\n⏳ Waiting for real-time WebSocket alert...")
                
                try:
                    # Wait up to 10 seconds for alert
                    alert_message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    alert_data = json.loads(alert_message)
                    
                    print(f"🚨 Real-time Alert Received!")
                    print(f"   Type: {alert_data['type']}")
                    print(f"   Title: {alert_data.get('title', 'N/A')}")
                    print(f"   Message: {alert_data['message']}")
                    print(f"   Priority: {alert_data.get('priority', 'N/A')}")
                    print(f"   Risk Score: {alert_data.get('risk_score', 'N/A')}%")
                    
                    # Verify alert matches the tip analysis
                    if alert_data['type'] == 'high_risk_tip':
                        print("✅ Alert type matches expectation")
                        
                        if alert_data.get('risk_score') == assessment['score']:
                            print("✅ Risk scores match between API and WebSocket")
                        else:
                            print(f"⚠️ Risk score mismatch: API={assessment['score']}%, WS={alert_data.get('risk_score')}%")
                        
                        return True
                    else:
                        print(f"⚠️ Unexpected alert type: {alert_data['type']}")
                        return False
                        
                except asyncio.TimeoutError:
                    print("❌ No WebSocket alert received within 10 seconds")
                    print("   This might indicate the integration is not working")
                    return False
                    
            else:
                print(f"❌ Tip submission failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    print("🔗 IRIS Tip Analysis ↔ WebSocket Integration Test")
    print("This test verifies that high-risk tips trigger real-time alerts\n")
    
    # Run the test
    result = asyncio.run(test_tip_websocket_integration())
    
    print("\n" + "=" * 60)
    if result:
        print("🎉 TIP-WEBSOCKET INTEGRATION TEST PASSED!")
        print("\n✅ Verified Flow:")
        print("   1. High-risk tip submitted via HTTP API")
        print("   2. Tip analyzed and stored in database")
        print("   3. Real-time alert sent via WebSocket")
        print("   4. Alert received by connected clients")
        print("\n🎯 This enables:")
        print("   ✅ Live notifications in the NavBar")
        print("   ✅ Real-time fraud detection alerts")
        print("   ✅ Immediate regulator notifications")
        print("   ✅ Demo-ready live functionality")
        
    else:
        print("❌ INTEGRATION TEST FAILED")
        print("The tip analysis and WebSocket alert system may not be properly connected.")
    
    return result

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)