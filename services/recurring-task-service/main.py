from fastapi import FastAPI, Request
import json
from events.schemas import TaskEvent

app = FastAPI(
    title="Recurring Task Service",
    description="Automatically creates next occurrences of recurring tasks."
)

# Dapr PubSub component name (from dapr/components/pubsub-kafka.yaml)
PUBSUB_NAME = "pubsub-broker"

@app.get("/")
async def read_root():
    return {"message": "Recurring Task Service is running"}

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
        
        # TODO: Implement logic to process task completion events and schedule/create next recurring task
        if task_event.event_type == "completed":
            print(f"Processing completed task event for recurring task: {task_event.task_id}")
            # Here you would typically check if it's a recurring task
            # and if so, create the next instance.
            # Example:
            # next_task = create_next_recurring_task(task_event.task_data)
            # await publish_event("task-events", TaskEvent(...event_type="created", task_id=next_task.id...))
        
        return {"status": "SUCCESS"}
    except Exception as e:
        print(f"Error processing task event: {e}")
        raise HTTPException(status_code=500, detail=str(e))
