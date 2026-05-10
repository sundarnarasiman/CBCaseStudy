# Customer Experience and Control

This directory contains the user-facing Customer Portal where users can view their real-time usage and manage their billing controls. It consists of a FastAPI backend and a React frontend.

## Backend
The FastAPI backend (`backend/`) streams real-time data from the `usage-events` Kafka topic to populate local caches and serve usage dashboards to the frontend.

### Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Running
```bash
uvicorn main:app --host 0.0.0.0 --port 8002
```

### Testing
```bash
pytest test_main.py
```

## Frontend (React)
*(Assuming Node v20+)*
```bash
npx create-vite@latest frontend --template react
cd frontend
npm install
npm run dev
```
The frontend queries the FastAPI backend at `http://localhost:8002/api/usage/{customerId}` to render charts and burn-down views.
