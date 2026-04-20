import os
import json
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, Request, Form, Depends, Response, Cookie
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
import uvicorn

from api.routes import router
from api.auth import auth_router
from services.ai.agent import stitchflow_agent
from services.database import Base, engine, get_db
from services.migrations import run_migrations
from services import models

# BASE_DIR is .../backend/
BASE_DIR = Path(__file__).resolve().parent
# PROJECT_ROOT is .../StitchFlow/
PROJECT_ROOT = BASE_DIR.parent

# Create all database tables
Base.metadata.create_all(bind=engine)

# Run migrations for missing columns
run_migrations()

# Initialize FastAPI app
app = FastAPI()

# Ensure the uploads directory exists at the project root
(PROJECT_ROOT / "uploads").mkdir(exist_ok=True)

# Serve static files using absolute paths
app.mount("/static", StaticFiles(directory=str(PROJECT_ROOT / "frontend" / "static")), name="static")
app.mount("/uploads", StaticFiles(directory=str(PROJECT_ROOT / "uploads")), name="uploads")

# Templates
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "frontend" / "templates"))

# ============================================
# PAGE ROUTES
# ============================================

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse(
        "landing.html",
        {"request": request}
    )

@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/signup")
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.get("/profile")
async def profile_page(request: Request, user_email: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    if not user_email:
        return RedirectResponse(url="/login", status_code=303)
    
    # Fetch user from database
    user = db.query(models.User).filter(models.User.email == user_email).first()
    
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user
    })

@app.get("/profile-data")
async def profile_data(user_email: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    """API endpoint to get profile data as JSON"""
    if not user_email:
        return {"error": "Not logged in"}
    
    user = db.query(models.User).filter(models.User.email == user_email).first()
    if user:
        return {"name": user.name, "email": user.email}
    return {"error": "User not found"}

@app.get("/reminders")
async def reminders_page(request: Request, user_email: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    if not user_email:
        return RedirectResponse(url="/login", status_code=303)
    
    user = db.query(models.User).filter(models.User.email == user_email).first()
    orders = db.query(models.Order).all()
    
    # Use the agent to identify urgent orders
    alerts = stitchflow_agent.get_urgent_alerts(orders)
    
    return templates.TemplateResponse("reminders.html", {
        "request": request, 
        "user": user, 
        "alerts": alerts
    })

@app.get("/orders-page")
async def orders_page(request: Request):
    return templates.TemplateResponse(
        "orders.html",
        {"request": request}
    )

# ============================================
# INCLUDE ROUTERS
# ============================================

app.include_router(router)
app.include_router(auth_router)

# ============================================
# RUN THE APPLICATION
# ============================================

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)