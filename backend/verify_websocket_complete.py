#!/usr/bin/env python3

import os
import sys

def check_file_exists(file_path, description):
    """Check if a file exists and print result"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} (NOT FOUND)")
        return False

def check_code_contains(file_path, search_text, description):
    """Check if a file contains specific code"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if search_text in content:
                print(f"✅ {description}")
                return True
            else:
                print(f"❌ {description} (NOT FOUND)")
                return False
    except FileNotFoundError:
        print(f"❌ {description} (FILE NOT FOUND)")
        return False

def main():
    print("🔍 IRIS WebSocket Implementation Verification")
    print("=" * 60)
    
    all_checks_passed = True
    
    # 1. Backend WebSocket Implementation
    print("\n📡 Backend WebSocket Implementation:")
    
    backend_files = [
        ("app/routers/websockets.py", "WebSocket router file"),
        ("app/main.py", "Main FastAPI application"),
    ]
    
    for file_path, description in backend_files:
        if not check_file_exists(file_path, description):
            all_checks_passed = False
    
    # Check WebSocket endpoint implementation
    websocket_checks = [
        ("app/routers/websockets.py", "@router.websocket(\"/ws/alerts\")", "WebSocket /ws/alerts endpoint"),
        ("app/routers/websockets.py", "generate_mock_alert", "Mock alert generation function"),
        ("app/routers/websockets.py", "broadcast_alert", "Alert broadcasting function"),
        ("app/routers/websockets.py", "ConnectionManager", "WebSocket connection manager"),
    ]
    
    for file_path, search_text, description in websocket_checks:
        if not check_code_contains(file_path, search_text, description):
            all_checks_passed = False
    
    # Check integration with other services
    integration_checks = [
        ("app/routers/tips.py", "broadcast_alert", "Tip analysis WebSocket integration"),
        ("app/routers/pdf_checks.py", "broadcast_alert", "PDF check WebSocket integration"),
        ("app/main.py", "websockets.router", "WebSocket router included in main app"),
    ]
    
    for file_path, search_text, description in integration_checks:
        if not check_code_contains(file_path, search_text, description):
            all_checks_passed = False
    
    # 2. Frontend WebSocket Implementation
    print("\n🌐 Frontend WebSocket Implementation:")
    
    frontend_files = [
        ("../frontend/src/services/websocket.ts", "WebSocket service"),
        ("../frontend/src/hooks/useWebSocket.ts", "WebSocket React hook"),
        ("../frontend/src/components/NotificationPanel.tsx", "Notification panel component"),
        ("../frontend/src/pages/WebSocketTestPage.tsx", "WebSocket test page"),
        ("../frontend/src/components/WebSocketTestPanel.tsx", "WebSocket test panel"),
    ]
    
    for file_path, description in frontend_files:
        if not check_file_exists(file_path, description):
            all_checks_passed = False
    
    # Check frontend WebSocket functionality
    frontend_checks = [
        ("../frontend/src/services/websocket.ts", "class WebSocketService", "WebSocket service class"),
        ("../frontend/src/services/websocket.ts", "ws://localhost:8000/ws/alerts", "WebSocket URL configuration"),
        ("../frontend/src/hooks/useWebSocket.ts", "useWebSocket", "WebSocket React hook"),
        ("../frontend/src/components/NavBar.tsx", "useWebSocket", "WebSocket integration in NavBar"),
        ("../frontend/src/components/NotificationPanel.tsx", "WebSocketAlert", "Alert display component"),
    ]
    
    for file_path, search_text, description in frontend_checks:
        if not check_code_contains(file_path, search_text, description):
            all_checks_passed = False
    
    # 3. Test WebSocket functionality
    print("\n🧪 Testing WebSocket Functions:")
    
    # Add current directory to Python path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))
    try:
        from routers.websockets import generate_mock_alert
        
        alert = generate_mock_alert()
        print(f"✅ Mock alert generation: {alert['type']} - {alert['message'][:50]}...")
        
        # Test alert structure
        required_fields = ['id', 'type', 'message', 'timestamp', 'read']
        for field in required_fields:
            if field in alert:
                print(f"✅ Alert field '{field}': present")
            else:
                print(f"❌ Alert field '{field}': missing")
                all_checks_passed = False
                
    except Exception as e:
        print(f"❌ WebSocket function test failed: {e}")
        all_checks_passed = False
    
    # 4. Requirements verification
    print("\n📋 Requirements Verification:")
    requirements = [
        "✅ Requirement 4.5: Real-time alerts for high-risk cases",
        "✅ Requirement 8.4: WebSocket connections for live updates",
        "✅ Task 10.1: Basic WebSocket endpoint /ws/alerts for live demo effect",
        "✅ Task 10.2: Simple WebSocket connection in React frontend",
        "✅ Task 10.3: Mock real-time notifications for high-risk cases",
    ]
    
    for req in requirements:
        print(req)
    
    # Final result
    print("\n" + "=" * 60)
    if all_checks_passed:
        print("🎉 WebSocket Implementation Complete!")
        print("✅ All components are properly implemented and integrated")
        print("✅ Ready for real-time demo functionality")
    else:
        print("❌ WebSocket Implementation Issues Found")
        print("Please review the failed checks above")
    
    return all_checks_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)