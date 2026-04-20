import os
import json
import re
from typing import Optional
from fastapi import Body, Request
from fastapi import APIRouter, HTTPException, Form, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import joinedload
from twilio.rest import Client
from services.ai.agent import StitchFlowAgent
from services.ai.image_handler import save_image
from services.database import SessionLocal
from services import models
from datetime import datetime

router = APIRouter()
agent = StitchFlowAgent()

# Twilio credentials from environment variables
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN else None

class UserCommand(BaseModel):
    text: str


@router.post("/process-image")
async def process_image(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        result = agent.parse_image(contents, file.content_type)
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        print(f"Image processing error: {e}")
        return {
            "status": "error",
            "message": str(e),
            "data": {"measurements": {}}
        }


@router.post("/upload-style")
async def upload_style(
    request: Request,
    customer: str = Form(...),
    due_date: str = Form(...),
    text: str = Form(""),
    garment_type: str = Form("general"),
    phone: Optional[str] = Form(None),
    measurements: Optional[str] = Form(None),
    chest: Optional[str] = Form(None),
    waist: Optional[str] = Form(None),
    hips: Optional[str] = Form(None),
    shoulder: Optional[str] = Form(None),
    sleeve: Optional[str] = Form(None),
    inseam: Optional[str] = Form(None),
    neck: Optional[str] = Form(None),
    full_length: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    db = SessionLocal()
    try:
        # Get logged-in user
        user_email = request.cookies.get("user_email")
        if not user_email:
            raise HTTPException(status_code=401, detail="Please login first")
        
        user = db.query(models.User).filter(models.User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        print(f"📝 Saving order for: {customer} (User: {user.email})")
        print(f"   Garment type: {garment_type}")
        
        # Ensure customer exists
        cust = db.query(models.Customer).filter(
            models.Customer.name == customer,
            models.Customer.user_id == user.id
        ).first()
        
        if not cust:
            cust = models.Customer(name=customer, phone=phone, user_id=user.id)
            db.add(cust)
            db.commit()
            db.refresh(cust)
            print(f"✅ Created new customer: {customer}")
        elif phone:
            cust.phone = phone
            db.commit()
            print(f"✅ Updated customer: {customer}")

        # Build measurements dictionary from form fields
        m_dict = {}
        if chest and chest.strip():
            m_dict["chest"] = chest
        if waist and waist.strip():
            m_dict["waist"] = waist
        if hips and hips.strip():
            m_dict["hips"] = hips
        if shoulder and shoulder.strip():
            m_dict["shoulder"] = shoulder
        if sleeve and sleeve.strip():
            m_dict["sleeve"] = sleeve
        if inseam and inseam.strip():
            m_dict["inseam"] = inseam
        if neck and neck.strip():
            m_dict["neck"] = neck
        if full_length and full_length.strip():
            m_dict["full_length"] = full_length
        
        # If no individual measurements, try to parse from measurements JSON or text
        if not m_dict:
            if measurements and measurements.strip().startswith('{'):
                try:
                    m_dict = json.loads(measurements)
                except:
                    m_dict = {}
            elif text and text.strip():
                for line in text.split('\n'):
                    match = re.search(r'(\w+):\s*(\d+(?:\.\d+)?)', line)
                    if match:
                        m_dict[match.group(1).lower()] = match.group(2)
        
        print(f"📏 Measurements: {m_dict}")

        # Convert due_date string to Python date object
        due_date_obj = datetime.strptime(due_date, "%Y-%m-%d").date()

        # Handle optional image
        image_url = None
        if file and file.filename:
            image_path = save_image(file)
            image_url = f"/uploads/{os.path.basename(image_path)}"
            print(f"🖼️ Image saved: {image_url}")

        # Calculate yardage
        yardage = agent.calculate_yardage(m_dict, garment_type)
        print(f"🧵 Calculated yardage: {yardage}")

        # Save order with user_id
        order = models.Order(
            customer_id=cust.id,
            due_date=due_date_obj,
            measurements=json.dumps(m_dict),
            image_url=image_url,
            garment_type=garment_type,
            user_id=user.id
        )
        db.add(order)
        db.commit()
        db.refresh(order)
        
        print(f"✅ Order #{order.id} saved successfully!")

        return {
            "status": "success",
            "message": "Order saved successfully",
            "order_id": order.id,
            "customer": cust.name,
            "phone": cust.phone,
            "due_date": str(order.due_date),
            "measurements": order.measurements,
            "yardage": yardage,
            "image_url": order.image_url,
            "garment_type": garment_type
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error saving style: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error saving style: {str(e)}")
    finally:
        db.close()


@router.post("/process")
async def process_command(command: UserCommand):
    try:
        result = agent.parse_command(command.text)
        return {
            "status": "success",
            "ai_response": f"Extracted data for {result.get('customer', 'customer')}",
            "data": result
        }
    except Exception as e:
        print(f"Extraction Route Error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


@router.get("/orders")
async def list_orders(request: Request):
    db = SessionLocal()
    try:
        # Get logged-in user
        user_email = request.cookies.get("user_email")
        if not user_email:
            return []
        
        user = db.query(models.User).filter(models.User.email == user_email).first()
        if not user:
            return []
        
        # Get orders only for this user
        orders = db.query(models.Order).options(
            joinedload(models.Order.customer)
        ).filter(models.Order.user_id == user.id).all()
        
        result_list = []
        for order in orders:
            m_dict = {}
            if isinstance(order.measurements, str) and order.measurements.strip().startswith('{'):
                try:
                    m_dict = json.loads(order.measurements)
                except:
                    m_dict = {}
            
            garment_type = getattr(order, 'garment_type', 'general')
            yardage = agent.calculate_yardage(m_dict, garment_type)
            
            result_list.append({
                "id": order.id,
                "customer": order.customer.name if order.customer else "Unknown Customer",
                "customer_phone": order.customer.phone if order.customer else "N/A",
                "due_date": str(order.due_date),
                "measurements": order.measurements or "No measurements recorded",
                "yardage": yardage,
                "image_url": order.image_url,
                "garment_type": garment_type
            })
        return result_list
    except Exception as e:
        print(f"Error fetching orders: {e}")
        return []
    finally:
        db.close()


@router.delete("/orders/{order_id}")
async def delete_order(order_id: int, request: Request):
    db = SessionLocal()
    try:
        # Get logged-in user
        user_email = request.cookies.get("user_email")
        if not user_email:
            raise HTTPException(status_code=401, detail="Please login first")
        
        user = db.query(models.User).filter(models.User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        # Verify order belongs to this user
        order = db.query(models.Order).filter(
            models.Order.id == order_id,
            models.Order.user_id == user.id
        ).first()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        db.delete(order)
        db.commit()
        return {"status": "deleted", "message": f"Order {order_id} deleted"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting order: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting order: {str(e)}")
    finally:
        db.close()


@router.post("/send-sms/{order_id}")
async def send_sms(order_id: int, request: Request):
    db = SessionLocal()
    try:
        # Get logged-in user
        user_email = request.cookies.get("user_email")
        if not user_email:
            return {"status": "error", "message": "Please login first"}
        
        user = db.query(models.User).filter(models.User.email == user_email).first()
        if not user:
            return {"status": "error", "message": "User not found"}
        
        # Verify order belongs to this user
        order = db.query(models.Order).options(
            joinedload(models.Order.customer)
        ).filter(
            models.Order.id == order_id,
            models.Order.user_id == user.id
        ).first()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        customer_phone = order.customer.phone if order.customer else None
        
        # Get order number from position
        all_user_orders = db.query(models.Order).filter(
            models.Order.user_id == user.id
        ).order_by(models.Order.id).all()
        order_number = next((i + 1 for i, o in enumerate(all_user_orders) if o.id == order_id), order_id)
        
        if not customer_phone or customer_phone == "Not provided" or customer_phone == "":
            return {
                "status": "success", 
                "message": f"✅ Demo: SMS would be sent to {order.customer.name} for Order #{order_number}",
                "demo": True
            }

        if twilio_client:
            try:
                message_body = f"StitchFlow: Hello {order.customer.name}, your order #{order_number} ({order.garment_type or 'Outfit'}) is ready! Due: {order.due_date}"
                # Keep message under 160 chars for trial
                if len(message_body) > 160:
                    message_body = message_body[:157] + "..."
                
                message = twilio_client.messages.create(
                    to=customer_phone,
                    from_=TWILIO_PHONE_NUMBER,
                    body=message_body
                )
                return {"status": "success", "message": f"✅ SMS sent to {customer_phone}"}
            except Exception as e:
                print(f"Twilio error: {e}")
                return {"status": "warning", "message": f"⚠️ SMS failed: {str(e)}"}
        else:
            return {
                "status": "success", 
                "message": f"✅ Demo: SMS would be sent to {customer_phone} for Order #{order_number}",
                "demo": True
            }
    except HTTPException:
        raise
    except Exception as e:
        print(f"SMS error: {e}")
        return {"status": "error", "message": f"Failed to send SMS: {str(e)}"}
    finally:
        db.close()


@router.put("/orders/{order_id}")
async def update_order(order_id: int, updated: dict = Body(...), request: Request = None):
    db = SessionLocal()
    try:
        # Get logged-in user
        user_email = request.cookies.get("user_email") if request else None
        if not user_email:
            raise HTTPException(status_code=401, detail="Please login first")
        
        user = db.query(models.User).filter(models.User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        # Verify order belongs to this user
        order = db.query(models.Order).filter(
            models.Order.id == order_id,
            models.Order.user_id == user.id
        ).first()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        if "customer" in updated:
            cust = db.query(models.Customer).filter(
                models.Customer.name == updated["customer"],
                models.Customer.user_id == user.id
            ).first()
            if not cust:
                cust = models.Customer(name=updated["customer"], user_id=user.id)
                db.add(cust)
                db.commit()
                db.refresh(cust)
            order.customer_id = cust.id

        if "due_date" in updated:
            order.due_date = datetime.strptime(updated["due_date"], "%Y-%m-%d").date()

        if "measurements" in updated:
            order.measurements = updated["measurements"]
            
        if "garment_type" in updated:
            order.garment_type = updated["garment_type"]

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
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating order: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating order: {str(e)}")
    finally:
        db.close()