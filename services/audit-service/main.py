from fastapi import FastAPI, Request
import json
from events.schemas import TaskEvent

app = FastAPI(
    title="Audit Service",
    description="Logs all task-related events for auditing purposes."
)

# Dapr PubSub component name (from dapr/components/pubsub-kafka.yaml)
PUBSUB_NAME = "pubsub-broker"

@app.get("/")
async def read_root():
    return {"message": "Audit Service is running"}

# Dapr subscription endpoint
@app.get("/dapr/subscribe", include_in_schema=False)
async def subscribe():
    return [
        {
            "pubsubname": PUBSUB_NAME,
            "topic": "task-events",
            "route": "/task-events",
            "deadLetterTopic": "task-events-deadletter"
        }
    ]

# Endpoint to handle messages from the "task-events" topic
@app.post("/task-events")
async def task_event_subscriber(request: Request):
    try:
        data = await request.json()
        print(f"Received task event: {data}")
        task_event = TaskEvent(**data["data"]) # Dapr wraps payload in "data"
        
        # TODO: Implement actual audit logging logic here
        print(f"Auditing event '{task_event.event_type}' for task '{task_event.task_id}' by user '{task_event.user_id}' at {task_event.timestamp}")
        
        return {"status": "SUCCESS"}
    except Exception as e:
        print(f"Error processing task event: {e}")
        raise HTTPException(status_code=500, detail=str(e))
