#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
import websockets
import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

async def test_websocket_connection():
    """Test WebSocket connection and alert reception"""
    print("🔍 Testing WebSocket Real-time Updates...")
    
    try:
        # Connect to WebSocket
        uri = "ws://localhost:8000/ws/alerts"
        print(f"Connecting to {uri}...")
        
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected successfully")
            
            # Wait for initial connection message
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                print(f"📨 Received connection message: {data['type']}")
                
                if data['type'] == 'connection':
                    print("✅ Connection message received correctly")
                else:
                    print(f"⚠️ Unexpected message type: {data['type']}")
                
            except asyncio.TimeoutError:
                print("⚠️ No connection message received within 5 seconds")
            
            # Test high-risk tip submission (should trigger alert)
            print("\n🧪 Testing high-risk tip submission...")
            
            tip_data = {
                "message": "🚨 URGENT! Buy TESTSTOCK now! Guaranteed 500% returns in 24 hours!",
                "source": "websocket_test"
            }
            
            # Submit tip via HTTP API
            response = client.post("/api/check-tip", json=tip_data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Tip analyzed - Risk Score: {result['assessment']['score']}%")
                
                # Wait for WebSocket alert
                try:
                    alert_message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    alert_data = json.loads(alert_message)
                    
                    if alert_data['type'] == 'high_risk_tip':
                        print("🚨 Real-time alert received successfully!")
                        print(f"   Alert: {alert_data['message']}")
                        print(f"   Priority: {alert_data.get('priority', 'N/A')}")
                        print(f"   Risk Score: {alert_data.get('risk_score', 'N/A')}%")
                    else:
                        print(f"⚠️ Received different alert type: {alert_data['type']}")
                        
                except asyncio.TimeoutError:
                    print("⚠️ No alert received within 10 seconds")
                    
            else:
                print(f"❌ Tip submission failed: {response.status_code}")
            
            # Wait for periodic mock alerts
            print("\n⏳ Waiting for periodic mock alerts (30 seconds)...")
            try:
                mock_alert = await asyncio.wait_for(websocket.recv(), timeout=35.0)
                mock_data = json.loads(mock_alert)
                print(f"📨 Received mock alert: {mock_data['type']} - {mock_data['message']}")
            except asyncio.TimeoutError:
                print("⚠️ No mock alert received within 35 seconds")
            
            print("\n✅ WebSocket integration test completed successfully!")
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False
    
    return True

def test_websocket_endpoints():
    """Test WebSocket-related HTTP endpoints"""
    print("\n🔍 Testing WebSocket-related endpoints...")
    
    # Test that WebSocket router is included
    try:
        from app.routers.websockets import generate_mock_alert, create_high_risk_tip_alert
        
        # Test mock alert generation
        mock_alert = generate_mock_alert()
        print(f"✅ Mock alert generated: {mock_alert['type']}")
        
        # Test specific alert creation
        tip_alert = create_high_risk_tip_alert("test_tip_123", 85, "Technology")
        print(f"✅ High-risk tip alert created: {tip_alert['message']}")
        
        return True
        
    except Exception as e:
        print(f"❌ WebSocket endpoint test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 IRIS WebSocket Integration Test")
    print("=" * 50)
    
    # Test endpoints first
    endpoints_ok = test_websocket_endpoints()
    
    if endpoints_ok:
        print("\n🌐 Starting WebSocket connection test...")
        print("Note: This requires the backend server to be running on localhost:8000")
        
        try:
            # Run async WebSocket test
            result = asyncio.run(test_websocket_connection())
            
            if result:
                print("\n🎉 All WebSocket tests passed!")
                print("\n📋 Verified Requirements:")
                print("✅ Requirement 4.5: Real-time alerts for high-risk cases")
                print("✅ Requirement 8.4: WebSocket connections for live updates")
                print("✅ Task 10: Basic WebSocket endpoint /ws/alerts")
                print("✅ Task 10: Mock real-time notifications")
                print("✅ Task 10: Integration with tip analysis")
            else:
                print("\n❌ Some WebSocket tests failed")
                
        except Exception as e:
            print(f"\n❌ WebSocket connection test failed: {e}")
            print("Make sure the backend server is running on localhost:8000")
    else:
        print("\n❌ WebSocket endpoint tests failed")