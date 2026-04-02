from fastapi import APIRouter,  Request, HTTPException
from pydantic import BaseModel
from services.ai.agent import StitchFlowAgent
from services.ai.tools import calculate_fabric

router = APIRouter()
agent = StitchFlowAgent()

class UserCommand(BaseModel):
    text: str

@router.post('/process')
async def process_command(command:UserCommand):
    try:
        user_text = command.text
        result = agent.parse_command(user_text)
        return {
            "status": "success",
            "ai_response": f"I've noted the order for {result.get('customer', 'an unknown customer')}",
            "data": result
        }
    except Exception as e:
        print(f"Error in /process route:{e}")
        raise
HTTPException(status_code=500, detail="Internal Sever Error: Could not process command.")
    