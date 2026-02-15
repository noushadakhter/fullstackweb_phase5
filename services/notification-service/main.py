from fastapi import FastAPI, Request
import json
from events.schemas import ReminderEvent

app = FastAPI(
    title="Notification Service",
    description="Handles sending notifications based on events."
)

# Dapr PubSub component name (from dapr/components/pubsub-kafka.yaml)
PUBSUB_NAME = "pubsub-broker"

@app.get("/")
async def read_root():
    return {"message": "Notification Service is running"}

# Dapr subscription endpoint
@app.get("/dapr/subscribe", include_in_schema=False)
async def subscribe():
    return [
        {
            "pubsubname": PUBSUB_NAME,
            "topic": "reminders",
            "route": "/reminders",
            "deadLetterTopic": "reminders-deadletter" # Optional: for failed messages
        }
    ]

# Endpoint to handle messages from the "reminders" topic
@app.post("/reminders")
async def reminder_subscriber(request: Request):
    try:
        data = await request.json()
        print(f"Received reminder event: {data}")
        reminder_event = ReminderEvent(**data["data"]) # Dapr wraps payload in "data"
        
        # TODO: Implement actual notification sending logic here
        print(f"Sending notification for task '{reminder_event.title}' to user '{reminder_event.user_id}' due at {reminder_event.due_at}")
        
        return {"status": "SUCCESS"}
    except Exception as e:
        print(f"Error processing reminder event: {e}")
        # Dapr will retry if a non-200 status code is returned
        raise HTTPException(status_code=500, detail=str(e))
