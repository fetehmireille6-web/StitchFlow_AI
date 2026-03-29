from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

app = FastAPI()

app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")
templates= Jinja2Templates(directory="../frontend/templates")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html",{"request": request, "message": "StitchFlow Backend is Connected!"})
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)