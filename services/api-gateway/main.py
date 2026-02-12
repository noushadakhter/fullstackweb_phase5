import uvicorn
from fastapi import FastAPI, Body
from pydantic import BaseModel
from dapr.clients import DaprClient
import uuid
import json

app = FastAPI()

DAPR_PUBSUB_NAME = "pubsub-broker"
DAPR_TOPIC_NAME = "tasks"

class TaskCreate(BaseModel):
    title: str
    description: str | None = None

@app.post("/v1/tasks")
async def create_task(task: TaskCreate):
    with DaprClient() as d:
        event_id = str(uuid.uuid4())
        event_data = {
            "eventId": event_id,
            "eventType": "TaskCreated",
            "data": task.dict()
        }
        
        # Publish an event to the topic
        d.publish_event(
            pubsub_name=DAPR_PUBSUB_NAME,
            topic_name=DAPR_TOPIC_NAME,
            data=json.dumps(event_data),
            data_content_type='application/json',
        )
        
        print(f"Published event {event_id} of type TaskCreated to {DAPR_TOPIC_NAME}", flush=True)

    return {"message": "Task creation event published", "eventId": event_id}

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
