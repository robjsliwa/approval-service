import os
import requests
from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
REGISTRATION_URL = os.getenv("REGISTRATION_URL")
WEBHOOK_TOKEN = os.getenv("WEBHOOK_TOKEN")


# Register the webhook with the approval service
def register_webhook():
    data = {"url": WEBHOOK_URL}
    headers = {"token": WEBHOOK_TOKEN}
    response = requests.post(REGISTRATION_URL, json=data, headers=headers)
    if response.status_code == 201:
        print("Webhook registered successfully")
    else:
        print(
            f"Failed to register webhook: {response.status_code} - {response.text}"
        )


@app.on_event("startup")
async def startup_event():
    register_webhook()


# Endpoint to handle webhook calls
@app.post("/webhook")
async def handle_webhook(request: Request):
    payload = await request.json()
    print("Received webhook event:", payload)
    return {"message": "Event received"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
