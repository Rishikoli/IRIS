from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import json
import asyncio
from datetime import datetime
import random

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove disconnected clients
                self.active_connections.remove(connection)

manager = ConnectionManager()

@router.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial connection message
        await manager.send_personal_message(
            json.dumps({
                "type": "connection",
                "message": "Connected to IRIS real-time alerts",
                "timestamp": datetime.now().isoformat()
            }),
            websocket
        )
        
        # Keep connection alive and send periodic mock alerts
        while True:
            await asyncio.sleep(30)  # Send mock alert every 30 seconds
            
            # Generate mock high-risk alert
            mock_alert = generate_mock_alert()
            await manager.send_personal_message(
                json.dumps(mock_alert),
                websocket
            )
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

def generate_mock_alert():
    """Generate mock real-time notifications for demo purposes"""
    alert_types = [
        {
            "type": "high_risk_tip",
            "title": "High-Risk Investment Tip Detected",
            "message": "New tip with 95% fraud probability detected in Technology sector",
            "priority": "high",
            "sector": "Technology",
            "risk_score": random.randint(85, 100)
        },
        {
            "type": "fraud_chain_update",
            "title": "Fraud Chain Extended",
            "message": "New connection added to existing fraud chain #FC-2024-001",
            "priority": "medium",
            "chain_id": "FC-2024-001",
            "new_nodes": random.randint(1, 3)
        },
        {
            "type": "document_anomaly",
            "title": "Suspicious Document Uploaded",
            "message": "PDF document with multiple authenticity issues detected",
            "priority": "high",
            "anomaly_count": random.randint(3, 7)
        },
        {
            "type": "advisor_verification",
            "title": "Unregistered Advisor Activity",
            "message": "Multiple tips referencing unregistered advisor 'Quick Profit Guru'",
            "priority": "medium",
            "advisor_name": "Quick Profit Guru",
            "tip_count": random.randint(5, 15)
        },
        {
            "type": "regional_spike",
            "title": "Regional Fraud Activity Spike",
            "message": "40% increase in fraud reports from Mumbai region",
            "priority": "medium",
            "region": "Mumbai",
            "increase_percentage": random.randint(25, 60)
        }
    ]
    
    selected_alert = random.choice(alert_types)
    selected_alert.update({
        "id": f"alert_{random.randint(1000, 9999)}",
        "timestamp": datetime.now().isoformat(),
        "read": False
    })
    
    return selected_alert

# Function to broadcast alerts from other parts of the application
async def broadcast_alert(alert_data: dict):
    """Function to broadcast alerts from other services"""
    await manager.broadcast(json.dumps(alert_data))

# Helper functions to create specific alert types
def create_high_risk_tip_alert(tip_id: str, risk_score: int, sector: str = None) -> dict:
    """Create alert for high-risk tip detection"""
    return {
        "id": f"tip_alert_{tip_id}",
        "type": "high_risk_tip",
        "title": "High-Risk Investment Tip Detected",
        "message": f"New tip with {risk_score}% fraud probability detected" + (f" in {sector} sector" if sector else ""),
        "priority": "high" if risk_score >= 80 else "medium",
        "sector": sector,
        "risk_score": risk_score,
        "tip_id": tip_id,
        "timestamp": datetime.now().isoformat(),
        "read": False
    }

def create_document_anomaly_alert(pdf_id: str, anomaly_count: int, filename: str = None) -> dict:
    """Create alert for suspicious document detection"""
    return {
        "id": f"pdf_alert_{pdf_id}",
        "type": "document_anomaly",
        "title": "Suspicious Document Uploaded",
        "message": f"PDF document with {anomaly_count} authenticity issues detected" + (f": {filename}" if filename else ""),
        "priority": "high" if anomaly_count >= 5 else "medium",
        "anomaly_count": anomaly_count,
        "pdf_id": pdf_id,
        "filename": filename,
        "timestamp": datetime.now().isoformat(),
        "read": False
    }

def create_fraud_chain_alert(chain_id: str, new_nodes: int) -> dict:
    """Create alert for fraud chain updates"""
    return {
        "id": f"chain_alert_{chain_id}_{datetime.now().timestamp()}",
        "type": "fraud_chain_update",
        "title": "Fraud Chain Extended",
        "message": f"New connection added to existing fraud chain #{chain_id}",
        "priority": "medium",
        "chain_id": chain_id,
        "new_nodes": new_nodes,
        "timestamp": datetime.now().isoformat(),
        "read": False
    }

def create_regional_spike_alert(region: str, increase_percentage: int) -> dict:
    """Create alert for regional fraud activity spikes"""
    return {
        "id": f"region_alert_{region}_{datetime.now().timestamp()}",
        "type": "regional_spike",
        "title": "Regional Fraud Activity Spike",
        "message": f"{increase_percentage}% increase in fraud reports from {region} region",
        "priority": "high" if increase_percentage >= 50 else "medium",
        "region": region,
        "increase_percentage": increase_percentage,
        "timestamp": datetime.now().isoformat(),
        "read": False
    }