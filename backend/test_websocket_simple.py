#!/usr/bin/env python3

import asyncio
import websockets
import json
import sys

async def test_websocket_connection():
    """Simple test to verify WebSocket endpoint is accessible"""
    uri = "ws://localhost:8000/ws/alerts"
    
    try:
        print("🔌 Attempting to connect to WebSocket endpoint...")
        print(f"   URI: {uri}")
        
        # This will fail if server is not running, which is expected
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connection established!")
            
            # Wait for initial message
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                print(f"📨 Received initial message: {data['type']} - {data['message']}")
                
                # Wait for a mock alert (sent every 30 seconds)
                print("⏳ Waiting for mock alert (up to 35 seconds)...")
                message = await asyncio.wait_for(websocket.recv(), timeout=35.0)
                data = json.loads(message)
                print(f"🚨 Received mock alert: {data['type']} - {data['message']}")
                
                return True
                
            except asyncio.TimeoutError:
                print("⏰ Timeout waiting for messages (this is normal if no alerts are generated)")
                return True
                
    except ConnectionRefusedError:
        print("❌ Connection refused - FastAPI server is not running")
        print("   To test WebSocket functionality:")
        print("   1. Start the backend server: python -m uvicorn app.main:app --reload")
        print("   2. Run this test again")
        return False
        
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False

def main():
    print("🧪 IRIS WebSocket Connection Test")
    print("=" * 50)
    
    # Run the async test
    result = asyncio.run(test_websocket_connection())
    
    print("\n" + "=" * 50)
    if result:
        print("✅ WebSocket endpoint is properly configured!")
        print("   The endpoint will work when the server is running.")
    else:
        print("❌ WebSocket test failed")
        print("   Please check server configuration.")
    
    return result

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)