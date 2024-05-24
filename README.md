# Approval Service with Webhook Integration

This project implements an approval service where users can create items on behalf of other users, who then need to approve these items. The approval process can be performed via a link sent to the approver. This service uses FastAPI for the backend, MongoDB for data storage, and includes a sample webhook listener to handle and log webhook events.

## Features

- Create approval links with descriptions and optional checkbox points.
- Approve items via a link sent to the approver.
- Register webhooks to be notified upon approval.
- Log webhook notifications and handle errors gracefully.

## Project Structure

.
├── Dockerfile
├── Dockerfile.webhook_listener
├── README.md
├── docker-compose.yaml
├── requirements.txt
├── main.py
├── webhook_listener.py
└── templates/
│ └── approve.html


## Setup

### Prerequisites

- Docker
- Docker Compose

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-repo/approval-service.git
cd approval-service
```

Create a .env file and set your environment variables:

```bash
SECRET_KEY=your_secret_key
WEBHOOK_TOKEN=your_webhook_token
MONGODB_URI=mongodb://mongo:27017
```

Build and start the services using Docker Compose:

```bash
docker-compose up --build
```

## Usage
### Creating Approval Links

Send a POST request to /create-link with the following JSON body:

```json
{
  "metadata": {  "tenant_id": "tenant1" },
  "description": "Please approve this request",
  "bullet_points": [
    { "description": "Accept this condition", "checked": false },
    { "description": "Accept this as well", "checked": true }
  ]
}
```
The response will include an approval_link that can be sent to the approver.

### Approving Items
1. The approver visits the approval_link.
2. They see the description and bullet points and must check all boxes.
3. After clicking the "Submit" button, the approval is processed.

### Registering Webhooks
Send a POST request to /register-webhook/ with the following JSON body and an authorization token in the headers:

```json
{
  "url": "http://your-webhook-url.com/webhook"
}
```

Headers:

```
Authorization: your_webhook_token
```

### Webhook Listener
The webhook_listener.py script registers itself with the approval service and listens for webhook events, printing them to the console.

## Running Tests
You can use tools like Postman or curl to send requests to the API endpoints and verify their functionality.

## Example Requests
### Registering a Webhook
```bash
curl -X POST http://localhost:8000/register-webhook -H "Authorization: your_webhook_token" -H "Content-Type: application/json" -d '{"url": "http://localhost:8001/webhook"}'
```

### Creating an Approval Link
```bash
curl -X POST http://localhost:8000/create-link -H "Content-Type: application/json" -d '{
  "metadata": { "tenant_id": "tenant1" },
  "description": "Please approve this request",
  "bullet_points": [
    { "description": "Accept this condition", "checked": false },
    { "description": "Accept this as well", "checked": true }
  ]
}'
```
### Approving an Item
Visit the approval link returned from the /create-link request, check all bullet points, and click submit.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.
