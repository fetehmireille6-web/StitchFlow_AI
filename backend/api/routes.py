import os
import json
from typing import Optional
from fastapi import Body
from fastapi import APIRouter, HTTPException, Form, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import joinedload
from services.ai.agent import StitchFlowAgent
from services.ai.image_handler import save_image
from services.database import SessionLocal
from services import models
from datetime import datetime   # <-- import datetime

router = APIRouter()
agent = StitchFlowAgent()

class UserCommand(BaseModel):
    text: str

@router.post("/upload-style")
async def upload_style(
    customer: str = Form(...),
    due_date: str = Form(...),   # comes in as string "YYYY-MM-DD"
    text: str = Form(...),
    file: Optional[UploadFile] = File(None)
):
    db = SessionLocal()
    try:
        # Ensure customer exists
        cust = db.query(models.Customer).filter(models.Customer.name == customer).first()
        if not cust:
            cust = models.Customer(name=customer)
            db.add(cust)
            db.commit()
            db.refresh(cust)

        # Parse measurements
        result = agent.parse_command(text)

        # Convert due_date string to Python date object
        due_date_obj = datetime.strptime(due_date, "%Y-%m-%d").date()

        # Handle optional image
        image_url = None
        if file:
            image_path = save_image(file)
            image_url = f"/uploads/{os.path.basename(image_path)}"

        # Save order
        order = models.Order(
            customer_id=cust.id,
            due_date=due_date_obj,
            measurements=json.dumps(result["measurements"]),
            image_url=image_url
        )
        db.add(order)
        db.commit()
        db.refresh(order)

        return {
            "status": "success",
            "customer": cust.name,
            "due_date": str(order.due_date),   # convert back to string for JSON
            "measurements": order.measurements,
            "image_url": order.image_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving style: {e}")
    finally:
        db.close()

@router.post("/process")
async def process_command(command: UserCommand):
    try:
        result = agent.parse_command(command.text)
        return {
            "status": "success",
            "ai_response": f"I've noted the order for {result.get('customer', 'an unknown customer')}",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")
@router.get("/orders")
async def list_orders():
    db = SessionLocal()
    try:
        orders = db.query(models.Order).options(joinedload(models.Order.customer)).all()
        return [
            {
                "id": order.id,
                "customer": order.customer.name if order.customer else "Unknown Customer",
                "due_date": str(order.due_date),
                "measurements": order.measurements or "No measurements recorded",
                "image_url": order.image_url
            }
            for order in orders
        ]
    finally:
        db.close()
@router.delete("/orders/{order_id}")
async def delete_order(order_id: int):
    db = SessionLocal()
    try:
        order = db.query(models.Order).filter(models.Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        db.delete(order)
        db.commit()
        return {"status": "deleted"}
    finally:
        db.close()
@router.put("/orders/{order_id}")
async def update_order(order_id: int, updated: dict = Body(...)):
    db = SessionLocal()
    try:
        order = db.query(models.Order).filter(models.Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # Update customer if provided
        if "customer" in updated:
            cust = db.query(models.Customer).filter(models.Customer.name == updated["customer"]).first()
            if not cust:
                cust = models.Customer(name=updated["customer"])
                db.add(cust)
                db.commit()
                db.refresh(cust)
            order.customer_id = cust.id

        # Update due_date if provided
        if "due_date" in updated:
            order.due_date = datetime.strptime(updated["due_date"], "%Y-%m-%d").date()

        # Update measurements if provided
        if "measurements" in updated:
            order.measurements = updated["measurements"]

        db.commit()
        db.refresh(order)

        return {
            "status": "updated",
            "id": order.id,
            "customer": order.customer.name,
            "due_date": str(order.due_date),
            "measurements": order.measurements,
            "image_url": order.image_url
        }
    finally:
        db.close()