from fastapi import FastAPI, WebSocket, Request, HTTPException
from typing import List
import json
from events.schemas import TaskUpdateEvent # Import the TaskUpdateEvent schema

app = FastAPI(
    title="WebSocket Service",
    description="Handles real-time synchronization of task updates to connected clients."
)

# In-memory store for active WebSocket connections
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
            # Send message as JSON string
            await connection.send_text(message)

manager = ConnectionManager()

# Dapr PubSub component name (from dapr/components/pubsub-kafka.yaml)
PUBSUB_NAME = "pubsub-broker"

@app.get("/")
async def read_root():
    return {"message": "WebSocket Service is running"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, or handle client messages if needed
            # For now, just a dummy receive to keep the connection open
            await websocket.receive_text()
    except Exception:
        manager.disconnect(websocket)

# Dapr subscription endpoint
@app.get("/dapr/subscribe", include_in_schema=False)
async def subscribe():
    return [
        {
            "pubsubname": PUBSUB_NAME,
            "topic": "task-updates",
            "route": "/task-updates",
            "deadLetterTopic": "task-updates-deadletter"
        }
    ]

# Endpoint to handle messages from the "task-updates" topic
@app.post("/task-updates")
async def task_update_subscriber(request: Request):
    try:
        data = await request.json()
        print(f"Received task update event: {data}")
        task_update_event = TaskUpdateEvent(**data["data"]) # Dapr wraps payload in "data"
        
        # Broadcast the raw data to all connected WebSocket clients
        await manager.broadcast(json.dumps(data["data"]))
        
        return {"status": "SUCCESS"}
    except Exception as e:
        print(f"Error processing task update event: {e}")
        raise HTTPException(status_code=500, detail=str(e))
