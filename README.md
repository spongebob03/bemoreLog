# BemoreLog - FastAPI + Vue.js Application

This is a simple full-stack application with a FastAPI backend and Vue.js frontend.

## Backend Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the backend server:
```bash
cd backend
uvicorn main:app --reload
```

The backend will be available at http://localhost:8000

## Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Run the development server:
```bash
npm run dev
```

The frontend will be available at http://localhost:5173

## API Endpoints

- GET `/api/hello` - Returns a hello message from the API 