from services.database import SessionLocal, engine
from services import models
from sqlalchemy import text

def reset_order_ids():
    db = SessionLocal()
    try:
        # Get all orders ordered by ID
        orders = db.query(models.Order).order_by(models.Order.id).all()
        
        if not orders:
            print("No orders to reorder")
            return
        
        print(f"Found {len(orders)} orders")
        
        # Update IDs sequentially
        for new_id, order in enumerate(orders, start=1):
            print(f"Order {order.id} → {new_id}")
            # This requires SQLite to allow ID update
            db.execute(text(f"UPDATE orders SET id = {new_id} WHERE id = {order.id}"))
        
        # Reset the auto-increment counter
        db.execute(text("DELETE FROM sqlite_sequence WHERE name='orders'"))
        db.execute(text(f"INSERT INTO sqlite_sequence (name, seq) VALUES ('orders', {len(orders)})"))
        
        db.commit()
        print("✅ Order IDs reset successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_order_ids()