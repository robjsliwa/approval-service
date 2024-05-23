from fastapi import FastAPI, HTTPException, Request, Depends, Header
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
from motor.motor_asyncio import AsyncIOMotorClient
import os
import uuid
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Serve static files
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 templates
templates = Jinja2Templates(directory="templates")

# MongoDB setup
client = AsyncIOMotorClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017'))
db = client['approval_service']

# JWT secret key
SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')

# Webhook token for authentication
WEBHOOK_TOKEN = os.getenv('WEBHOOK_TOKEN', 'your_webhook_token')

class CreateLinkRequest(BaseModel):
    tenant_id: str
    metadata: dict
    description: str
    bullet_points: list = []

class WebhookRegistration(BaseModel):
    url: str

def verify_webhook_token(token: str = Header(...)):
    if token != WEBHOOK_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

# API to create approval link
@app.post("/create-link")
async def create_link(request: CreateLinkRequest):
    token_data = {
        "tenant_id": request.tenant_id,
        "metadata": request.metadata,
        "description": request.description,
        "bullet_points": request.bullet_points,
        "exp": datetime.utcnow() + timedelta(hours=1),  # Token expires in 1 hour
        "jti": str(uuid.uuid4())  # Unique token ID
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm="HS256")
    await db.tokens.insert_one(token_data)
    return {"approval_link": f"http://localhost:8000/approve/{token}"}

# API to verify approval link
@app.get("/verify/{token}")
async def verify_link(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return {"status": "valid", "data": payload}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid token")

# API to accept approval
@app.post("/accept/{token}")
async def accept_approval(token: str, request: Request):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        token_data = await db.tokens.find_one({"jti": payload["jti"]})
        if not token_data:
            raise HTTPException(status_code=404, detail="Token not found or already used")

        submission_data = {
            "tenant_id": payload["tenant_id"],
            "metadata": payload["metadata"],
            "description": payload["description"],
            "bullet_points": payload["bullet_points"],
            "timestamp": datetime.utcnow()
        }
        await db.submissions.insert_one(submission_data)

        # Notify webhooks
        webhooks = db.webhooks.find({})
        for webhook in await webhooks.to_list(length=100):
            # Add code to notify webhook (e.g., using HTTP requests)
            pass

        # Remove the token as it has been used
        await db.tokens.delete_one({"jti": payload["jti"]})

        return {"status": "success", "data": submission_data}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid token")

# Serve the approval page
@app.get("/approve/{token}", response_class=HTMLResponse)
async def approval_page(request: Request, token: str):
    return templates.TemplateResponse("approve.html", {"request": request, "token": token})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)