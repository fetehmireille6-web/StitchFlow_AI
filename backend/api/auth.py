from fastapi import APIRouter, Form, Depends, Response, Cookie
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from services.database import get_db
from services import models

auth_router = APIRouter(tags=["Authentication"])

@auth_router.post("/api/login")
async def login(response: Response, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or user.password != password:
        return RedirectResponse(url="/login?error=invalid", status_code=303)

    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(key="user_email", value=email, path="/")
    return response

@auth_router.post("/api/signup")
async def signup(response: Response, name: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == email).first()
    if existing_user:
        return RedirectResponse(url="/signup?error=email_exists", status_code=303)

    new_user = models.User(name=name, email=email, password=password)
    db.add(new_user)
    db.commit()
    
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(key="user_email", value=email, path="/")
    return response

@auth_router.get("/logout")
async def logout(response: Response):
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("user_email", path="/")
    return response