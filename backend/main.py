from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn

from services.agent import StitchFlowAgent

app = FastAPI()
agent = StitchFlowAgent()

app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")
templates= Jinja2Templates(directory="../frontend/templates")

class UserCommand(BaseModel):
    text: str

@app.get("/")
async def read_rout(request: Request):
    return templates.TemplateResponse("index.html",{"request": request, "message": "StitchFlow Backend is Connected!"})

@app.post("/process")
async def process_command(command: UserCommand):
    try:
        user_text = command.text
        result = agent.parse_command(user_text)
        response_data = {
            "status": "success",
            "ai_response": f"I've noted the order for {result['customer']}",
            "data": result
        }
        return response_data
    except Exception as e:
        print(f"Error processing command: {e}")
        raise
HTTPException(status_code=500, detail="An error occurred while processing the command.")
if __name__ == "__main__":
    uvicorn.run("main:app", host = "127.0.0.1",port=8000, reload=True)