from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn

from services.ai.agent import StitchFlowAgent
from api.routes import router

app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
agent = StitchFlowAgent()

app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")
templates= Jinja2Templates(directory="../frontend/templates")

class UserCommand(BaseModel):
    text: str

@app.get("/")
async def read_rout(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "message": "StitchFlow Backend is Connected!"})
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
