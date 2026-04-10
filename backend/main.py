import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from api.routes import router
from services.ai.agent import StitchFlowAgent
from services.database import Base, engine

# Resolve project paths relative to this file
# BASE_DIR is .../backend/
BASE_DIR = Path(__file__).resolve().parent
# PROJECT_ROOT is .../StitchFlow/
PROJECT_ROOT = BASE_DIR.parent

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Ensure the uploads directory exists at the project root
(PROJECT_ROOT / "uploads").mkdir(exist_ok=True)

# Serve static files using absolute paths
app.mount("/static", StaticFiles(directory=str(PROJECT_ROOT / "frontend" / "static")), name="static")
app.mount("/uploads", StaticFiles(directory=str(PROJECT_ROOT / "uploads")), name="uploads")

# Templates
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "frontend" / "templates"))

agent = StitchFlowAgent()

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )
@app.get("/orders-page")
async def orders_page(request: Request):
    return templates.TemplateResponse(
        "orders.html",
        {"request": request}
    )

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)