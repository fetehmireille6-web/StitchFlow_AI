# StitchFlow Backend

## 📂 Project Structure
StitchFlow/
│
├── backend/                  → Main backend application
│   ├── main.py               → Entry point (FastAPI app starts here)
│   ├── __init__.py           → Marks folder as a Python package
│   │
│   ├── api/                  → API routes/endpoints
│   │   ├── routes.py         → Defines REST endpoints (e.g., /process)
│   │   └── __init__.py
│   │
│   ├── core/                 → Core backend logic (configs, helpers)
│   │   └── __init__.py
│   │
│   ├── services/             → Business logic and services
│       ├── __init__.py
│       └── ai/               → AI-related modules
│           ├── agent.py              → Main StitchFlowAgent class
│           ├── tools.py              → Utility functions
│           ├── measurement_extractor.py → Extracts measurements
│           ├── fabric_logic.py       → Fabric calculation logic
│           ├── image_handler.py      → Image processing
│           ├── chat_services.py      → Chat-related logic
│           ├── voice.py              → Voice input/output
│           └── __init__.py
│
├── frontend/                 → Frontend assets
│   ├── static/               → CSS, JS, images
│   └── templates/            → HTML templates (Jinja2)
│
└── requirements.txt          → Python dependencies
## 🚀 Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd StitchFlow

## 🚀 Install Dependencies
From the project root (`StitchFlow/`):
pip install -r requirements.txt

## 🚀 Running the sever
From the project root (`StitchFlow/`):

uvicorn backend.main:app --reload
- The backend will start at: http://127.0.0.1:8000
- Static files are served at: http://127.0.0.1:8000/static/ (127.0.0.1 in Bing)
- Templates are rendered via FastAPI routes.

🌐 API Endpoints
- GET / → Loads the homepage (index.html) with a connection message.
- POST /process → Accepts user commands, parses them with StitchFlowAgent, and returns structured data.


🧩 Key Components
- backend/main.py → Starts FastAPI, mounts static files, loads templates, and includes API routes.
- backend/api/routes.py → Defines API endpoints (like /process).
- backend/services/ai/agent.py → Contains the StitchFlowAgent class, which parses commands and extracts measurements.
- backend/services/ai/tools.py → Helper functions (e.g., fabric calculations).
- frontend/static/ → Holds CSS, JavaScript, and images for styling and interactivity.
- frontend/templates/ → HTML templates rendered by FastAPI (via Jinja2).
- requirements.txt → List of dependencies (FastAPI, Uvicorn, Jinja2, etc.) 
