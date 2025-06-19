from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import json

from app.config import settings
from app.routers import auth, robots, agents, system, logs
from app.services.websocket_manager import ConnectionManager
from app.services.robot_manager import robot_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Artbot Control Hub",
    description="Database-free robot control and monitoring system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
manager = ConnectionManager()

# Connect robot_manager with websocket_manager
robot_manager.websocket_manager = manager

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(robots.router, prefix="/api/robots", tags=["robots"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(system.router, prefix="/api/system", tags=["system"])
app.include_router(logs.router, prefix="/api/logs", tags=["logs"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Artbot Control Hub API",
        "version": "1.0.0",
        "status": "running"
    }

@app.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """WebSocket endpoint for real-time dashboard updates"""
    await manager.connect(websocket, "dashboard")
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            logger.info(f"Received dashboard WebSocket message: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket, "dashboard")
        logger.info("Dashboard WebSocket client disconnected")

@app.websocket("/ws/agent/{agent_id}")
async def websocket_agent(websocket: WebSocket, agent_id: str):
    """WebSocket endpoint for agent communication"""
    await manager.connect(websocket, f"agent:{agent_id}")
    
    # Register agent when it connects
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle agent messages (heartbeat, status updates, command responses)
            await manager.handle_agent_message(agent_id, message)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, f"agent:{agent_id}")
        robot_manager.remove_agent(agent_id)
        logger.info(f"Agent {agent_id} disconnected")
    except Exception as e:
        logger.error(f"Error handling agent {agent_id} message: {e}")
        manager.disconnect(websocket, f"agent:{agent_id}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
