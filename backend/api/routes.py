from flask import Blueprint, request, jsonify, render_template
from backend.services.agent import StitchFlowAgent
from backend.services.tools import calculate_fabric

api_bp = Blueprint('api', __name__)
agent = StitchFlowAgent()

@api_bp.route('/process',methods = ['POST'])
def process_voice():
    data = request.json
    user_input = data.get("text", "")
    result = agent.parse_command(user_input)

    return jsonify({
        "status": "success", 
        "ai_response": f"I've noted the order for {result['customer']}.",
        "data": result
    })